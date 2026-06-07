# Q(a) — Will vaccination cause the epidemic to PEAK, and when does decline occur?

## The question
Run the sIC HIV/AIDS model with the vaccine ON (ν = 0.65/yr vaccinating S_{f2},
S_{m2} → P; waning l = 0.1/yr) and compare to the ν = 0 baseline over 0–80 yr.
Does HIV **prevalence** (proportion infected) and **incidence** (new infections/yr)
reach a **peak and then decline** under vaccination, versus a baseline that rises
to a high endemic plateau? Report the peak time, peak level, and when decline begins.

## Modeling assumptions — apply to all results

### γ and R₀
We use the **biologically grounded γ = 0.1/yr** (mean ≈ 10 yr from HIV infection
to AIDS, within the textbook's stated 1–10 yr range), **NOT** the literal
Table 15.2 value γ = 1.16/yr. With γ = 1.16 the continuous-ODE basic reproduction
number is R₀ = c·√(β_mf·β_fm)/(μ+γ) ≈ 0.24 < 1, so the epidemic cannot ignite
(contradicting Fig 15.5); this is the verified core's documented finding. With
γ = 0.1/yr the mean infectious period is ≈ 8.1 yr and

- **R₀ = c·√(β_mf·β_fm)/(μ+γ) ≈ 2.346 > 1** (epidemic invades),
- herd-immunity / critical vaccination fraction **p_c = 1 − 1/R₀ ≈ 0.574**.

The epidemic is seeded with **infectious males I_{m2} = 5** (the literal seed
A_{m2} = 5 cannot ignite because AIDS individuals are excluded from the force of
infection). Vaccine waning ceiling **ν/(ν+l) = 0.65/0.75 ≈ 0.867**.

### Partner-pool convention (corrected default)
The force of infection is frequency-dependent, λ ~ I/(S+I+P). Vaccine-**Protected**
individuals are sexually active and uninfected, hence legitimate partners, so they
belong in the denominator (`count_p_in_denominator = True`, the corrected default).
Moving susceptibles into P therefore **dilutes the infectious frequency** and
yields genuine herd immunity. Because ν/(ν+l) = 0.867 **exceeds** p_c = 0.574,
ν = 0.65/yr is **above the herd-immunity threshold** ν_c ≈ 0.37/yr (see Q(c)), so
the vaccinated effective reproduction number is **R_eff ≈ R₀·(1−0.867) ≈ 0.31 < 1**.
(At ν = 0, P = 0, so the baseline is identical to the textbook.)

## Key numerical results

### Incidence — vaccination PREVENTS ignition (monotone decline from the seed)
| Scenario | Peak incidence | Peak time | Behavior | Incidence @ 80 yr |
|---|---|---|---|---|
| Baseline (ν = 0) | **790.6 new/yr** | 47.8 yr | rises to a large peak, stays high | 437.9/yr |
| Vaccine (ν = 0.65) | **2.3 new/yr** | 0 yr (the seed) | **monotone decline, never ignites** | ≈ 0.004/yr |

Because ν = 0.65 drives R_eff ≈ 0.31 < 1, the seeded infection **cannot grow**:
vaccinated incidence is highest at t = 0 (just the 5 seed males infecting a few
contacts), then **falls monotonically to essentially zero** within the horizon.
The peak incidence is suppressed by ≈ **100 %** (791 → 2.3 new/yr). The baseline
instead climbs to ≈ 791 new/yr near t ≈ 48 yr and stays high. So vaccination above
ν_c converts the epidemic from "ignite and plateau" into "never takes off."

### Prevalence — small early bump, then decline to ~0 within the horizon
| Scenario | Peak prevalence (overall) | Peak time | Prevalence @ 80 yr |
|---|---|---|---|
| Baseline (ν = 0) | 0.409 | ≈ 96 yr (then high endemic plateau) | 0.408 |
| Vaccine (ν = 0.65) | **0.0010** | **≈ 4.6 yr** | ≈ 0.0000 |

Under the corrected convention the vaccinated prevalence shows only a **tiny
interior bump (~0.001) around t ≈ 4.6 yr** from the initial seed cohort, then
**declines to ~0** as those individuals progress to AIDS and die without replacing
themselves through transmission — a clear **peak-and-decline within the horizon**,
in contrast to the baseline's rise to a ~0.41 endemic plateau. (No recovery
compartment exists, so the decline is paced by the ~8–10 yr I→A→death stock
clearing, but with R_eff < 1 there is no fresh inflow to sustain it.)

### Protected fraction saturates toward the analytic ceiling
The vaccine-protected fraction of the eligible (S + P) age-2 pool rises and
**saturates at P/(S+P) ≈ 0.852, close to the analytic ceiling ν/(ν+l) = 0.867**
(slightly lower because natural mortality μ acts on P), confirming the
take-with-waning steady state.

## Interpretation
Because the maximum achievable protected fraction (0.867) **exceeds** the herd
threshold p_c = 0.574, and (corrected convention) the protected individuals dilute
the partner pool, vaccination at ν = 0.65/yr pushes the effective reproduction
number to R_eff ≈ 0.31 < 1. The seeded epidemic therefore **never ignites**: new
infections fall monotonically from t = 0 and prevalence shows only a negligible
early bump before declining to ~0. This is a stronger result than "peak then
decline" — it is genuine herd-immunity control. The decline is not instantaneous
only because the existing I/A stock carries the virus for ~8–10 yr; with no
transmission to refill it, the infection clears. (At any rate **below** ν_c ≈ 0.37
vaccination would instead only lower the epidemic size, not prevent ignition.)

## Figures
- `figures/qa_prevalence.png` — overall prevalence, vaccine vs baseline (0–80 yr):
  baseline rises toward ~0.41; vaccinated stays near zero.
- `figures/qa_incidence.png` — incidence (new infections/yr), vaccine vs baseline:
  baseline peaks ~791/yr @ 48 yr; vaccinated declines monotonically from the seed.
- `figures/qa_protected_fraction.png` — protected fraction P/(S+P) and P/(all age-2)
  saturating near ν/(ν+l) = 0.867.

## Reproduce
```
python3 q_a_peak_decline.py
```
