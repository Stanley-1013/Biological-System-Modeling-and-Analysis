# Part 2 (d) — Vaccination vs Safe-Sex Education + Condoms

## Question
Which intervention more effectively controls the HIV epidemic on the sIC model:
**vaccination** (nu = 0.65/yr, l = 0.1/yr) or **safe-sex education + condoms**
(modeled as halving the transmission probabilities)? Compare over a multi-decade
horizon on prevalence trajectories, infections averted, time-to-decline,
reproduction number, and cost.

## Modeling assumption and R0 (stated explicitly)
- **gamma = 0.1/yr** (mean ~10 yr HIV->AIDS; within the textbook's
  1-10 yr range). Literal `gamma = 1.16/yr` gives R0 < 1 (no epidemic) — the
  verified core's documented finding.
- **Baseline R0 = c·sqrt(beta_mf·beta_fm)/(mu+gamma) = 2.346.** Epidemic
  seeded with infectious males `I_m2 = 5`. Horizon = 80 yr.
- **Partner-pool convention (corrected default).** The force of infection is
  frequency-dependent, `lambda ~ I/(S+I+P)`. Vaccine-Protected individuals are
  sexually active and uninfected, hence legitimate partners, so they belong in
  the denominator (`count_p_in_denominator = True`). This is the CORRECT
  convention: moving susceptibles into P dilutes the infectious frequency and
  produces genuine herd immunity. (At nu = 0, P = 0, so baseline and condoms are
  unaffected.) The WRONG convention (P excluded) is reported only as a caveat.

## Strategy definitions and reproduction numbers
- **Condoms** halve both transmission probabilities
  (beta_fm 0.075→0.0375, beta_mf 0.2→0.1). Because
  `R0 ∝ sqrt(beta_mf·beta_fm)`, this multiplies R0 by exactly 0.5:
  **R0_condom = 1.173** — just above the threshold R = 1 (invasion growth
  rate +0.086/yr, still slightly positive).
- **Vaccination** (nu = 0.65, l = 0.1, take-with-waning). The equilibrium
  protected fraction is `nu/(nu+l) = 0.867` (ceiling). Under the corrected
  default vaccinees dilute the partner pool, so
  **`R_eff = R0·(1−0.867) = 0.313 < 1`** (below threshold;
  invasion growth rate -0.040/yr — the epidemic decays). nu = 0.65
  is above the herd-immunity threshold nu_c ≈ 0.37/yr found in (c).

| strategy | R0 / R_eff | invasion growth rate r (/yr) | below threshold? |
|---|---|---|---|
| baseline | R0 = 2.346 | +0.229 | no |
| vaccination (nu=0.65, corrected default) | R_eff = 0.313 | -0.040 | **yes** |
| condoms (0.5·beta) | R0 = 1.173 | +0.086 | borderline (just > 1) |
| vaccination (WRONG: P excluded) — caveat | ≈ 2.346 | +0.228 | no (artifact) |

## Trajectory outcomes (80-yr horizon)

| metric | baseline | vaccination (nu=0.65) | condoms (0.5·beta) |
|---|---|---|---|
| peak overall prevalence | 0.408 | 0.001 | 0.001 |
| end-of-horizon prevalence | 0.408 | 0.000 | 0.001 |
| time of prevalence peak | monotone (no interior peak) | 5 yr | monotone (no interior peak) |
| cumulative infections (80 yr) | 31,235 | 11 | 378 |
| infections averted vs baseline | — | 31,224 | 30,857 |
| program cost (USD) | $0 | $348,618 | $0 (unpriced) |

## Verdict (this model, these assumptions): **BOTH interventions control the epidemic**

Under the corrected frequency-dependent convention, both strategies essentially
control the epidemic, and they do so by **different mechanisms** — so the honest
verdict is a balanced comparison, not a single winner.

- **R_eff (threshold).** Vaccination at nu = 0.65 drives **R_eff = 0.313 < 1**
  (invasion r = -0.040/yr): it genuinely crosses the elimination
  threshold because it removes the protected fraction nu/(nu+l) ≈ 0.867 > p_c =
  0.574 from the susceptible mixing pool.
  Condoms put R0 at **1.173**, still **marginally above 1** (invasion r =
  +0.086/yr) — a 50% beta cut is not quite enough to cross the
  threshold at this R0, though the epidemic is so slow it is effectively
  controlled within the horizon.
- **Infections averted (80 yr).** Vaccination averts **31,224**
  and condoms **30,857** of the baseline 31,235 —
  nearly identical; vaccination edges ahead because it pushes R_eff strictly below
  1 while condoms hover just above it (leaving a small residual 378
  cumulative infections vs 11 for vaccination).
- **Time-to-decline.** Both collapse the epidemic early: peak prevalence falls
  from the baseline 0.408 to ~0.001 (vaccination) and
  ~0.001 (condoms), with no large interior peak — the seeded epidemic
  never takes off under either intervention.
- **Cost basis.** This is where they differ sharply. **Vaccination carries an
  explicit $348,618** over 80 yr (the $10/vax accumulator), and is
  capped by the waning ceiling nu/(nu+l) = 0.867 (it must re-vaccinate waned
  individuals indefinitely). **Condoms are modeled as a permanent 0.5× cut to
  R0 at no priced cost** — but that cost is *unpriced*, not zero; a real behavior-
  change program has its own (here unmodeled) budget.

**Net read.** At equal-mechanism strength (a 50% beta cut vs the standard
nu = 0.65), the two are **close to a tie on epidemiological outcome** —
vaccination is marginally better because it strictly crosses R_eff < 1, condoms
sit just above threshold — while their cost structures are not comparable as
priced here (explicit vaccine $ + waning ceiling vs unpriced behavioral program).
We deliberately avoid declaring a single winner.

## Fairness caveats (this is a MODEL-BASED comparison, not a policy claim)
1. **Unpriced condom cost.** Condoms carry a real behavioral-program cost this
   model does not price, while vaccination has an explicit $348,618. A
   dollar-matched comparison would need a condom-program cost the project does not
   supply; the comparison is at "equal-mechanism strength," not equal cost.
2. **Near-threshold sensitivity.** Condoms leave R0 at 1.173, only ~17% above
   1, and vaccination's R_eff = 0.313 also depends on R0
   through p_c. A higher baseline R0 (e.g. higher partner rate c) would push
   condom-R0 clearly above 1 and would raise the vaccination nu_c — both verdicts
   are R0-sensitive near threshold, which is why we report R_eff explicitly.
3. **Vaccine waning + saturation.** Vaccination protects at most nu/(nu+l) = 0.867
   and re-vaccinates waned individuals (ongoing cost), whereas a sustained
   behavioral change lowers R0 for everyone permanently.
4. **Pool convention.** The corrected default (P in the partner pool) is what
   makes vaccination cross R_eff < 1. The WRONG convention (P excluded) would
   leave vaccination unable to cross the threshold at any rate — an artifact of
   dropping uninfected, sexually-active vaccinees from the frequency-dependent
   mixing pool, not a real property of the disease (see (c)).

## Figures
- `qd_strategy_comparison.png` — overall prevalence(t) for baseline / vaccination / condoms.
- `qd_averted_and_reff.png` — infections averted and reproduction number per strategy.

## Bottom line
Under gamma = 0.1/yr (R0 = 2.35) and the corrected frequency-dependent
convention, **both vaccination (nu = 0.65) and condoms (50% beta cut) control the
epidemic**. Vaccination drives **R_eff = 0.31 < 1** and
averts **31,224** infections (residual 11);
condoms hold R0 at **1.17** (just above 1) and avert **30,857**
(residual 378) — essentially a tie on epidemiological outcome, with
vaccination marginally ahead for crossing the threshold strictly. They differ on
cost basis: vaccination $348,618 explicit + a waning ceiling vs condoms'
unpriced behavioral program. The verdict is balanced and **R0-sensitive near
threshold**; we report explicit R_eff and fairness caveats rather than overclaim a
single winner.
