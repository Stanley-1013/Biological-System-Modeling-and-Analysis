# Q(b) — Total COST of vaccination (at $10 per vaccination) and cost-effectiveness

## The question
Using the model's cost accumulator V(t) (dV/dt = ν·(S_{f2}+S_{m2})), report the
cumulative number of vaccinations and the total cost = $10·V(T) for the ν = 0.65/yr
run at several horizons (T = 20, 30, 50 yr), and the steady annual cost once
protection saturates. Then compute cost-effectiveness: infections **averted** =
cumulative new infections (baseline) − cumulative new infections (vaccine), and the
**cost per infection averted**.

## Modeling assumptions — apply to all results
We use **γ = 0.1/yr** (mean ≈ 10 yr HIV→AIDS; mean infectious ≈ 8.1 yr), **NOT** the
literal Table 15.2 γ = 1.16/yr which gives R₀ < 1 (no epidemic). With γ = 0.1/yr,
**R₀ ≈ 2.346 > 1**. Seed = infectious males I_{m2} = 5. Vaccine: ν = 0.65/yr,
l = 0.1/yr, cost = $10 per vaccination. Infections averted are obtained by
trapezoidal integration of the incidence auxiliary λ_{Sf2}·S_{f2} + λ_{Sm2}·S_{m2}
for the baseline and vaccinated runs.

**Partner-pool convention (corrected default).** The frequency-dependent force of
infection counts the vaccine-Protected in the partner pool (λ ~ I/(S+I+P)), the
correct convention since P individuals are uninfected and sexually active. Because
ν = 0.65 is above the herd-immunity threshold ν_c ≈ 0.37 (see Q(c)), the vaccinated
epidemic is driven to R_eff ≈ 0.31 < 1 and **never ignites** — so the vaccinated
arm has almost no infections, and "infections averted" is essentially the entire
baseline epidemic. (At ν = 0, P = 0, so the baseline is unchanged.)

## Cost and cost-effectiveness by horizon
| T (yr) | Cumulative vaccinations | Total cost ($10/vax) | Infections baseline | Infections vaccine | **Infections averted** | **Cost / infection averted** |
|---|---|---|---|---|---|---|
| 20 | 11,374 | **$113,738** | 314 | 9 | 305 | **$372** |
| 30 | 16,217 | **$162,165** | 1,595 | 10 | 1,585 | **$102** |
| 50 | 24,746 | **$247,461** | 13,444 | 11 | 13,434 | **$18** |

### Annual steady cost
Once the protected fraction saturates near ν/(ν+l) ≈ 0.867, vaccinations **recur**
because protection wanes (P → S at rate l) and new susceptibles age in (S_{·,1} →
S_{·,2}). The program therefore keeps re-vaccinating at a roughly steady rate and
cumulative cost grows **~linearly**. Over the last 10 yr the slope is

- **≈ 407 vaccinations/yr → ≈ $4,070/yr** steady annual cost.

(The much larger early per-year totals reflect the initial mass vaccination of the
standing susceptible pool; the steady-state recurring cost is the small ongoing
top-up to replace waned protection and cover new entrants. Note that because the
epidemic is suppressed, the susceptible pool stays large and healthy, so the
recurring vaccination volume — and cost — is slightly higher than it would be if
the epidemic had thinned the population.)

## Interpretation
- **Total cost is modest and grows nearly linearly.** From ~$114k at 20 yr to
  ~$247k at 50 yr, with a steady recurring cost of only ~$4.1k/yr once protection
  saturates — the expense is dominated by the up-front vaccination of the existing
  susceptible population, then a small maintenance cost.
- **Cost-effectiveness improves dramatically over time.** Cost per infection averted
  falls from $372 (20 yr) → **$102 (30 yr)** → $18 (50 yr). Early on the *untreated
  baseline* epidemic has barely taken off, so there are few infections to avert and
  the ratio looks expensive; as the **baseline epidemic accelerates** (its incidence
  peaks ~791/yr around 48 yr) while the vaccinated arm stays near zero, averted
  infections grow much faster than cumulative cost, so each dollar buys far more
  prevention. This is the same qualitative result as Stover & Garnett (2002), whose
  Imperial-College / rural-Zimbabwe figure was ~$110–$390 per infection averted
  (their $20/person basis); our 30-yr value of **$102** is just below that band
  (consistent with the $10 unit cost here and the corrected convention, under which
  vaccination averts nearly the *entire* baseline epidemic rather than only part of
  it).
- **Caveat on cost basis.** Each $10 charge counts a vaccination *event*, including
  re-vaccinating people whose protection waned and who returned to S — the correct
  basis since every jab costs $10.

## Figure
- `figures/qb_cost.png` — two panels: (top) cumulative cost(t) with cumulative
  vaccinations on a twin axis, horizon markers at 20/30/50 yr; (bottom) cumulative
  infections for baseline vs vaccine and the cumulative **infections averted** band.

## Reproduce
```
python3 q_b_cost.py
```
