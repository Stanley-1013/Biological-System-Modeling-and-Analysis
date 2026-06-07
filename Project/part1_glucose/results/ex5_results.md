# Exercise 5 - Hyperinsulinism / insulin shock - Results

## Question (Haefner Ch. 12, ex. 5)
Hyperinsulinism (Guyton 1986): overproduction of insulin drives plasma glucose
down (hypoglycemia). The CNS depends almost exclusively on plasma glucose; near
~70 mg/100 ml the patient shows erratic behaviour and loss of motor control;
below 20-50 mg/100 ml convulsions, coma and death follow ("insulin shock").

- **(a)** Simulate hyperinsulinism by adjusting Table 12.2 (first guess: increase
  a6 in F6). Terminate the patient when plasma glucose falls below
  **20 mg/100 ml**. Report the a6 setting that is fatal and the time of death.
- **(b)** Resuscitate with IV glucose: how much glucose must be added to prevent
  death?

## Modeling assumption (how a6 is scaled - disclosed)
The verified Cobelli core is strongly glucose-buffered: raising a6 alone does NOT
kill the patient. At steady state the pancreatic mass balance forces secretion
F6 == synthesis W, and the W gate closes as glucose falls, so endogenous plasma
insulin saturates (~40 uU/ml, x3.6 basal) and glucose only dips to ~78 mg/100 ml
before recovering. This homeostasis is correct - a normal pancreas cannot kill
you - which is why clinical insulin shock requires an **autonomous** insulin
source (insulinoma / overdose) that does not switch off when glucose drops.

We model this faithfully as an autonomous insulinoma whose output is set by the
a6 amplification and delivered to plasma at a glucose-independent rate:

> `Ip_tumor = (a6_multiplier - 1) * F6_basal`   uU/min,   F6_basal = 1.638e+04 uU/min

A multiplier of 1 is the healthy subject; multiplier M means the tumour secretes
(M-1)x basal F6 continuously. The native pancreas (W=F6 balance, all tanh shapes,
all transfer rates) is unchanged. The terminal death event is a solve_ivp
terminal event on `gbar - 20` with downward direction.

## (a) Fatal hyperinsulinism

| a6 mult | Ip_tumor (uU/min) | min gbar (mg/100ml) | died | t_death (min) |
|--------:|------------------:|--------------------:|:----:|--------------:|
| 1.0 | 0 | 91.50 | no | - |
| 2.0 | 1.638e+04 | 87.62 | no | - |
| 3.0 | 3.277e+04 | 79.66 | no | - |
| 4.0 | 4.915e+04 | 36.65 | no | - |
| 4.5 | 5.735e+04 | 20.10 | yes | 79.6 |
| 5.0 | 6.554e+04 | 20.06 | yes | 57.5 |
| 6.0 | 8.192e+04 | 20.22 | yes | 49.6 |
| 8.0 | 1.147e+05 | 20.11 | yes | 43.3 |
| 10.0 | 1.475e+05 | 20.24 | yes | 38.9 |

- **Lethal threshold (first fatal multiplier in the sweep): 4.5x.**
- Below the threshold the autonomous insulin is not enough to overwhelm hepatic
  output + falling peripheral uptake, and glucose stabilises above 20.
- **Demo scenario a6 x 8: death at
  t = 43.3 min.**
- Figure: `figures/ex5_fatal_decline.png` (glucose driven through the 70 and 20
  mg/100 ml lines; insulin rises far above basal).

## (b) IV-glucose rescue
Starting from the clearly-fatal a6 x 8 scenario
(untreated death at t = 43.3 min), a continuous IV
dextrose drip is given over a **240-min** clinical window
and the total grams is found by bisection (keep gbar >= 20 for the whole window).

- **Minimum rescue dose = 69.11 g** of glucose over
  240 min.
- Below this the nadir still crosses 20 and the patient dies; at/above it the
  glucose floor is held at 20 and the patient survives the window.
- Figure: `figures/ex5_rescue.png` (un-rescued death vs rescued survival).

### Assumption for the rescue dose
Because the modelled insulinoma is permanent, IV glucose is *temporizing*, not
curative (clinically the tumour must be removed) - exactly the textbook's
"short-term treatment = large IV glucose". The minimum dose is therefore quoted
for a defined clinical window (a continuous drip over
240 min); a longer window needs proportionally more
glucose. This is reported as an explicit assumption rather than an unconditional
"grams to survive forever", which is undefined for a permanent source.

## Figures
- `figures/ex5_fatal_decline.png`
- `figures/ex5_rescue.png`
