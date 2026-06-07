# Exercise 4 — Meal (60-min glucose infusion) vs IVGTT pulse

## Question
Simulate the glucose infusion diagnostic test by adding glucose NOT as an
instantaneous IVGTT pulse but as a constant input spread over 60 minutes (a
meal): administer 25 g of glucose to a 70-kg
subject over 60 minutes. Plot plasma glucose and insulin
over 0-180 min, compare against an IVGTT delivering the SAME
total dose as a short pulse, and explain the differences in terms of model
mechanisms. (Haefner Ch. 12, §12.5 #4.)

## Documented assumptions
- **Subject:** NORMAL patient, 70 kg, started from the
  clinical basal steady state (gbar = 91.5 mg/100 ml, pbar = 11 µU/ml). The
  same calibrated core model verified against Fig 12.4 is used unchanged.
- **Meal forcing:** 25 g = 25000 mg delivered as
  a *constant* glucose infusion Ig(t) = 416.7 mg/min for
  t in [0, 60] min, 0 afterwards (rectangular pulse).
- **IVGTT comparison:** identical total 25 g delivered over a
  short 2-min rectangular bolus
  (Ig = 12500 mg/min), so the ONLY
  difference between the two runs is the temporal spread of the input.
- **First-order approximation (cite Dalla Man, Rizza & Cobelli 2007;
  references/ref3_man_2007.md):** a real oral meal is absorbed through a
  gastro-intestinal stage (stomach -> gut -> plasma) with nonlinear gastric
  emptying, giving a smooth, delayed, *time-varying* glucose rate of appearance
  Ra(t). Our constant 60-min infusion is a deliberate first-order stand-in for
  Ra(t); it reproduces the essential contrast with an IV bolus (gradual
  appearance) without implementing the full 2007 GI submodel, which this
  exercise does not require.

## Key numeric observations (from the actual simulation)
| Metric | Meal (60 min) | IVGTT (2 min) |
|---|---|---|
| Peak plasma glucose (mg/100 ml) | 143.9 | 263.4 |
| Time-to-peak glucose (min) | 59.9 | 2.0 |
| Peak plasma insulin (µU/ml) | 30.5 | 40.2 |
| Time-to-peak insulin (min) | 13.8 | 4.2 |
| Glucose recovery (within 5% basal, min) | 82.5 | 53.9 |

Basal reference: glucose 91.5 mg/100 ml,
insulin 11.0 µU/ml.

## Figure
- `figures/ex4_meal_vs_ivgtt.png` — three panels: plasma glucose (overlay), plasma insulin
  (overlay), and the glucose input rate Ig(t) showing the two protocols deliver
  the same 25 g total but with very different temporal spread.

## Discussion (grounded in the output)
**Glucose peak height and timing.** The IVGTT dumps all 25 g into
the glucose pool within 2 min, faster than any clearance
flux can respond, so glucose spikes to 263.4 mg/100 ml almost
immediately (t ~= 2.0 min). The meal delivers the identical
mass at only 417 mg/min, slow enough that the clearance fluxes
(renal F3, peripheral F4, CNS/RBC F5) and the suppression of hepatic production
remove glucose *as it arrives*. The result is a much lower, broader glucose
excursion peaking at 143.9 mg/100 ml near the end of the infusion
window (t ~= 59.9 min). Same dose, very different peak.

**Insulin response.** In the Cobelli model insulin secretion is gated by the
standardized glucose deviation Δḡ through the W (synthesis) and F6 (release)
tanh gates, with F6 drawing on the finite releasable pool r. Both protocols show
an early first-phase peak as r is secreted, but the meal peak
(30.5 µU/ml) is blunted relative to the sharp IVGTT spike
(40.2 µU/ml) because the gentler glucose rise opens the
secretion gates less strongly. After the first-phase peak, insulin settles to a
lower sustained plateau during the meal infusion (the releasable pool partially
depletes and is refilled by synthesis W), whereas the IVGTT produces a single
tall transient that then decays as glucose is cleared. The insulin profile thus
mirrors the glucose drive: a brief tall pulse for the IVGTT versus a lower,
broader response for the meal.

**Mechanistic summary.** Spreading the same glucose load over 60 min lowers the
instantaneous glucose appearance rate, which (i) lets the clearance fluxes keep
pace, producing a lower and broader glucose peak, and (ii) drives the
glucose-gated insulin secretion less hard, producing a blunted insulin response.
This is exactly why an oral meal stresses glucose homeostasis far less than an
equal-dose IV bolus, and why diagnostic tolerance tests use a rapid IV bolus to
maximally probe the feedback system. A physiologically realistic meal would be
even gentler still, because gastric emptying further smooths and delays the
glucose rate of appearance (Dalla Man et al. 2007).
