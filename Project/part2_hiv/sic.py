"""sIC (simple Imperial College) HIV/AIDS compartment model + HIV-vaccination extension.

Implements the simplified Imperial College AIDS model from Haefner (2005),
*Modeling Biological Systems*, 2nd ed., Chapter 15 (Eqs. 15.5a-f for females,
15.7a-f for males; force of infection 15.6/15.8; Table 15.2 parameters),
extended with a Protected (P) vaccination compartment per the project's Part-2
specification (Haefner Ex. 15.6 #5, loosely after Garnett/Stover 2002).

This module is PURE PHYSICS only. It defines:
  * the parameter set (Table 15.2),
  * the 15-ODE right-hand side (12 baseline + 2 protected P + 1 cost accumulator V),
  * the frequency-dependent force of infection,
  * a ``solve_ivp`` wrapper,
  * auxiliary diagnostics (population, prevalence, incidence, cost).

Validation lives in ``verify_sic.py``.

================================================================================
UNITS
================================================================================
Time      : YEARS.
State     : numbers of INDIVIDUALS (people) per compartment.
Rates     : per year (e.g. mu = 0.0227 /yr).
Cost state: V = cumulative vaccinations (individuals); money cost = $10 * V.

================================================================================
STATE VECTOR LAYOUT (length 15, fixed documented order)
================================================================================
Index  Symbol     Meaning
  0    S_f1       susceptible female, age class 1 (0-15 yr, pre-sexual)
  1    S_f2       susceptible female, age class 2 (16+, sexually active)
  2    S_m1       susceptible male,   age class 1
  3    S_m2       susceptible male,   age class 2
  4    I_f1       HIV+ (pre-AIDS, infectious) female, age 1   [perinatal only]
  5    I_f2       HIV+ female, age 2
  6    I_m1       HIV+ male,   age 1
  7    I_m2       HIV+ male,   age 2
  8    A_f1       clinical AIDS female, age 1
  9    A_f2       clinical AIDS female, age 2
 10    A_m1       clinical AIDS male,   age 1
 11    A_m2       clinical AIDS male,   age 2
 12    P_f2       vaccine-protected female, age 2   (extension; 0 when nu=0)
 13    P_m2       vaccine-protected male,   age 2   (extension; 0 when nu=0)
 14    V          cumulative vaccinations administered (cost accumulator)

When nu = 0 (vaccination OFF, the default), P_f2, P_m2, V all stay 0 for all
time, exactly recovering the textbook's 12-compartment baseline sIC model.

================================================================================
KEY MODELING CHOICES (documented for the report)
================================================================================
1. CONSERVATIVE AGEING TERM (Haefner 15.5f / 15.7f flag).
   The textbook prints the AIDS age-2 ageing inflow as xi*I_{,1}, which
   double-counts the I_{,1} cohort (already aged into I_{,2} in 15.5d/15.7d)
   and loses the A_{,1} cohort. Conservation of individuals requires the inflow
   to be xi*A_{,1}. THIS MODULE USES xi*A_{,1} (the conservative, correct form).

2. PROTECTED COMPARTMENT = "TAKE" (all-or-nothing) vaccine WITH WANING.
   While in P an individual is treated as FULLY protected: the force of
   infection does not act on P at all (P has no lambda term and never flows to
   I). Susceptibles S_{.,2} are vaccinated into P at per-capita rate nu;
   protection wanes back to S at rate l. P suffers natural mortality mu but no
   AIDS death and no ageing (age-2 is the terminal age class). This is the
   cleanest reading of the project's requested S -> P -> S flow and maps to the
   IC model's "fully immunized + waning" category (Stover/Garnett 2002).

3. PARTNER-AVAILABILITY DENOMINATOR = S + I + P (age-2). [DEFAULT, CORRECTED]
   The sIC force of infection is FREQUENCY-dependent:
       lambda_Sf2 = c*rho*beta_mf * I_m2 / (partner pool).
   The "partner pool" is the set of sexually active age-2 individuals a
   susceptible can partner with. AIDS individuals (A) are excluded (assumed not
   sexually active, per the textbook). VACCINE-PROTECTED individuals (P),
   however, are sexually active and uninfected, so they ARE eligible partners:
   a partnership with a protected person simply yields no transmission. The
   correct frequency-dependent denominator therefore MUST include P:
       pool_m = S_m2 + I_m2 + P_m2,   pool_f = S_f2 + I_f2 + P_f2.
   Excluding P is an ARTIFACT: it removes vaccinees from BOTH the numerator and
   the denominator of I/(S+I+P), which artificially holds the infected fraction
   up and spuriously erases any herd-immunity threshold (vaccination would then
   appear to have no critical rate at all). Including P is the correct
   convention and yields genuine herd immunity (a finite nu_c). At nu=0, P=0
   identically, so the nu=0 baseline and the condom scenario are UNAFFECTED and
   still reproduce the textbook exactly. The exclusion is kept available behind
   the flag ``count_p_in_denominator=False`` for sensitivity discussion only.
   DEFAULT: P INCLUDED (count_p_in_denominator=True).

4. PROPORTION INFECTED (prevalence), consistent with Fig 15.5.
   "Proportion infected" = proportion that carries the virus, where I (HIV+
   pre-AIDS) and A (clinical AIDS) both "have the virus".
   * prevalence_overall  = (all I + all A) / (all living people).
   * prevalence_female/male = (I+A)/(living) restricted to the AGE-2
     (sexually-active) class of that sex. The textbook's Fig 15.5 sex curves
     track the sexually-active population (the epidemic lives in age-2; whole-
     population figures are diluted by the large pre-sexual age-1 cohort).
     ``prevalence_female_allages`` / ``prevalence_male_allages`` are provided
     for the diluted whole-sex definition.
   The cost accumulator V is excluded from all population totals.

5. PARAMETER / R0 CAVEAT (documented in verify_sic.py).
   With Table 15.2 taken literally as continuous per-year rates, gamma=1.16/yr
   gives a mean infectious period 1/(mu+gamma)~0.85 yr and a two-sex
   R0 = c*sqrt(beta_mf*beta_fm)/(mu+gamma) ~ 0.24 < 1, so the epidemic CANNOT
   ignite -- contradicting Fig 15.5. A biologically realistic HIV->AIDS
   progression (the text itself states 1-10 yr), e.g. gamma ~ 0.1/yr giving a
   ~8-yr infectious period and R0 ~ 2.3, reproduces Fig 15.5. The module keeps
   the literal Table 15.2 default and verify_sic.py reports BOTH the literal
   sub-threshold result and the calibrated textbook-reproducing run.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

import numpy as np
from scipy.integrate import solve_ivp

# ---------------------------------------------------------------------------
# State indexing (fixed, documented order)
# ---------------------------------------------------------------------------
IDX = {
    "S_f1": 0, "S_f2": 1, "S_m1": 2, "S_m2": 3,
    "I_f1": 4, "I_f2": 5, "I_m1": 6, "I_m2": 7,
    "A_f1": 8, "A_f2": 9, "A_m1": 10, "A_m2": 11,
    "P_f2": 12, "P_m2": 13,
    "V": 14,
}
STATE_NAMES = list(IDX.keys())
N_STATE = len(STATE_NAMES)  # 15

# Compartments that count as "living people" (V excluded).
LIVING_IDX = [IDX[k] for k in STATE_NAMES if k != "V"]

COST_PER_VACCINATION_USD = 10.0


# ---------------------------------------------------------------------------
# Parameters (Table 15.2) -- immutable dataclass
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Params:
    """sIC parameters (Haefner Table 15.2) plus vaccination extension.

    All rates are per YEAR. Defaults reproduce the textbook baseline with
    vaccination OFF (nu = 0).
    """

    # --- demographic / disease (Table 15.2) ---
    alpha: float = 1.0        # AIDS extra death rate /yr
    beta_fm: float = 0.075    # female -> male per-partnership transmission prob
    beta_mf: float = 0.2      # male -> female per-partnership transmission prob
    c: float = 2.35           # new-partner acquisition rate /yr
    eta: float = 0.5          # proportion of newborns that are female
    gamma: float = 1.16       # progression rate I -> A /yr
    mu: float = 0.0227        # natural (non-AIDS) death rate /yr
    rho: float = 1.0          # social mixing probability (single class)
    theta: float = 0.2088     # female fecundity (birth rate) /yr
    vartheta: float = 0.35    # perinatal (mother->child) transmission prob
    xi: float = 0.0667        # ageing rate age1 -> age2 /yr
    zeta: float = 1.0         # proportion in the sexual-activity class

    # --- vaccination extension (OFF by default) ---
    nu: float = 0.0           # per-capita vaccination rate of S_{.,2} -> P /yr
    l: float = 0.1            # waning rate P -> S /yr (mean 1/l yr protection)

    # --- modeling-choice flags ---
    # Include the vaccine-Protected (P) in the frequency-dependent partner-pool
    # denominator. DEFAULT = True (CORRECT convention): P individuals are
    # sexually active and uninfected, hence legitimate partners; a partnership
    # with a protected person yields no transmission. Excluding them removes
    # vaccinees from BOTH numerator and denominator of I/(S+I+P), artificially
    # holding the infected fraction up and spuriously erasing herd immunity.
    # Set to False ONLY for the documented sensitivity/caveat scenario. At nu=0
    # P=0, so this flag has NO effect on the baseline or condom scenarios.
    count_p_in_denominator: bool = True

    def with_(self, **overrides) -> "Params":
        """Return a NEW Params with the given fields overridden (immutable)."""
        return replace(self, **overrides)


# ---------------------------------------------------------------------------
# Initial conditions (Table 15.2)
# ---------------------------------------------------------------------------
def initial_conditions(
    seed_A_m2: float = 5.0,
    seed_I_m2: float = 0.0,
) -> np.ndarray:
    """Build the Table 15.2 initial state vector (length 15).

    Table 15.2 lists the literal seed as A_{m,2} = 5 (5 AIDS males age-2).
    Because AIDS individuals (A) are excluded from the force of infection, that
    literal seed CANNOT ignite the epidemic. To ignite, seed infectious males
    via ``seed_I_m2`` instead (see verify_sic.py).

    Args:
        seed_A_m2: initial AIDS males age-2 (textbook literal seed = 5).
        seed_I_m2: initial HIV+ (infectious) males age-2 (ignition seed).

    Returns:
        np.ndarray of length 15, individuals.
    """
    y = np.zeros(N_STATE, dtype=float)
    y[IDX["S_f1"]] = 3000.0
    y[IDX["S_f2"]] = 1000.0
    y[IDX["S_m1"]] = 3000.0
    y[IDX["S_m2"]] = 1000.0
    y[IDX["A_m2"]] = seed_A_m2
    y[IDX["I_m2"]] = seed_I_m2
    return y


# ---------------------------------------------------------------------------
# Force of infection (Eqs. 15.6 / 15.8), frequency-dependent
# ---------------------------------------------------------------------------
def _frequency(infectious: float, pool: float) -> float:
    """Proportion infectious among the partner pool; guarded against /0."""
    if pool <= 0.0:
        return 0.0
    return infectious / pool


def forces_of_infection(y: np.ndarray, p: Params) -> tuple[float, float]:
    """Compute (lambda_Sf2, lambda_Sm2): per-capita hazards on susceptible age-2.

    lambda_Sf2 = c * rho * beta_mf * I_m2 / (S_m2 + I_m2 [+ P_m2])   (Eq. 15.6)
    lambda_Sm2 = c * rho * beta_fm * I_f2 / (S_f2 + I_f2 [+ P_f2])   (Eq. 15.8)

    A (AIDS) is excluded from the denominator (not sexually active). P
    (vaccine-protected) IS included by DEFAULT (count_p_in_denominator=True):
    protected individuals remain sexually active and uninfected, so they are
    legitimate partners in the frequency-dependent mixing pool (a partnership
    with them simply transmits nothing). Excluding P is an artifact available
    only for sensitivity analysis. At nu=0, P=0, so the default and the
    exclusion coincide on the baseline/condom scenarios.
    Denominator-zero is guarded -> lambda = 0.
    """
    S_f2 = y[IDX["S_f2"]]
    S_m2 = y[IDX["S_m2"]]
    I_f2 = y[IDX["I_f2"]]
    I_m2 = y[IDX["I_m2"]]
    P_f2 = y[IDX["P_f2"]]
    P_m2 = y[IDX["P_m2"]]

    pool_m = S_m2 + I_m2 + (P_m2 if p.count_p_in_denominator else 0.0)
    pool_f = S_f2 + I_f2 + (P_f2 if p.count_p_in_denominator else 0.0)

    lam_f = p.c * p.rho * p.beta_mf * _frequency(I_m2, pool_m)  # hazard for S_f2
    lam_m = p.c * p.rho * p.beta_fm * _frequency(I_f2, pool_f)  # hazard for S_m2
    return lam_f, lam_m


# ---------------------------------------------------------------------------
# Right-hand side: full 15-ODE system
# ---------------------------------------------------------------------------
def dydt(t: float, y: np.ndarray, p: Params) -> np.ndarray:
    """sIC + vaccination RHS. Pure function; returns d(state)/dt (length 15).

    Uses the CONSERVATIVE ageing term xi*A_{.,1} in the AIDS age-2 equations
    (not the book's printed xi*I_{.,1}). With nu = 0 the P and V derivatives are
    identically zero, recovering the 12-compartment baseline.
    """
    # Unpack
    S_f1 = y[IDX["S_f1"]]; S_f2 = y[IDX["S_f2"]]
    S_m1 = y[IDX["S_m1"]]; S_m2 = y[IDX["S_m2"]]
    I_f1 = y[IDX["I_f1"]]; I_f2 = y[IDX["I_f2"]]
    I_m1 = y[IDX["I_m1"]]; I_m2 = y[IDX["I_m2"]]
    A_f1 = y[IDX["A_f1"]]; A_f2 = y[IDX["A_f2"]]
    A_m1 = y[IDX["A_m1"]]; A_m2 = y[IDX["A_m2"]]
    P_f2 = y[IDX["P_f2"]]; P_m2 = y[IDX["P_m2"]]

    lam_f, lam_m = forces_of_infection(y, p)

    eta, theta, zeta, vartheta = p.eta, p.theta, p.zeta, p.vartheta
    mu, xi, gamma, alpha, nu, l = p.mu, p.xi, p.gamma, p.alpha, p.nu, p.l

    # Reproduction (births come only from age-2 females; males don't limit it).
    # Non-infecting births (-> S newborns) from S_f2 and (1-vartheta) I_f2.
    # Infecting births (-> I newborns) from vartheta * I_f2.
    births_S = theta * zeta * (S_f2 + (1.0 - vartheta) * I_f2)
    births_I = theta * zeta * vartheta * I_f2

    d = np.zeros(N_STATE, dtype=float)

    # ---------------- FEMALES (15.5a-f, conservative) ----------------
    d[IDX["S_f1"]] = eta * births_S - mu * S_f1 - xi * S_f1
    d[IDX["S_f2"]] = xi * S_f1 - (lam_f + mu + nu) * S_f2 + l * P_f2
    d[IDX["I_f1"]] = eta * births_I - (mu + xi) * I_f1 - gamma * I_f1
    d[IDX["I_f2"]] = lam_f * S_f2 - (mu + gamma) * I_f2 + xi * I_f1
    d[IDX["A_f1"]] = gamma * I_f1 - (mu + xi + alpha) * A_f1
    d[IDX["A_f2"]] = gamma * I_f2 + xi * A_f1 - (mu + alpha) * A_f2  # xi*A_f1 (conservative)
    d[IDX["P_f2"]] = nu * S_f2 - (l + mu) * P_f2

    # ---------------- MALES (15.7a-f, conservative) ----------------
    d[IDX["S_m1"]] = (1.0 - eta) * births_S - (mu + xi) * S_m1
    d[IDX["S_m2"]] = xi * S_m1 - (lam_m + mu + nu) * S_m2 + l * P_m2
    d[IDX["I_m1"]] = (1.0 - eta) * births_I - (mu + xi) * I_m1 - gamma * I_m1
    d[IDX["I_m2"]] = lam_m * S_m2 - (mu + gamma) * I_m2 + xi * I_m1
    d[IDX["A_m1"]] = gamma * I_m1 - (mu + xi + alpha) * A_m1
    d[IDX["A_m2"]] = gamma * I_m2 + xi * A_m1 - (mu + alpha) * A_m2  # xi*A_m1 (conservative)
    d[IDX["P_m2"]] = nu * S_m2 - (l + mu) * P_m2

    # ---------------- COST ACCUMULATOR ----------------
    # V(t) = cumulative vaccinations = integral of nu*(S_f2 + S_m2) dt.
    d[IDX["V"]] = nu * (S_f2 + S_m2)

    return d


# ---------------------------------------------------------------------------
# Simulation wrapper
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SimResult:
    """Container for a simulation run."""

    t: np.ndarray              # (n,) years
    y: np.ndarray              # (15, n) states
    params: Params
    success: bool
    message: str

    def get(self, name: str) -> np.ndarray:
        """Return the time series of compartment ``name``."""
        return self.y[IDX[name]]


def simulate(
    y0: np.ndarray,
    t_end: float,
    p: Params = Params(),
    n_eval: int = 1000,
    method: str = "LSODA",
    rtol: float = 1e-8,
    atol: float = 1e-10,
    max_step: Optional[float] = None,
) -> SimResult:
    """Integrate the sIC(+vaccine) system from 0 to ``t_end`` years.

    Args:
        y0: initial state (length 15), individuals.
        t_end: horizon in years.
        p: immutable Params.
        n_eval: number of uniform output points.
        method: solve_ivp method ('LSODA' or 'Radau' recommended).
        rtol, atol: solver tolerances.
        max_step: optional cap on step size.

    Returns:
        SimResult.
    """
    y0 = np.asarray(y0, dtype=float)
    if y0.shape != (N_STATE,):
        raise ValueError(f"y0 must have length {N_STATE}, got {y0.shape}")
    if t_end <= 0:
        raise ValueError("t_end must be positive")

    t_eval = np.linspace(0.0, t_end, n_eval)
    kwargs = dict(
        fun=lambda t, y: dydt(t, y, p),
        t_span=(0.0, t_end),
        y0=y0,
        method=method,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
    )
    if max_step is not None:
        kwargs["max_step"] = max_step

    sol = solve_ivp(**kwargs)
    return SimResult(
        t=sol.t, y=sol.y, params=p, success=bool(sol.success), message=str(sol.message)
    )


# ---------------------------------------------------------------------------
# Auxiliary diagnostics
# ---------------------------------------------------------------------------
def _sum_idx(y: np.ndarray, names: list[str]) -> np.ndarray:
    """Sum selected compartments along the time axis (y is (15, n) or (15,))."""
    return sum(y[IDX[n]] for n in names)


def total_population(y: np.ndarray) -> np.ndarray:
    """Total living population N(t) (all compartments except V)."""
    return y[LIVING_IDX].sum(axis=0)


def total_hiv_positive(y: np.ndarray) -> np.ndarray:
    """Total HIV+ (pre-AIDS, infectious) = sum of all I compartments."""
    return _sum_idx(y, ["I_f1", "I_f2", "I_m1", "I_m2"])


def total_aids(y: np.ndarray) -> np.ndarray:
    """Total clinical AIDS = sum of all A compartments."""
    return _sum_idx(y, ["A_f1", "A_f2", "A_m1", "A_m2"])


def total_with_virus(y: np.ndarray) -> np.ndarray:
    """Total carrying the virus = I + A (all classes)."""
    return total_hiv_positive(y) + total_aids(y)


def prevalence_overall(y: np.ndarray) -> np.ndarray:
    """Overall proportion infected = (I + A) / living population.

    Consistent with Fig 15.5: 'proportion of the population that has the virus'.
    """
    N = total_population(y)
    with np.errstate(divide="ignore", invalid="ignore"):
        prev = np.where(N > 0, total_with_virus(y) / N, 0.0)
    return prev


def _sex_prevalence_age2(y: np.ndarray, sex: str) -> np.ndarray:
    """Proportion infected among the AGE-2 (sexually-active) class of one sex.

    (I_{s,2}+A_{s,2}) / (S_{s,2}+I_{s,2}+A_{s,2}+P_{s,2}). This is the textbook
    Fig 15.5 sex-curve definition (epidemic concentrated in the sexually-active
    population). P is age-2 only and counts toward the age-2 living total.
    """
    s = sex
    infected = _sum_idx(y, [f"I_{s}2", f"A_{s}2"])
    living = _sum_idx(y, [f"S_{s}2", f"I_{s}2", f"A_{s}2", f"P_{s}2"])
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(living > 0, infected / living, 0.0)


def _sex_prevalence_allages(y: np.ndarray, sex: str) -> np.ndarray:
    """Proportion infected within one sex across BOTH age classes (diluted)."""
    s = sex
    infected = _sum_idx(y, [f"I_{s}1", f"I_{s}2", f"A_{s}1", f"A_{s}2"])
    living = _sum_idx(
        y,
        [f"S_{s}1", f"S_{s}2", f"I_{s}1", f"I_{s}2",
         f"A_{s}1", f"A_{s}2", f"P_{s}2"],
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(living > 0, infected / living, 0.0)


def prevalence_female(y: np.ndarray) -> np.ndarray:
    """Fig-15.5 female prevalence: (I_f2+A_f2)/(age-2 living females)."""
    return _sex_prevalence_age2(y, "f")


def prevalence_male(y: np.ndarray) -> np.ndarray:
    """Fig-15.5 male prevalence: (I_m2+A_m2)/(age-2 living males)."""
    return _sex_prevalence_age2(y, "m")


def prevalence_female_allages(y: np.ndarray) -> np.ndarray:
    """Whole-female-population prevalence (diluted by age-1 children)."""
    return _sex_prevalence_allages(y, "f")


def prevalence_male_allages(y: np.ndarray) -> np.ndarray:
    """Whole-male-population prevalence (diluted by age-1 children)."""
    return _sex_prevalence_allages(y, "m")


def incidence(y: np.ndarray, p: Params) -> np.ndarray:
    """New infections per year = lambda_Sf2 * S_f2 + lambda_Sm2 * S_m2.

    Works for y of shape (15, n) (vectorized) or (15,).
    """
    y = np.asarray(y, dtype=float)
    if y.ndim == 1:
        lam_f, lam_m = forces_of_infection(y, p)
        return np.array(lam_f * y[IDX["S_f2"]] + lam_m * y[IDX["S_m2"]])
    # vectorized over time
    out = np.zeros(y.shape[1], dtype=float)
    for k in range(y.shape[1]):
        lam_f, lam_m = forces_of_infection(y[:, k], p)
        out[k] = lam_f * y[IDX["S_f2"], k] + lam_m * y[IDX["S_m2"], k]
    return out


def cumulative_vaccinations(y: np.ndarray) -> np.ndarray:
    """Cumulative vaccinations administered V(t) (the accumulator state)."""
    return y[IDX["V"]]


def total_cost(y: np.ndarray) -> np.ndarray:
    """Cumulative vaccination cost in USD = $10 * V(t)."""
    return COST_PER_VACCINATION_USD * cumulative_vaccinations(y)


def waning_protection_ceiling(p: Params) -> float:
    """Steady protected fraction ignoring demography = nu / (nu + l).

    Analytic sanity-check ceiling for the take-with-waning vaccine: the maximum
    fraction of age-2 susceptibles that can be in P at any instant.
    """
    denom = p.nu + p.l
    return p.nu / denom if denom > 0 else 0.0


def auxiliaries(res: SimResult) -> dict:
    """Bundle all auxiliary time series for a SimResult into a dict."""
    y = res.y
    return {
        "t": res.t,
        "N": total_population(y),
        "HIV_pos": total_hiv_positive(y),
        "AIDS": total_aids(y),
        "with_virus": total_with_virus(y),
        "prev_overall": prevalence_overall(y),
        "prev_female": prevalence_female(y),
        "prev_male": prevalence_male(y),
        "incidence": incidence(y, res.params),
        "cum_vaccinations": cumulative_vaccinations(y),
        "cost_usd": total_cost(y),
    }
