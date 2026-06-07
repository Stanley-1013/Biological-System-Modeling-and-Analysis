# Expertise Brief — Part 2: HIV Vaccination on the sIC AIDS Compartment Model

**For:** BME5113 (NTU) Biological System Modeling and Analysis — Term Project Part 2
**Scope:** Knowledge foundation for implementing the simulation and writing the report.
**Project task:** Haefner Ch. 15 Exercise 5 — add HIV vaccination (compartments `P_{f,2}`, `P_{m,2}`; vaccinate `S_{f,2}`, `S_{m,2}` at rate `ν = 0.65/yr`; waning at `l = 0.1/yr`), plus a project-added "optimum vaccination rate" sub-question.

> **Academic-rigor conventions used here.** Claims are tagged by source strength:
> - **[Haefner Ch.15]** — extracted from the textbook (see `textbook_notes/ch15_diseases.md`).
> - **[Garnett & Anderson 1993]** — IC-model root paper; only the *abstract* was readable (paywalled), so model *structure* is confirmed but *equations/numbers* are inferred. See `references/ref4_garnett_anderson_1993.md`.
> - **[Stover/Garnett 2002]** — World Bank PRWP 2811, open-access, read in full; direct basis of the vaccination approach. See `references/ref5_garnett_2002_worldbank.md`.
> - **[Lit]** — general epidemic-modeling literature (web sources, listed at end).
> - **[Synthesis]** — my own reasoning connecting the above; not a quoted result.
> No equations or numbers have been fabricated. Where a quantity is genuinely unknown it is stated as such.

---

## 1. Epidemic Modeling Foundations

### 1.1 The SIR threshold and R0
The Kermack–McKendrick **SIR** model partitions a fixed population `N = S + I + R` into Susceptible, Infected, Removed and (in mass-action form) reads `dS/dt = −αSI`, `dI/dt = αSI − βI`, `dR/dt = βI` **[Haefner Ch.15, Eqs. 15.2–15.4]**. The infected class grows (`dI/dt > 0`) only while `S > β/α`; this **threshold susceptible density `S_T = β/α`** is the algebraic root of the epidemic threshold **[Haefner Ch.15]**. Equivalently, defining the **basic reproduction number `R0`** = expected secondary infections from one infectious individual in a fully susceptible population, an epidemic can invade iff `R0 > 1` **[Lit]**.

The single most useful consequence for Part 2:

> **Critical vaccination / herd-immunity threshold:** `p_c = 1 − 1/R0`. If a fraction ≥ `p_c` of the population is effectively immune, the effective reproduction number drops below 1 and the disease cannot sustain itself **[Lit: ScienceDirect "Herd Immunity"; MetricGate; arXiv 1410.4469]**. With an **imperfect vaccine** the coverage needed rises to `v_c = (1 − 1/R0) / VE`, where `VE` is vaccine efficacy **[Lit: PMC7880839]**. Notably, the *critical coverage* `1 − 1/R0` is the **same** for leaky, all-or-nothing, and waning vaccines; what differs below threshold is the *endemic level*, which is higher for leaky vaccines **[Lit: arXiv 1410.4469]**.

### 1.2 Force of infection (λ)
The **force of infection** `λ` is the per-capita hazard (rate) at which a susceptible becomes infected. In mass-action SIR it is `λ = αI`; in general `λ = (contact rate) × (per-contact transmission probability) × (probability a contact is infectious)` **[Lit; Haefner Ch.15]**. New infections per unit time = `λ · S`.

### 1.3 Frequency-dependent (STD-specific) transmission — why the term is `I/(S+I)`
For airborne diseases, contact rate scales with population density (**density-dependent**, term `βSI`). For STDs, people actively *seek* a fixed number of partners regardless of how large the population is, so transmission is **frequency-dependent**: the relevant quantity is the *proportion* of infectious individuals, not their absolute density, giving a term `βSI/N` **[Lit: parasiteecology.wordpress.com; PMC1257709]**.

The sIC force of infection implements exactly this. For a susceptible female (Eq. 15.6):
`λ_{S_{f,2}} = c · ρ · β_{m,f} · I_{m,2}/(S_{m,2}+I_{m,2})` **[Haefner Ch.15]**. The factor `I_{m,2}/(S_{m,2}+I_{m,2})` is the **frequency** of infectious individuals among potential (age-2) male partners — the STD-specific `I/(S+I)` form. A key modeling consequence: **AIDS-stage individuals (`A`) are excluded from the denominator** because they are assumed not sexually active **[Haefner Ch.15]**; the partner pool is `S + I` only.

### 1.4 Why HIV/AIDS does not "burn out" like flu
A closed SIR epidemic burns out because the susceptible pool is finite and recovereds become immune (`R`); once `S` falls below `β/α` the epidemic ends — e.g. the boarding-school flu terminates after ~14 days **[Haefner Ch.15 Fig. 15.2]**. HIV/AIDS differs on two structural counts **[Synthesis grounded in Lit + Haefner]**:
1. **No recovery/immunity.** HIV has no `R` compartment — infection is for life and ends in AIDS and death. Structurally it is an **S–I–(death)** disease, not S–I–R **[Lit: IDM "SIR and SIRS"; Haefner Ch.15]**.
2. **Continuous demographic recruitment of susceptibles.** Births (here, high developing-country fertility `θ = 0.2088/yr`) continuously refill the susceptible pool, so the threshold can be exceeded indefinitely and the disease settles to an **endemic equilibrium** rather than burning out **[Lit: arXiv 2510.21371; Haefner Ch.15]**. The textbook confirms the baseline sIC run shows the population *growing* while **HIV/AIDS persists and does not go away** (Fig. 15.5a) **[Haefner Ch.15]**.

This is the central qualitative fact for Part 2: the relevant question is not "will the epidemic end" but "where does prevalence equilibrate, and can vaccination push that equilibrium (or `R0`) down."

---

## 2. The sIC Model In Depth

### 2.1 The 12 compartments
States = {S, I, A} × {female, male} × {age-1, age-2} **[Haefner Ch.15, Fig. 15.4]**:
- **S** = susceptible (uninfected); **I** = HIV-infected but pre-AIDS (infectious); **A** = clinical AIDS (assumed non-infectious / non-active).
- **Age 1** = birth to 15 (pre-sexual); **Age 2** = 16 to death (sexually active). Only age-2 participate in transmission.
- 12 state variables: `S_{f,1} S_{f,2} S_{m,1} S_{m,2}`, `I_{f,1} I_{f,2} I_{m,1} I_{m,2}`, `A_{f,1} A_{f,2} A_{m,1} A_{m,2}`.

Simplifications relative to the full IC model **[Haefner Ch.15]**: 2 sexes with identical behavior, a single AIDS stage, one sexual-activity class (so the mixing probability collapses to `ρ = 1.0`), 2 age classes.

### 2.2 Table 15.2 parameters (meaning of each)
> Values are **[Haefner Ch.15, Table 15.2]**, "attributed to / adapted from Garnett & Anderson 1993." Per `ref4`, the *specific numbers* could **not** be independently verified against the paywalled paper, so cite them as Haefner's, not as quoted from Garnett & Anderson.

| Symbol | Meaning | Value | Notes |
|---|---|---|---|
| `α` | AIDS-stage extra death rate | 1.0 /yr | on top of `μ`; mean ~1 yr in AIDS |
| `β_{f,m}` | per-partnership female→male transmission prob | 0.075 | **lower** direction |
| `β_{m,f}` | per-partnership male→female transmission prob | 0.2 | **higher** direction (asymmetry) |
| `c` (`c_{S,2}`) | new-partner acquisition rate at t=0 | 2.35 /yr | drives λ; can be time-varying `c(t)` |
| `η` | proportion of newborns that are female | 0.5 | |
| `γ` | progression rate I→A | 1.16 /yr | mean pre-AIDS infectious period ~1/γ |
| `μ` | natural (non-AIDS) death rate | 0.0227 /yr | ≈ 1/44 yr life expectancy |
| `ρ` | social mixing probability | 1.0 | single class → 1 |
| `θ` | female fecundity (birth rate) | 0.2088 /yr | high-fertility regime |
| `ϑ` (vartheta) | perinatal (mother→child) transmission prob | 0.35 | |
| `ξ` (xi) | rate age-1 → age-2 | 0.0667 /yr | maturation/ageing |
| `ζ` (zeta) | proportion in the sexual-activity class | 1.0 | |

### 2.3 Force of infection and the partner-change rate c
Females (Eq. 15.6) and males (Eq. 15.8) **[Haefner Ch.15]**:
```
λ_{S_{f,2}} = c · ρ · β_{m,f} · I_{m,2}/(S_{m,2}+I_{m,2})      (15.6)
λ_{S_{m,2}} = c · ρ · β_{f,m} · I_{f,2}/(S_{f,2}+I_{f,2})      (15.8)
```
- `c` = rate of acquiring new partners (the STD analogue of the SIR contact rate). Raising `c` from 1→2→3 /yr "dramatically increases HIV spread" (Fig. 15.6) — monogamy strongly suppresses an STD **[Haefner Ch.15]**.
- **Transmission asymmetry** `β_{m,f} = 0.2` vs `β_{f,m} = 0.075`: male→female transmission is ~2.7× more likely than female→male, a well-established biological feature of heterosexual HIV **[Haefner Ch.15; ref4 notes the asymmetry as a standard IC feature]**. Effect: women reach higher equilibrium prevalence than men in the baseline run **[Haefner Ch.15]**.

### 2.4 The other mechanisms
- **Reproduction & perinatal transmission.** Births come *only* from age-2 females (males do not limit reproduction). Susceptible mothers (`S_{f,2}`) bear susceptible newborns. Infected mothers (`I_{f,2}`) bear an *infected* newborn with probability `ϑ = 0.35` and a *susceptible* newborn with probability `(1−ϑ)`. Newborn sex split is `η : (1−η)` **[Haefner Ch.15]**. So infected births feed `I_{·,1}` and non-infecting births from infected mothers feed `S_{·,1}`.
- **Ageing `ξ`.** Age-1 individuals mature into age-2 at rate `ξ` (S→S, I→I, A→A within sex).
- **AIDS progression `γ`** moves `I → A`; **AIDS mortality `α`** is the *extra* death rate in `A` on top of natural mortality `μ`.
- **Demographics.** Natural death `μ` applies to all compartments; AIDS death `α` adds to it in `A`.

### 2.5 The ageing-term conservation flag (CRITICAL — must address in the report)
The textbook prints the AIDS age-2 equations (15.5f, 15.7f) with an ageing inflow of `ξ·I_{f,1}` (and `ξ·I_{m,1}`):
```
dA_{f,2}/dt = γ I_{f,2} + ξ I_{f,1} − (μ+α) A_{f,2}      (15.5f, as printed) ⚠
```
This **violates conservation of individuals** **[Haefner Ch.15 transcription note; Synthesis]**:
- In Eq. 15.5e, `A_{f,1}` *loses* `ξ A_{f,1}` to ageing — that flux must land somewhere, namely in `A_{f,2}`.
- Meanwhile `I_{f,1}`'s ageing flux `ξ I_{f,1}` is **already** accounted for as an inflow to `I_{f,2}` in Eq. 15.5d. Counting it *again* in `A_{f,2}` double-counts the `I_{f,1}` cohort and loses the `A_{f,1}` cohort.

**Recommendation:** use the **conservative form** with `ξ·A_{f,1}` / `ξ·A_{m,1}`:
```
dA_{f,2}/dt = γ I_{f,2} + ξ A_{f,1} − (μ+α) A_{f,2}      (conservative) ✔
dA_{m,2}/dt = γ I_{m,2} + ξ A_{m,1} − (μ+α) A_{m,2}      (conservative) ✔
```
Document the discrepancy in the report, justify the fix on conservation grounds, and (as a sanity check) verify the total-population balance numerically with the corrected term. This is a clean, defensible point to raise for academic credit.

---

## 3. Vaccination Modeling Approach (Garnett / Stover 2002 → sIC extension)

### 3.1 Vaccine property types (from the IC model)
The IC model classifies vaccine action three ways **[Stover/Garnett 2002, full text]**:
1. **Type of protection — "take" vs "degree":**
   - **Take (all-or-nothing):** completely (sterilizingly) protects a fraction of vaccinees; the rest get nothing. 50% efficacy ⇒ 50% of vaccinees fully immune.
   - **Degree (leaky):** *every* vaccinee gets a *reduced* per-exposure infection probability. 50% efficacy ⇒ everyone's `λ` is cut by 50%.
   - The paper's "standard" vaccine is **degree** type.
2. **Efficacy:** 50%, 75%, 95% scenarios.
3. **Duration / waning:** protection decays by a **mean exponential decay process** with mean 5 or 10 yr, or lifetime. **Mean 10 yr ⇒ waning rate 1/10 = 0.1/yr = the project's `l`** **[Stover/Garnett 2002]**.

### 3.2 Coverage vs rate (important nuance)
In the paper, "65% coverage" is a **coverage level reached 5 years after program start** (and footnote: "applies only to susceptible adults") **[Stover/Garnett 2002]**. The project instead uses **`ν = 0.65/yr` as a constant per-capita vaccination rate** applied to susceptible age-2 individuals. These are **not identical** — a constant rate `ν` produces an exponential approach to a protected steady state, not a fixed 65% level. The mapping `ν = 0.65/yr ↔ "65% coverage"` and `l = 0.1/yr ↔ "10-yr mean protection"` is the **deliberate simplification the project intends** **[Stover/Garnett 2002 mapping in ref5; Haefner Ch.15 Ex.5]**; state this simplification explicitly in the report.

### 3.3 How the sIC extension maps onto the IC structure
The IC model has 4 immunization categories (fully immunized / partially immunized / not immunized / previously-vaccinated-unprotected) **[Stover/Garnett 2002]**. The project collapses these to a **single Protected compartment `P` per sex at age-2**, vaccinating only age-2 susceptibles (mirroring the paper's interest in vaccinating new entrants/teenagers) and sending waned protection **straight back to `S`** (the project omits the IC model's intermediate 2-year re-vaccination-delay state) **[ref5 mapping]**.

**Is this take or degree?** As specified — vaccinees move into a `P` state and waning returns them to `S` — the natural reading is **all-or-nothing / "take" with waning**: while in `P` the individual is treated as *fully protected* (zero force of infection), and a fraction loses protection at rate `l` **[Synthesis; consistent with Stover/Garnett 2002 "fully immunized" + waning]**. This is the recommended default because it is the cleanest mapping to the requested compartment flow (`S→P→S`). If a **degree/leaky** variant is desired instead, keep `P` exposed but multiply its force of infection by `(1−VE)` and *do not* route new `P` infections — note that with full protection `P` simply has no λ term at all. **State the chosen interpretation explicitly.**

### 3.4 The exact extended ODE system
Below is the full corrected sIC + vaccination system. **P compartments are age-2 only** (terminal age class → no ageing out). The two modified susceptible equations add a `−ν` loss and an `+l·P` waning return; everything else is the conservative baseline. **`A` excluded from λ denominators.**

```
# ---------- PARAMETERS (Table 15.2) ----------
# η=0.5  θ=0.2088  ζ=1.0  ϑ=0.35  μ=0.0227  ξ=0.0667
# γ=1.16  α=1.0  ρ=1.0  c=2.35  β_mf=0.2  β_fm=0.075
# VACCINE: ν (sweep; baseline 0.65 /yr)   l (=0.1 /yr)

# ---------- FORCE OF INFECTION (frequency-dependent, A excluded) ----------
λ_f = c · ρ · β_mf · I_m2 / (S_m2 + I_m2)        # hazard for susceptible females
λ_m = c · ρ · β_fm · I_f2 / (S_f2 + I_f2)        # hazard for susceptible males

# ---------- FEMALES ----------
dS_f1/dt = η·θ·ζ·( S_f2 + (1−ϑ)·I_f2 ) − μ·S_f1 − ξ·S_f1
dS_f2/dt = ξ·S_f1 − (λ_f + μ + ν)·S_f2 + l·P_f2                 # ← vaccination loss −ν·S_f2, waning gain +l·P_f2
dI_f1/dt = η·θ·ζ·ϑ·I_f2 − (μ + ξ)·I_f1 − γ·I_f1
dI_f2/dt = λ_f·S_f2 − (μ + γ)·I_f2 + ξ·I_f1
dA_f1/dt = γ·I_f1 − (μ + ξ + α)·A_f1
dA_f2/dt = γ·I_f2 + ξ·A_f1 − (μ + α)·A_f2                       # ← conservative: ξ·A_f1 (NOT ξ·I_f1)
dP_f2/dt = ν·S_f2 − (l + μ)·P_f2                                # ← NEW protected compartment

# ---------- MALES ----------
dS_m1/dt = (1−η)·θ·ζ·( S_f2 + (1−ϑ)·I_f2 ) − (μ + ξ)·S_m1
dS_m2/dt = ξ·S_m1 − (λ_m + μ + ν)·S_m2 + l·P_m2                 # ← vaccination loss −ν·S_m2, waning gain +l·P_m2
dI_m1/dt = (1−η)·θ·ζ·ϑ·I_f2 − (μ + ξ)·I_m1 − γ·I_m1
dI_m2/dt = λ_m·S_m2 − (μ + γ)·I_m2 + ξ·I_m1
dA_m1/dt = γ·I_m1 − (μ + ξ + α)·A_m1
dA_m2/dt = γ·I_m2 + ξ·A_m1 − (μ + α)·A_m2                       # ← conservative: ξ·A_m1 (NOT ξ·I_m1)
dP_m2/dt = ν·S_m2 − (l + μ)·P_m2                                # ← NEW protected compartment

# baseline (no-vaccine) = set ν = 0  (then P stays 0)
```
Notes on this system **[Synthesis, grounded in Haefner Ch.15 + ref5]**:
- 14 ODEs total (12 baseline + 2 P). `P` compartments suffer natural mortality `μ` but no AIDS death and no ageing (already terminal age class).
- **Protected-state steady fraction (take interpretation):** ignoring demographics, `P/(S+P) → ν/(ν+l)`. With `ν=0.65, l=0.1` ⇒ ≈ `0.65/0.75 ≈ 0.87` of age-2 susceptibles protected at any instant — a useful analytic sanity check **[Synthesis]**.
- If implementing **degree/leaky** instead, replace the `P` having no λ with a `dP_f2/dt` that includes `−(1−VE)·λ_f·P_f2` and add `+(1−VE)·λ_f·P_f2` into `dI_f2/dt`. Default recommendation is the take/full-protection form above.

---

## 4. Analysis Methods for the Four Part-2 Questions

### (a) Will vaccination cause the epidemic to PEAK, and when does decline occur?
- **Outcome to track:** prevalence (proportion infected) and/or **incidence** (new infections per year = `λ_f·S_f2 + λ_m·S_m2`). The textbook's auxiliary variable of interest is the **proportion of the population that has the virus** **[Haefner Ch.15]**.
- **Detecting a peak:** record the prevalence (or incidence) time series; a peak is the time `t*` where the time-derivative changes sign from + to − (numerically: first index where `prev[k] > prev[k−1]` and `prev[k] > prev[k+1]`, or where finite-difference slope crosses zero). Report `t*` and the peak value, then the subsequent declining trajectory.
- **Interpretation framing [Synthesis + Lit]:** A peak followed by decline means vaccination has pushed the **effective** reproduction number `R_eff` below 1 (at least transiently). At a true endemic equilibrium `R_eff = 1`. So "does it peak then decline" is operationally "does vaccination move the system from an increasing-prevalence regime to a decreasing one." Be careful to distinguish a *transient* peak (epidemiological overshoot during the demographic transient) from a genuine downward shift in the endemic level — run long enough (decades) to see the true equilibrium, and compare against the ν=0 baseline (which persists, Fig. 15.5a).

### (b) Total COST
**Cumulative vaccinations to horizon `T`** = the integral of the vaccination flux **[Haefner Ch.15 Ex.5; design note]**:
```
TotalVaccinations(T) = ∫₀ᵀ ν·( S_f2(t) + S_m2(t) ) dt
TotalCost(T)         = $10 × TotalVaccinations(T)
```
**Implementation:** add a 15th accumulator ODE `dV/dt = ν·(S_f2 + S_m2)` integrated alongside the state (cleanest — no post-hoc quadrature error), then `cost = 10·V(T)`. Alternatively, trapezoidal-integrate the saved `ν·(S_f2+S_m2)` series. Note this counts **vaccination *events*** (including re-vaccination of waned individuals who returned to `S` and get re-vaccinated), which is the right cost basis since each jab costs $10 **[Synthesis]**.

### (c) OPTIMUM vaccination rate (project-added question)
This is the open-ended, higher-credit question. Recommended framing **[Synthesis grounded in Lit + ref5]**:
1. **Sweep `ν`** over a range (e.g. 0 to ~2 /yr) holding `l = 0.1/yr` fixed; for each `ν` run to a long horizon and record: peak prevalence, equilibrium/end-of-horizon prevalence, incidence reduction vs baseline, infections averted, and total cost.
2. **Connect to theory.** With an imperfect+waning vaccine, the relevant control target is to drive `R_eff < 1`. There is a **critical vaccination rate `ν_c`** analogous to the critical coverage `p_c = 1 − 1/R0`: below `ν_c` the disease stays endemic (only at a lower level — characteristic of leaky/waning vaccines), at/above `ν_c` prevalence declines toward elimination **[Lit: arXiv 1410.4469; ScienceDirect Herd Immunity]**. The protected fraction at steady state is `ν/(ν+l)`, so the vaccine can *only* protect a fraction `< 1` for any finite `ν`; if the maximum achievable protected fraction `ν/(ν+l)` (times efficacy, if degree) cannot reach `p_c`, **elimination is impossible at any rate** — an important, citable insight to test numerically by estimating `R0`/`p_c` for the baseline parameters.
3. **Define "optimum" explicitly — there are two defensible definitions; report both:**
   - **Epidemiological optimum:** smallest `ν` that turns sustained growth into decline (≈ `ν_c`, drives `R_eff` below 1). Identifiable as the knee in the peak-prevalence-vs-`ν` curve.
   - **Cost-effectiveness optimum:** the `ν` minimizing **cost per infection averted** (mirrors the paper's primary metric) **[Stover/Garnett 2002]**, or maximizing infections-averted-per-dollar. Because of diminishing returns (each extra `ν` protects fewer additional people as `ν/(ν+l)` saturates), this optimum is typically *below* the elimination rate.
   State which you adopt; the cost-effectiveness framing is the most aligned with the source literature.

### (d) VACCINATION vs SAFE-SEX / CONDOMS
- **Condom scenario = halve the transmission probabilities** (Fig. 15.5b): `β_{f,m}: 0.075→0.0375`, `β_{m,f}: 0.2→0.1`. Textbook effect: equilibrium prevalence falls (females 0.9→0.7, males 0.75→0.45) and time-to-10%-prevalence stretches from ~20 to ~50 yr **[Haefner Ch.15]**. (Halving β in the *figure caption* is authoritative; the text body's "0.1 and 0.2 → 0.05 and 0.1" is a minor inconsistency — use the halving.)
- **Fair comparison [Synthesis]:** the two interventions act on different levers (condoms ↓β via `λ`; vaccine moves people to `P`), so compare on **matched outcomes** rather than matched mechanism:
  - Plot prevalence/incidence **trajectories** for: baseline, condoms-only (halved β), vaccination (`ν=0.65`), on the same axes and horizon.
  - Compare **infections averted** and **equilibrium prevalence** for each.
  - For genuine fairness, normalize by **effort/cost**: condoms have their own per-unit cost; if no condom cost is given, compare at "equal final prevalence reduction" or report each intervention's prevalence reduction and note that only vaccination has a dollar figure here. Be explicit that a perfectly matched cost comparison requires a condom-cost assumption the project does not supply.
  - **Mechanistic insight to highlight:** condoms reduce `R0` directly (β enters `R0 ∝ √(c²·β_mf·β_fm)`), so even a *partial* β reduction can be very effective and benefits the whole population permanently; vaccination only protects a saturating fraction `ν/(ν+l)` and wanes. This often makes behavior change competitive or superior per unit effect — consistent with the textbook's emphasis that monogamy/condoms strongly suppress STD spread (Figs. 15.5–15.6) **[Haefner Ch.15]**.

---

## 5. Implementation Guidance

- **Simulation horizon.** HIV is slow (mean infectious period ~1/γ ≈ 0.86 yr to AIDS here, but epidemic spread over the *population* plays out over decades). Use **decades** — at least 50–100 yr — so the endemic equilibrium and the ~20–50 yr time-to-10%-prevalence behavior in Fig. 15.5 are visible **[Haefner Ch.15]**.
- **Integrator.** The system is non-stiff and smooth; a standard adaptive RK method (e.g. SciPy `solve_ivp` with `RK45`, or `LSODA` for safety) with tight tolerances (`rtol=1e-6, atol=1e-9`) is appropriate. Guard the λ denominators against division by zero when `S_{·,2}+I_{·,2}=0` (return λ=0) **[Synthesis]**.
- **Auxiliary outputs.** Compute **prevalence** = `(ΣI + ΣA)/(Σall)` overall, and **by sex** = `(I_{f,2}+A_{f,2})/(S_{f,2}+I_{f,2}+A_{f,2}+P_{f,2})` etc., to reproduce the textbook's female-vs-male prevalence curves. Also track **incidence** `λ_f·S_f2 + λ_m·S_m2` and the **cost accumulator** `V`.
- **Initial conditions (Table 15.2).** `S_{f,1}=S_{m,1}=3000`, `S_{f,2}=S_{m,2}=1000`, all `I=0`, all `A=0` **except `A_{m,2}=5`** (the 5-AIDS-male seed). Set `P_{f,2}=P_{m,2}=0` **[Haefner Ch.15]**. (Note: seeding only `A` — which is non-infectious — means the very first transmissions actually require infectious `I`; verify the textbook's `sIC_AIDS` seeds `I` or that the seed nonetheless ignites the epidemic. If the epidemic fails to start from an `A`-only seed under the "A excluded from transmission" rule, seed a small `I_{m,2}` instead and document the choice **[Synthesis — flag to verify]**.)
- **Sanity checks (must pass before trusting results):**
  1. **Population dynamics:** with baseline params the total population should *grow* (high fertility) **[Haefner Ch.15 Fig. 15.5a]**.
  2. **Disease persistence:** at baseline (`ν=0`) HIV/AIDS must **not** die out — prevalence settles to a positive endemic level, not zero **[Haefner Ch.15]**.
  3. **Conservation:** with the **corrected** `ξ·A_{·,1}` term, verify the bookkeeping `d/dt(Σ all states) = births − deaths` holds to numerical tolerance (a strong test that the ODEs are transcribed correctly).
  4. **Condom check:** halving β must **lower** equilibrium prevalence and lengthen time-to-10% toward the Fig. 15.5b numbers **[Haefner Ch.15]**.
  5. **Vaccine monotonicity:** higher `ν` (or lower `l`) ⇒ larger prevalence/incidence reduction — consistent with the paper **[Stover/Garnett 2002]**.
  6. **Sex asymmetry:** female prevalence > male prevalence at baseline (because `β_{m,f} > β_{f,m}`) **[Haefner Ch.15]**.

---

## Sources

**Project files (read in full):**
- `Project/textbook_notes/ch15_diseases.md` — Haefner (2005), *Modeling Biological Systems*, 2nd ed., Ch. 15 (SIR Eqs. 15.2–15.4; sIC Eqs. 15.5a–f / 15.7a–f; force of infection 15.6/15.8; Table 15.2; Exercise 5; the 15.5f/15.7f ageing-conservation flag).
- `Project/references/ref4_garnett_anderson_1993.md` — Garnett & Anderson (1993), *Phil. Trans. R. Soc. Lond. B* 342:137–159, DOI 10.1098/rstb.1993.0143 (IC-model root; **abstract only**, full text paywalled).
- `Project/references/ref5_garnett_2002_worldbank.md` — Stover, Garnett, Seitz & Forsythe (2002), *The Epidemiological Impact of an HIV/AIDS Vaccine in Developing Countries*, World Bank PRWP 2811 (open access, read in full; take/degree/duration, 65% coverage, 10-yr waning, cost-per-infection-averted).

**Web literature consulted:**
- Herd immunity / critical vaccination `1 − 1/R0`: ScienceDirect "Herd Immunity" overview — https://www.sciencedirect.com/topics/mathematics/herd-immunity ; MetricGate HIT calculator — https://metricgate.com/docs/herd-immunity-threshold/
- Imperfect-vaccine critical coverage (same `1 − 1/R0` for leaky / all-or-nothing / waning; endemic level differs): Ball et al., arXiv 1410.4469 — https://arxiv.org/pdf/1410.4469 ; PMC4394665 "Epidemiological consequences of imperfect vaccines" — https://pmc.ncbi.nlm.nih.gov/articles/PMC4394665/
- Vaccine efficacy in critical coverage `v_c = (1−1/R0)/VE`: PMC7880839 — https://pmc.ncbi.nlm.nih.gov/articles/PMC7880839/
- Frequency- vs density-dependent transmission (`βSI/N` for STDs): Parasite Ecology — https://parasiteecology.wordpress.com/2013/10/17/density-dependent-vs-frequency-dependent-disease-transmission/ ; PMC1257709 "Measuring the transmission dynamics of an STD" — https://pmc.ncbi.nlm.nih.gov/articles/PMC1257709/
- Two-sex STD `R0 = √(mf)` (geometric mean): Stanford EarthSys214 R0 notes — https://web.stanford.edu/class/earthsys214/notes/R0.html ; "On the basic reproduction number R0 in sexual activity models for HIV/AIDS" — https://pubmed.ncbi.nlm.nih.gov/17924713/
- Endemic persistence with demography / S–I (no recovery) for HIV: IDM emod-hiv "SIR and SIRS models" — https://docs.idmod.org/projects/emod-hiv/en/search/model-sir.html ; arXiv 2510.21371 (SIR with demography) — https://arxiv.org/abs/2510.21371
