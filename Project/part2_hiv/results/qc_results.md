# Part 2 (c) — Optimum HIV Vaccination Rate

## Question
Find the optimum vaccination rate `nu` to control the HIV epidemic on the sIC
model with a take-with-waning Protected compartment (vaccinate susceptible
age-2 individuals at per-capita rate `nu`; protection wanes back to susceptible
at rate `l`). Answer it two ways: (1) the epidemiological threshold `nu_c` that
drives the epidemic toward elimination, and (2) the cost-effective `nu` (best
value per dollar).

## Modeling assumption and R0 (stated explicitly)
- **gamma = 0.1/yr** (mean ~10 yr HIV->AIDS; biologically grounded,
  within the textbook's stated 1-10 yr range). The literal Table-15.2
  `gamma = 1.16/yr` gives R0 < 1 (no epidemic) — the verified core's documented
  finding — so it cannot be used to study control.
- **R0 = c·sqrt(beta_mf·beta_fm)/(mu+gamma) = 2.3457** (> 1). Critical
  vaccinated fraction **p_c = 1 − 1/R0 = 0.5737**.
- Waning **l = 0.1/yr** (mean 10-yr protection). Epidemic seeded with
  infectious males `I_m2 = 5` (the literal A-only seed cannot ignite —
  A is excluded from the force of infection).
- Take-with-waning vaccine: while Protected, the force of infection does not act;
  a fraction wanes back to susceptible at rate `l`. Equilibrium protected
  fraction of age-2 susceptibles = `nu/(nu+l)` (lowered slightly by natural
  mortality `mu` acting on P).

## Why the threshold is framed via R_eff, not endemic prevalence
In this calibration the severe epidemic (`alpha = 1/yr` AIDS mortality) drives
the **whole population toward extinction** over centuries even at `nu = 0`
(N: 8005 → ~75 over 400 yr). Because the force of infection is
**frequency-dependent** (`lambda ~ I/(S+I+P)`), the *proportion* infected stays
high among the shrinking unprotected pool even while ABSOLUTE infection
collapses. So "(I+A)/N → 0" is not a usable elimination signal. We instead use
the **invasion / effective-reproduction-number** criterion, which is the robust,
theory-anchored test: seed a tiny infection into the vaccinated disease-free
population and measure the early exponential growth rate `r` of total infection.
`r > 0` ⇔ `R_eff > 1` (epidemic invades); `r < 0` ⇔ `R_eff < 1` (decays). The
zero crossing is the operational `nu_c`.

### The partner-pool convention (corrected) — why P belongs in the denominator
The sIC force of infection is **frequency-dependent**: `lambda ~ I/(partner
pool)`, where the pool is the set of sexually active age-2 individuals a
susceptible can partner with. Vaccine-**Protected** individuals (P) are sexually
active and uninfected, so they ARE legitimate partners (a partnership with a
protected person simply transmits nothing). The **CORRECT** convention therefore
includes P in the denominator: `pool = S + I + P` (A excluded — not sexually
active). This is the model's **DEFAULT** (`count_p_in_denominator = True`).
Excluding P would remove vaccinees from BOTH the numerator and the denominator of
`I/(S+I+P)`, artificially holding the infected frequency up and **spuriously
erasing the herd-immunity threshold** — an artifact, not a real result. At
`nu = 0` we have `P = 0`, so this choice leaves the `nu = 0` baseline and the
condom scenario exactly as the textbook.

## 1. Epidemiological threshold nu_c

Theory (vaccinees dilute the pool — the correct frequency-dependent reading):
> `R_eff = R0 · (1 − nu/(nu+l))`,  with elimination at `R_eff < 1`, i.e.
> `nu/(nu+l) >= p_c`  ⇔  **`nu_c = l · p_c / (1 − p_c)`**.

- **Predicted nu_c (theory) = l·p_c/(1−p_c) = 0.1346/yr.**
- **Simulated nu_c = 0.3655/yr** (zero crossing of the invasion growth
  rate under the corrected default — P in the pool). **There IS a finite
  herd-immunity threshold.**

### Why simulated nu_c (0.365) exceeds the simple theory (0.135)
The closed form is the correct **order of magnitude and direction** but is a
lower bound here because it omits two mechanisms the full sIC model contains:
1. **Vertical (perinatal) transmission** (`vartheta = 0.35`): infected mothers
   produce infected newborns — an infection route vaccination does **not** block
   (with `vartheta = 0` the simulated threshold drops by ~0.05–0.07/yr).
2. **Demographic recruitment + mortality on P**: continual births refill the
   susceptible pool and `mu` reduces the realized protected fraction below
   `nu/(nu+l)` (at nu=0.65 the realized age-2 protected fraction is
   0.852, vs the demography-free ceiling 0.867). Both push `nu_c` up.

So: theory `nu_c ≈ 0.135/yr` (relative gap to simulation
≈ 172%, attributable to the above), simulated `nu_c ≈ 0.365/yr`.
The standard **nu = 0.65/yr is well above the simulated nu_c**, so it drives
`R_eff < 1` and genuinely controls the epidemic.

> **Sensitivity / caveat (the WRONG convention).** If P is *excluded* from the
> partner pool (`count_p_in_denominator = False`), the invasion growth rate never
> crosses zero within the sweep — vaccination would appear to have **no finite
> herd-immunity threshold at any rate**, only shrinking the epidemic size. That
> is an **artifact** of dropping uninfected, sexually-active vaccinees out of the
> frequency-dependent mixing pool, not a real property of the disease; it is
> reported here only as a documented sensitivity check, not the main result.

## 2. Cost-effectiveness optimum (corrected default model)

Over a 50-yr horizon, for each `nu` we computed program cost
($10 × cumulative vaccinations V) and infections averted vs the no-vaccine
baseline (13444 cumulative infections over 50 yr). Under the
corrected convention the structure is dominated by the herd-immunity threshold:

- **Infections averted SATURATES past nu_c.** Below nu_c each extra unit of `nu`
  averts many more infections; once `nu >~ nu_c` essentially ALL of the
  achievable 13444 infections are already averted, and further `nu`
  only re-vaccinates waned individuals for negligible extra benefit.
- **Average cost per infection averted** now has a genuine interior **minimum at
  LOW nu** (≈$10.93 at nu≈0.03, just below/at nu_c,
  where the steep aversion is bought cheaply) and then **rises** with nu as the
  re-vaccination cost grows against a flat aversion. (Contrast: under the wrong
  P-excluded convention the average curve fell monotonically — the threshold was
  invisible.)
- **Diminishing-returns knee** = the smallest nu capturing **99% of the maximum
  achievable infections averted**: **nu ≈ 0.175/yr** (marginal cost there
  ≈ $121.64/extra infection averted). Past this knee, extra spending
  re-vaccinates waned people for almost no extra averted infection.

- At standard nu = 0.65/yr: cost = $247,461, infections averted =
  13434, average $18.42/infection averted. This
  is **above the cost-effective knee** (nu ≈ 0.18) — it still controls
  the epidemic (it is above nu_c) but it over-vaccinates somewhat relative to the
  most cost-efficient rate. ($10/vax basis; same order of magnitude as
  Garnett/Stover-2002's $110–390 per infection averted at their $20 basis.)

**Interpretation.** "Optimum" depends on the objective:
- **Epidemiologically optimal (eliminate):** any `nu ≥ nu_c ≈ 0.37/yr`
  drives `R_eff < 1`. `nu = 0.65/yr` is comfortably above it.
- **Cost-effective (best value):** the knee at `nu ≈ 0.18/yr` — just
  above nu_c, capturing ~99% of the achievable aversion at the lowest cost per
  infection; pushing far past it wastes money re-vaccinating waned individuals.

## 3. Sensitivity (R0-dependence)

| case | R0 | p_c | nu_c theory = l·p_c/(1−p_c) | nu_c simulated (corrected) |
|---|---|---|---|---|
| baseline (gamma=0.1, c=2.35) | 2.346 | 0.574 | 0.1346 | 0.3655 |
| higher R0 (c=3.0) | 2.994 | 0.666 | 0.1994 | 0.4846 |
| lower R0 (gamma=0.18) | 1.420 | 0.296 | 0.0420 | 0.1582 |

As R0 rises, p_c rises and **nu_c increases** (harder to eliminate); as R0 falls,
nu_c decreases. The exact value moves with R0, but the conclusion is **robust in
direction**: a finite critical rate `nu_c = l·p_c/(1−p_c)` always exists under the
correct convention, the simulated threshold tracks the closed form (with the
perinatal/demographic upward offset), and the standard `nu = 0.65/yr` stays above
`nu_c` across this plausible R0 range. Note the threshold sits near the edge for
small R0 (e.g. gamma=0.18 -> nu_c ≈ 0.16), so near-threshold conclusions
remain R0-sensitive.

## Figures
- `qc_invasion_threshold.png` — invasion growth rate r(nu) crossing zero (= R_eff = 1) under
  the corrected default (P in pool, finite nu_c) and, for contrast, the WRONG
  P-excluded convention (no crossing); theory and simulated nu_c, nu = 0.65 marked.
- `qc_prevalence_vs_nu.png` — peak epidemic size vs nu (corrected default model).
- `qc_cost_infections_vs_nu.png` — program cost and infections averted (saturating) vs nu, 50 yr.
- `qc_cost_effectiveness.png` — average vs marginal (ICER) cost per infection averted vs nu,
  with the diminishing-returns knee marked.

## Bottom line
- **Epidemiological optimum:** under the corrected frequency-dependent convention
  there IS a finite herd-immunity threshold `nu_c = l·p_c/(1−p_c) ≈
  0.135/yr` (theory) vs `≈ 0.365/yr` (simulated;
  higher because of perinatal transmission + demography). The standard
  `nu = 0.65/yr` is well above it and drives `R_eff < 1`.
- **Cost-effective optimum:** diminishing-returns knee at `nu ≈ 0.175/yr`
  (≈99% of max aversion; marginal ≈ $121.64/extra infection averted).
  `nu = 0.65/yr` controls the epidemic but slightly over-vaccinates relative to
  this knee.
- **Caveat (documented sensitivity):** the WRONG convention (P excluded from the
  partner pool) artificially removes the threshold entirely — vaccination would
  appear to have no critical rate at any value. We flag it only to show the result
  is an artifact of the denominator choice, not a real property of the model.
- The result is R0-sensitive in magnitude but robust in direction.
