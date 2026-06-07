# Exercise 6 - Insulin bolus and recovery - Results

## Question (Haefner Ch. 12, ex. 6)
A normal patient should recover from insulin shock. Simulate the rapid
ingestion/injection of insulin = **0.10 U/kg** body weight over **2 minutes**.
Observe the momentary hypoglycemia. Did the subject die? Repeat with an obese
subject.

## Protocol
- Dose: 0.10 U/kg x 70 kg = **7 U = 7.00e+06 uU**,
  delivered as a rectangular `Ip(t)` pulse over 2 min
  (rate 3.50e+06 uU/min into the plasma-insulin
  compartment, Eq. 12.5).
- Initial condition: each subject pre-equilibrated to its own natural basal steady
  state with `settle_to_basal()`.
- Terminal death event: solve_ivp terminal event on `gbar - 20`
  (death if plasma glucose < 20 mg/100 ml).

## Results

| subject | basal gbar | glucose nadir | t_nadir (min) | insulin peak (uU/ml) | verdict | t_death (min) | t_recovery (min) |
|---------|-----------:|--------------:|--------------:|---------------------:|:-------:|--------------:|-----------------:|
| normal | 91.5 | 20.08 | 21.3 | 1541 | **DIES** | 21.4 | - |
| obese | 91.5 | 59.83 | 37.2 | 1542 | survives | - | 103.6 |

- **Normal nadir = 20.08 mg/100 ml -> DIES**
  (death at t = 21.4 min).
- **Obese nadir = 59.83 mg/100 ml -> survives**
  (recovers to 91.1 by t = 103.6 min).

## Discussion (grounded in the actual output)
Both subjects receive the identical 7 U bolus and reach essentially the
same plasma-insulin peak (~1541 uU/ml), yet their glucose
nadirs differ sharply (20 vs 60 mg/100 ml). The
difference comes entirely from peripheral glucose disposal (F4): for the obese
subject the model freezes the interstitial-insulin gate H4 at the small constant
0.0012 (Table 12.3) and shifts the glucose gate (b42, c42), so the same flood of
insulin removes far less glucose per minute. This is the model's representation of
**insulin resistance**, and here it is *protective* against an insulin overdose:
the normal subject's fully insulin-responsive muscle/adipose tissue drives glucose
all the way through the 20 mg/100 ml line, while the insulin-
resistant obese subject bottoms out in the hypoglycemic-but-survivable range and
then recovers as the bolus clears and counter-regulation (reduced uptake, glucagon)
restores glucose toward basal.

The normal result sits right at the lethal boundary (nadir touches
20); the terminal event fires consistently across solvers
(LSODA/Radau) and step sizes, so the verdict is robust within the model.

## Figure
- `figures/ex6_insulin_bolus_normal_vs_obese.png`
