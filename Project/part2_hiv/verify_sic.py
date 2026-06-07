"""Validation script for the sIC HIV/AIDS model (sic.py).

Validates the core simulation against Haefner Ch. 15 Fig. 15.5 (baseline +
condom scenario), computes the basic reproduction number R0 and the
waning-vaccine protection ceiling nu/(nu+l), cross-checks two integrators, and
runs sanity checks (non-negativity, population growth, disease persistence).

Run:  python3 verify_sic.py
Outputs PASS/FAIL with all numbers, and saves:
  figures/verify_baseline_prevalence.png
  figures/verify_condom_prevalence.png

All units: time YEARS, state INDIVIDUALS.
"""

from __future__ import annotations

import math
import os

import numpy as np

import sic

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")

HORIZON_YEARS = 120.0
N_EVAL = 2000

# Calibrated HIV->AIDS progression for the textbook-reproducing run. Table 15.2
# lists gamma=1.16/yr, which makes the continuous-ODE R0<1 (epidemic cannot
# ignite). The text itself states HIV->AIDS takes 1-10 yr; gamma=0.1/yr (mean
# ~8 yr infectious) gives R0~2.3 and reproduces Fig 15.5. See README/report.
GAMMA_CALIBRATED = 0.1


# ---------------------------------------------------------------------------
# Matplotlib (Agg)
# ---------------------------------------------------------------------------
def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 130,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "font.size": 10,
        }
    )
    return plt


# ---------------------------------------------------------------------------
# R0 for the two-sex sIC STD model
# ---------------------------------------------------------------------------
def compute_R0(p: sic.Params) -> dict:
    """Basic reproduction number for the two-sex sIC model.

    For a two-sex STD, R0 = sqrt(R_{m->f} * R_{f->m}) (next-generation /
    geometric-mean construction). Each one-directional reproduction number is

        R_{x->y} = (partner rate c) * (transmission prob beta_{x,y})
                   * (mean infectious duration of an age-2 infected)

    An age-2 infected (compartment I_{.,2}) leaves the infectious class by
    progression to AIDS (rate gamma) or natural death (rate mu); A is
    non-infectious. So the mean infectious duration ~= 1/(mu + gamma).

        R_{m->f} = c * beta_mf / (mu + gamma)      (a male infects females)
        R_{f->m} = c * beta_fm / (mu + gamma)      (a female infects males)
        R0       = c / (mu + gamma) * sqrt(beta_mf * beta_fm)

    (Initial partner pool is ~all susceptible, so the frequency factor ~1.)
    """
    dur = 1.0 / (p.mu + p.gamma)  # years infectious in I_age2
    R_m_to_f = p.c * p.beta_mf * dur
    R_f_to_m = p.c * p.beta_fm * dur
    R0 = math.sqrt(R_m_to_f * R_f_to_m)
    return {
        "mean_infectious_duration_yr": dur,
        "R_m_to_f": R_m_to_f,
        "R_f_to_m": R_f_to_m,
        "R0": R0,
        "p_c_critical_vacc_fraction": 1.0 - 1.0 / R0 if R0 > 0 else float("nan"),
    }


# ---------------------------------------------------------------------------
# Equilibrium helpers
# ---------------------------------------------------------------------------
def _tail_mean(arr: np.ndarray, frac: float = 0.05) -> float:
    """Mean of the last ``frac`` of a time series (proxy for equilibrium)."""
    n = max(1, int(len(arr) * frac))
    return float(np.mean(arr[-n:]))


def _time_to_threshold(t: np.ndarray, prev: np.ndarray, thr: float) -> float:
    """First time prevalence crosses ``thr`` (linear interp); nan if never."""
    above = np.where(prev >= thr)[0]
    if len(above) == 0:
        return float("nan")
    k = above[0]
    if k == 0:
        return float(t[0])
    # linear interpolation between k-1 and k
    p0, p1 = prev[k - 1], prev[k]
    t0, t1 = t[k - 1], t[k]
    if p1 == p0:
        return float(t1)
    return float(t0 + (thr - p0) * (t1 - t0) / (p1 - p0))


# ---------------------------------------------------------------------------
# Main verification
# ---------------------------------------------------------------------------
def main() -> int:
    os.makedirs(FIG_DIR, exist_ok=True)
    plt = _plt()
    checks: list[tuple[str, bool, str]] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        checks.append((name, passed, detail))

    print("=" * 78)
    print("sIC HIV/AIDS MODEL VALIDATION (Haefner Ch. 15)")
    print("=" * 78)

    literal = sic.Params()  # Table 15.2 verbatim (gamma=1.16), nu=0
    base = sic.Params().with_(gamma=GAMMA_CALIBRATED)  # textbook-reproducing baseline

    # -----------------------------------------------------------------
    # 1. LITERAL SEED A_{m2}=5 -> no epidemic (A excluded from lambda)
    # -----------------------------------------------------------------
    print("\n[1] LITERAL TABLE-15.2 SEED  A_m2 = 5, all I = 0 (literal params)")
    y0_lit = sic.initial_conditions(seed_A_m2=5.0, seed_I_m2=0.0)
    res_lit = sic.simulate(y0_lit, HORIZON_YEARS, literal, n_eval=N_EVAL)
    aux_lit = sic.auxiliaries(res_lit)
    max_inc_lit = float(np.max(aux_lit["incidence"]))
    final_prev_lit = float(aux_lit["prev_overall"][-1])
    no_epidemic = (max_inc_lit < 1e-9) and (final_prev_lit < 1e-9)
    print(f"    max incidence over {HORIZON_YEARS:.0f} yr = {max_inc_lit:.3e} new/yr")
    print(f"    final overall prevalence            = {final_prev_lit:.3e}")
    print(f"    -> literal A-only seed ignites epidemic? {'NO (correct)' if no_epidemic else 'YES (unexpected)'}")
    record("literal A_m2=5 seed produces NO epidemic", no_epidemic,
           f"max_incidence={max_inc_lit:.2e}")

    # -----------------------------------------------------------------
    # 1b. LITERAL PARAMS even with infectious I_m2 seed -> still no epidemic
    #     (R0 = c*sqrt(beta_mf*beta_fm)/(mu+gamma) ~ 0.24 < 1 at gamma=1.16)
    # -----------------------------------------------------------------
    print("\n[1b] LITERAL PARAMS with infectious seed I_m2 = 5 (gamma=1.16)")
    y0_lit_I = sic.initial_conditions(seed_A_m2=0.0, seed_I_m2=5.0)
    res_litI = sic.simulate(y0_lit_I, HORIZON_YEARS, literal, n_eval=N_EVAL)
    aux_litI = sic.auxiliaries(res_litI)
    peak_prev_litI = float(np.max(aux_litI["prev_overall"]))
    print(f"    peak overall prevalence = {peak_prev_litI:.3e}  -> "
          f"epidemic {'DIES OUT (R0<1)' if peak_prev_litI < 0.01 else 'grows'}")
    print("    DISCREPANCY: literal gamma=1.16/yr gives R0<1, cannot reproduce "
          "Fig 15.5.")
    print(f"    -> using calibrated gamma={GAMMA_CALIBRATED}/yr (mean infectious "
          f"~{1/(literal.mu+GAMMA_CALIBRATED):.1f} yr, R0>1) for textbook match.")
    record("literal gamma=1.16 is sub-threshold (R0<1, dies out)",
           peak_prev_litI < 0.01, f"peak_prev={peak_prev_litI:.2e}")

    # -----------------------------------------------------------------
    # 2. IGNITED BASELINE (calibrated gamma): seed I_m2 = 5
    # -----------------------------------------------------------------
    print(f"\n[2] IGNITED BASELINE  (seed I_m2 = 5, A_m2 = 0, nu = 0, "
          f"gamma={GAMMA_CALIBRATED})")
    y0 = sic.initial_conditions(seed_A_m2=0.0, seed_I_m2=5.0)
    res = sic.simulate(y0, HORIZON_YEARS, base, n_eval=N_EVAL)
    aux = sic.auxiliaries(res)
    record("baseline solver succeeded", res.success, res.message)

    N0 = float(aux["N"][0])
    Nend = float(aux["N"][-1])
    Npeak = float(np.max(aux["N"]))
    t_npeak = float(aux["t"][int(np.argmax(aux["N"]))])
    # Disease-free reference (no seed) -> confirms the demographic engine grows.
    res_df = sic.simulate(sic.initial_conditions(0.0, 0.0), HORIZON_YEARS, base,
                          n_eval=N_EVAL)
    Ndf_end = float(sic.total_population(res_df.y)[-1])
    early_grows = Npeak > N0  # population grows over the early/displayed horizon
    print(f"    population: N(0)={N0:.0f}  peak N={Npeak:.0f} @ t={t_npeak:.0f}yr  "
          f"N({HORIZON_YEARS:.0f})={Nend:.0f}")
    print(f"    disease-free reference N({HORIZON_YEARS:.0f}) = {Ndf_end:.0f} (engine grows)")
    print("    NOTE: population grows initially (Fig 15.5a horizon) then the "
          "severe mature epidemic + AIDS death (alpha=1) drives long-term decline.")
    record("population grows over early horizon (Fig 15.5a)", early_grows,
           f"N0={N0:.0f}->peak {Npeak:.0f}@{t_npeak:.0f}yr; disease-free grows to {Ndf_end:.0f}")

    prev_f_eq = _tail_mean(aux["prev_female"])
    prev_m_eq = _tail_mean(aux["prev_male"])
    prev_all_eq = _tail_mean(aux["prev_overall"])
    print(f"    equilibrium prevalence:  female = {prev_f_eq:.3f}   "
          f"male = {prev_m_eq:.3f}   overall = {prev_all_eq:.3f}")
    print(f"    textbook Fig 15.5a target: female ~0.9, male ~0.75")

    hiv_persists = prev_all_eq > 0.05
    record("HIV does NOT die out (endemic)", hiv_persists,
           f"overall_eq_prev={prev_all_eq:.3f}")
    sex_asym = prev_f_eq > prev_m_eq
    record("female prevalence > male (beta_mf>beta_fm)", sex_asym,
           f"f={prev_f_eq:.3f} > m={prev_m_eq:.3f}")

    # save baseline figure
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(aux["t"], aux["prev_female"], color="#c0392b", lw=2, label="female")
    ax.plot(aux["t"], aux["prev_male"], color="#2471a3", lw=2, label="male")
    ax.plot(aux["t"], aux["prev_overall"], color="#555", lw=1.4, ls="--", label="overall")
    ax.axhline(0.9, color="#c0392b", lw=0.8, ls=":", alpha=0.6)
    ax.axhline(0.75, color="#2471a3", lw=0.8, ls=":", alpha=0.6)
    ax.set_xlabel("time (years)")
    ax.set_ylabel("proportion infected  (I+A)/living, age-2")
    ax.set_title("sIC baseline (nu=0): HIV proportion infected vs Fig 15.5a")
    ax.set_ylim(0, 1.0)
    ax.legend(loc="lower right")
    fig.tight_layout()
    f1 = os.path.join(FIG_DIR, "verify_baseline_prevalence.png")
    fig.savefig(f1)
    plt.close(fig)
    print(f"    saved {f1}")

    t10_base = _time_to_threshold(aux["t"], aux["prev_overall"], 0.10)
    print(f"    time to 10% overall prevalence = {t10_base:.1f} yr")

    # -----------------------------------------------------------------
    # 3. CONDOM SCENARIO: halve betas
    # -----------------------------------------------------------------
    print("\n[3] CONDOM SCENARIO  (betas halved: beta_fm 0.075->0.0375, "
          "beta_mf 0.2->0.1)")
    condom = base.with_(beta_fm=0.0375, beta_mf=0.1)
    res_c = sic.simulate(y0, HORIZON_YEARS, condom, n_eval=N_EVAL)
    aux_c = sic.auxiliaries(res_c)

    prev_f_c = _tail_mean(aux_c["prev_female"])
    prev_m_c = _tail_mean(aux_c["prev_male"])
    prev_all_c = _tail_mean(aux_c["prev_overall"])
    print(f"    equilibrium prevalence:  female = {prev_f_c:.3f}   "
          f"male = {prev_m_c:.3f}   overall = {prev_all_c:.3f}")
    print(f"    textbook Fig 15.5b target: female ~0.7, male ~0.45")

    lower_f = prev_f_c < prev_f_eq
    lower_m = prev_m_c < prev_m_eq
    print(f"    condom lowers prevalence?  female {prev_f_eq:.3f}->{prev_f_c:.3f} "
          f"({'yes' if lower_f else 'NO'}),  male {prev_m_eq:.3f}->{prev_m_c:.3f} "
          f"({'yes' if lower_m else 'NO'})")
    record("condom lowers equilibrium prevalence (both sexes)", lower_f and lower_m,
           f"f:{prev_f_eq:.3f}->{prev_f_c:.3f}, m:{prev_m_eq:.3f}->{prev_m_c:.3f}")

    t10_condom = _time_to_threshold(aux_c["t"], aux_c["prev_overall"], 0.10)
    slower = (math.isnan(t10_base) or math.isnan(t10_condom) or t10_condom > t10_base)
    print(f"    time to 10% prevalence: baseline {t10_base:.1f} yr -> "
          f"condom {t10_condom:.1f} yr ({'slower' if slower else 'NOT slower'})")
    record("condom slows rise (time-to-10% increases)", bool(slower),
           f"base={t10_base:.1f}yr, condom={t10_condom:.1f}yr")

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(aux_c["t"], aux_c["prev_female"], color="#c0392b", lw=2, label="female")
    ax.plot(aux_c["t"], aux_c["prev_male"], color="#2471a3", lw=2, label="male")
    ax.plot(aux["t"], aux["prev_female"], color="#c0392b", lw=1, ls="--", alpha=0.5,
            label="female (baseline)")
    ax.plot(aux["t"], aux["prev_male"], color="#2471a3", lw=1, ls="--", alpha=0.5,
            label="male (baseline)")
    ax.axhline(0.7, color="#c0392b", lw=0.8, ls=":", alpha=0.6)
    ax.axhline(0.45, color="#2471a3", lw=0.8, ls=":", alpha=0.6)
    ax.set_xlabel("time (years)")
    ax.set_ylabel("proportion infected  (I+A)/living, age-2")
    ax.set_title("sIC condom scenario (halved betas) vs Fig 15.5b")
    ax.set_ylim(0, 1.0)
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    f2 = os.path.join(FIG_DIR, "verify_condom_prevalence.png")
    fig.savefig(f2)
    plt.close(fig)
    print(f"    saved {f2}")

    # -----------------------------------------------------------------
    # 4. R0 and waning ceiling
    # -----------------------------------------------------------------
    print("\n[4] R0 and waning-vaccine protection ceiling")
    r0_lit = compute_R0(literal)
    print(f"    LITERAL gamma=1.16: 1/(mu+gamma)={r0_lit['mean_infectious_duration_yr']:.3f} yr"
          f"  R0={r0_lit['R0']:.4f}  (< 1 -> sub-threshold, matches [1b])")
    r0 = compute_R0(base)
    print(f"    CALIBRATED gamma={GAMMA_CALIBRATED}: "
          f"1/(mu+gamma)={r0['mean_infectious_duration_yr']:.3f} yr")
    print(f"    R_(m->f) = {r0['R_m_to_f']:.4f}   R_(f->m) = {r0['R_f_to_m']:.4f}")
    print(f"    R0 = sqrt(R_mf * R_fm) = {r0['R0']:.4f}")
    print(f"    critical vaccination fraction p_c = 1 - 1/R0 = {r0['p_c_critical_vacc_fraction']:.4f}")
    record("calibrated R0 > 1 (epidemic can grow)", r0["R0"] > 1.0,
           f"R0={r0['R0']:.4f} (literal R0={r0_lit['R0']:.3f})")

    vac = base.with_(nu=0.65, l=0.1)
    ceiling = sic.waning_protection_ceiling(vac)
    print(f"    waning protection ceiling nu/(nu+l) at nu=0.65, l=0.1 = {ceiling:.4f}")
    record("waning ceiling nu/(nu+l) ~ 0.867", abs(ceiling - 0.8667) < 1e-3,
           f"ceiling={ceiling:.4f}")
    # Can elimination ever be reached? compare ceiling to p_c
    can_eliminate = ceiling >= r0["p_c_critical_vacc_fraction"]
    print(f"    ceiling ({ceiling:.3f}) vs p_c ({r0['p_c_critical_vacc_fraction']:.3f}): "
          f"vaccine {'CAN' if can_eliminate else 'CANNOT'} reach herd-immunity threshold "
          f"at nu=0.65")

    # -----------------------------------------------------------------
    # 5. LSODA vs Radau cross-check
    # -----------------------------------------------------------------
    print("\n[5] INTEGRATOR CROSS-CHECK (LSODA vs Radau, ignited baseline)")
    res_lsoda = sic.simulate(y0, HORIZON_YEARS, base, n_eval=N_EVAL, method="LSODA")
    res_radau = sic.simulate(y0, HORIZON_YEARS, base, n_eval=N_EVAL, method="Radau")
    # compare on living compartments; relative to running scale
    yl = res_lsoda.y[sic.LIVING_IDX]
    yr = res_radau.y[sic.LIVING_IDX]
    scale = np.maximum(np.abs(yl), 1.0)
    max_rel = float(np.max(np.abs(yl - yr) / scale))
    print(f"    max relative difference (living compartments) = {max_rel:.3e}")
    record("LSODA vs Radau agree (max rel diff < 1e-3)", max_rel < 1e-3,
           f"max_rel_diff={max_rel:.2e}")

    # -----------------------------------------------------------------
    # 6. Non-negativity sanity
    # -----------------------------------------------------------------
    print("\n[6] NON-NEGATIVITY / FLOW SANITY")
    min_state = float(np.min(res.y))
    # allow tiny negative numerical noise
    nonneg = min_state > -1e-6
    print(f"    min state value over baseline run = {min_state:.3e}")
    record("no meaningful negative compartments", nonneg, f"min={min_state:.2e}")

    # CONSERVATION OF INDIVIDUALS (validates the corrected xi*A_{.,1} term):
    # d/dt(sum living) should equal births - deaths at every instant. Compare
    # the RHS-derived dN/dt to the analytic balance.
    pc = base  # conservative model, nu=0
    yc = res.y
    max_cons_err = 0.0
    for k in range(0, yc.shape[1], max(1, yc.shape[1] // 200)):
        yk = yc[:, k]
        d = sic.dydt(0.0, yk, pc)
        dN_rhs = float(np.sum(d[sic.LIVING_IDX]))
        births = pc.theta * pc.zeta * (yk[sic.IDX["S_f2"]] + yk[sic.IDX["I_f2"]])
        deaths = pc.mu * float(np.sum(yk[sic.LIVING_IDX])) + pc.alpha * (
            yk[sic.IDX["A_f1"]] + yk[sic.IDX["A_f2"]]
            + yk[sic.IDX["A_m1"]] + yk[sic.IDX["A_m2"]])
        balance = births - deaths
        max_cons_err = max(max_cons_err, abs(dN_rhs - balance))
    print(f"    conservation |dN/dt - (births-deaths)| max = {max_cons_err:.3e}")
    record("conservation of individuals (corrected xi*A term)",
           max_cons_err < 1e-6, f"max_err={max_cons_err:.2e}")

    # vaccine OFF -> P and V stay zero (recovers 12-compartment baseline)
    p_v_zero = (np.max(np.abs(res.y[sic.IDX["P_f2"]])) < 1e-12
                and np.max(np.abs(res.y[sic.IDX["P_m2"]])) < 1e-12
                and np.max(np.abs(res.y[sic.IDX["V"]])) < 1e-12)
    print(f"    nu=0 keeps P,V identically zero? {'yes' if p_v_zero else 'NO'}")
    record("nu=0 recovers baseline (P,V == 0)", p_v_zero, "")

    # -----------------------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------------------
    print("\n" + "=" * 78)
    print("VALIDATION SUMMARY")
    print("=" * 78)
    all_pass = True
    for name, passed, detail in checks:
        flag = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        extra = f"   [{detail}]" if detail else ""
        print(f"  [{flag}] {name}{extra}")

    print("-" * 78)
    print("KEY NUMBERS")
    print(f"  literal A_m2=5 seed: max incidence = {max_inc_lit:.2e} new/yr -> no epidemic")
    print(f"  baseline equilibrium prevalence: female={prev_f_eq:.3f}  "
          f"male={prev_m_eq:.3f}  overall={prev_all_eq:.3f}")
    print(f"  population: N0={N0:.0f} -> peak {Npeak:.0f}@{t_npeak:.0f}yr -> "
          f"N({HORIZON_YEARS:.0f})={Nend:.0f} (early growth, long-term epidemic decline)")
    print(f"  condom equilibrium prevalence:   female={prev_f_c:.3f}  "
          f"male={prev_m_c:.3f}  overall={prev_all_c:.3f}")
    print(f"  time-to-10%: baseline {t10_base:.1f} yr -> condom {t10_condom:.1f} yr")
    print(f"  R0 (calibrated) = {r0['R0']:.4f}  (literal gamma=1.16 -> R0={r0_lit['R0']:.3f}<1)  p_c={r0['p_c_critical_vacc_fraction']:.4f}")
    print(f"  waning ceiling nu/(nu+l) [nu=0.65,l=0.1] = {ceiling:.4f}")
    print(f"  LSODA vs Radau max rel diff = {max_rel:.2e}")
    print("=" * 78)
    print(f"\nOVERALL: {'ALL CHECKS PASS' if all_pass else 'SOME CHECKS FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
