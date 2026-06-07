# Exercise 7 — A bowl of vanilla ice cream: normal vs diabetic vs obese

## Question
Simulate the glucose, insulin, and glucagon dynamics resulting from a normal,
diabetic, and obese subject each consuming an average bowl of vanilla ice cream.
(Haefner Ch. 12, §12.5 #7.)

## Documented assumptions
- **Ice-cream carbohydrate content (key assumption):** "An average bowl of
  vanilla ice cream" = ~1 cup (~130 g) of regular vanilla ice cream. USDA
  FoodData Central ("Ice creams, vanilla") lists ~23-24 g carbohydrate per 100 g,
  almost entirely sugar (sucrose + lactose). One cup therefore supplies
  ~130 g x 0.24 ~= 31 g carbohydrate. **We adopt 30 g of
  digestible carbohydrate, treated as 100% appearing as plasma glucose** (a
  conservative upper bound; lactose + fat would slow real absorption). Source:
  USDA FoodData Central; standard label serving ~1/2 cup ~15-16 g carb, so a full
  bowl ~1 cup ~30 g.
- **Eating duration:** the bowl is eaten over **40 min**
  (within the 30-45 min brief), modelled as a constant glucose infusion
  Ig(t) = 750.0 mg/min for t in [0, 40] min.
- **Meal as first-order Ra(t) (cite Dalla Man et al. 2007;
  references/ref3_man_2007.md):** a real meal is absorbed through a
  gastro-intestinal stage giving a smooth, delayed glucose rate of appearance.
  Our constant infusion is a deliberate first-order approximation of that Ra(t).
- **Subjects & initial conditions:** NORMAL, DIABETIC, OBESE parameter sets from
  the verified cobelli.py core (Tables 12.2/12.3), 70 kg each.
  NORMAL starts from the clinical basal steady state. The DIABETIC subject uses
  the single canonical core configuration (`cb.make_patient('diabetic')`):
  Table 12.3 secretion/uptake-shape changes, the insulin-driven hepatic (F2) and
  peripheral (H4) uptake gates frozen to scale-consistent constants, and a
  calibration to its OWN elevated operating point (DIABETIC_BASAL = 140/7/75; see
  `cobelli.calibrate_diabetic_basal` and CALIBRATION_FINDINGS.md), so its
  calibrated basal_amounts ARE its (elevated, blunted) steady state and are used
  directly. OBESE is anchored to the normal clinical basal, so its pre-meal IC is
  obtained with `cb.settle_to_basal()` (integrate to its natural steady state).

## Key numeric observations (from the actual simulation)
| Subject | Basal g (mg/100ml) | Peak g | t-peak g (min) | Basal ins (µU/ml) | Peak ins | t-peak ins (min) | Basal glucagon (nU/ml) | Min glucagon | g recovery (min) |
|---|---|---|---|---|---|---|---|---|---|
| Normal | 91.5 | 185.7 | 39.8 | 11.0 | 36.9 | 8.3 | 75.0 | 2.2 | 77.3 |
| Diabetic | 140.0 | 252.8 | 40.0 | 7.0 | 9.4 | 30.3 | 75.0 | 1.5 | 126.4 |
| Obese | 91.5 | 206.8 | 40.0 | 11.0 | 35.5 | 5.0 | 74.9 | 1.2 | 113.8 |

(Glucose/insulin "peak" = maximum plasma concentration; glucagon "min" = maximum
suppression below basal. Recovery = first time glucose returns within 5% of that
subject's own basal.)

## Figures
- `figures/ex7_icecream_glucose.png` — plasma glucose, three subjects.
- `figures/ex7_icecream_insulin.png` — plasma insulin, three subjects.
- `figures/ex7_icecream_glucagon.png` — plasma glucagon, three subjects.

## Discussion (grounded in the actual output)
**Glucose.** The NORMAL subject shows a clear glucose rise to ~186 mg/100 ml
during eating, then clearance back toward its 91.5 basal once insulin acts. The
OBESE subject reaches a slightly *higher* glucose peak (~207 mg/100 ml) but a
broadly similar excursion shape from the same ~91.5 basal, consistent with the
textbook statement that the obese glucose response is "nearly normal" while the
abnormality is concentrated in the insulin curve (Fig 12.7).

The DIABETIC subject now starts from an **elevated fasting basal of
140 mg/100 ml** (its own calibrated operating point) and rises to the
**highest peak (~253 mg/100 ml)** of the three, then recovers **more slowly**
(~126 min vs ~77 min for normal back to within 5% of their respective basals).
This is the textbook diabetic signature (Fig 12.6 / §12.3.6: higher basal,
larger and slower excursion). The mechanism is explicit and consistent: the
insulin-driven hepatic (F2) and peripheral (H4) uptake gates are frozen low (the
liver and periphery can no longer ramp glucose uptake with insulin), and at the
low-liver-insulin diabetic state the UNFROZEN hepatic-production gate H1 sits
high (~0.66 vs 0.25 normal), so the liver keeps releasing glucose. Impaired
uptake + unsuppressed production = a higher, slower glucose excursion.

**Scale-consistency note (disclosed).** Table 12.3 lists `F2 = 0.037`, but in
the textbook's native (un-scaled) units; our core multiplies glucose fluxes by
`glucose_flux_scale = 1e5`, so the literal value would be a ~3700 mg/min hepatic
*vacuum* that clamps glucose flat — physiologically backwards. We therefore
freeze F2 near the NORMAL basal hepatic-uptake flux (~52 mg/min scaled) instead.
Because the strong glucose self-suppression (M1) and glucagon feedback make
91.5 mg/100 ml a robust attractor, the elevated diabetic basal does not emerge
from freezing alone; the diabetic is calibrated to its OWN operating point
(DIABETIC_BASAL = 140/7/75) using the SAME under-determined source/clearance
scales (aw, a71, b52) the normal subject uses — no feedback shape, transfer rate,
or flux scale is changed. See `cobelli.calibrate_diabetic_basal` and
CALIBRATION_FINDINGS.md.

**Insulin.** The NORMAL subject mounts a clean first-phase rise then decay
(11 → ~37 µU/ml). The OBESE subject reproduces the characteristic abnormal
**hump** in the insulin-decay curve (Fig 12.7): after the first-phase peak
(~35 µU/ml) and a brief dip, insulin rises again to a broad secondary peak
before finally decaying — driven by the altered F6 secretion gate (b6 = 0.5,
c6 = −3.64) and faster m02 clearance. The DIABETIC subject's insulin is honestly
**blunted**: it starts lower (7.0 µU/ml basal) and rises only weakly to
~9.4 µU/ml — the reduced beta-cell secretion of Table 12.3 (bw, cw, b6, c6)
plus the diabetic calibration to a low fasting insulin. This is the low/blunted
diabetic insulin response of §12.3.6, now from a genuinely elevated glucose
stimulus rather than the previous flat-clamp artifact.

**Glucagon.** In all three subjects the meal-driven glucose and insulin rise
suppress glucagon secretion (F7 is gated negatively by both glucose and
interstitial insulin), so glucagon plunges from ~75 nU/ml toward ~1-2 nU/ml
during the meal and then recovers. The diabetic suppresses too (75 → ~1.5),
because its glucose now genuinely rises with the meal. The "Min glucagon" column
quantifies the suppression depth for each subject.

**Overall.** A single identical ice-cream meal produces three distinct responses
from the verified core, all from one consistent canonical configuration:
well-regulated with a clean insulin spike and strong glucagon suppression
(normal); near-normal glucose but with the diagnostic abnormal insulin-decay
hump (obese); and an elevated-basal, higher-and-slower glucose excursion with
blunted insulin (diabetic) — matching Fig 12.6 / §12.3.6 qualitatively. The
diabetic configuration is identical to the one used in Exercise 3; the earlier
per-script workarounds and the flat-clamp artifact are gone.
