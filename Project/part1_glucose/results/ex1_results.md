# Exercise 1 — Normal IVGTT (reproduce Fig 12.4a/b)

**Question.** Code the Cobelli glucose-regulation model and reproduce Figs 12.4a (plasma glucose) and 12.4b (plasma/liver/interstitial insulin). Also plot glucagon concentration and the liver glucose-uptake rate F2. Discuss in light of the Forrester diagram, and answer: **where does the majority of glucose go?**

**Protocol.** NORMAL 70-kg subject, single IV glucose bolus 0.33 g/kg = **23.1 g** delivered over 2 min, integrated from the calibrated basal steady state for 150 min (LSODA).

## Key numeric results

- Plasma glucose: basal **91.5** -> peak **250 mg/100 ml** @ t=2 min; recovery (within 5% of basal) at t = **52 min** (Fig 12.4 quotes ~90 min).
- Plasma insulin: basal **11** -> peak **40 µU/ml** (rises within minutes of the bolus).
- Plasma glucagon: basal **75** -> dips to **6 nU/ml** (suppressed by the glucose+insulin rise).

## Where does the majority of glucose go? (cumulative flux integrals)

Integrating the glucose-disposal fluxes (true mg/min) over the 150-min response:

| Sink | Cumulative (mg) | % of peripheral disposal |
|------|-----------------|--------------------------|
| F4 muscle / adipose | 11202 | **27.9%** |
| F5 CNS / RBC        | 24503 | **61.0%** |
| F3 renal            | 4465 | **11.1%** |
| (∫NHGB net hepatic balance, signed) | 16855 | — |

Total peripheral disposal (F3+F4+F5) = **40170 mg** over the window. The net hepatic balance ∫NHGB = 16855 mg (sign: positive = the liver is a net glucose *source* on balance over the window; negative = net sink).

**Answer:** the majority of disposed glucose goes to **CNS + red blood cells (F5) (61.0%)**, followed by muscle/adipose tissue (F4) (27.9%); renal excretion (F3) is 11.1%.

## Discussion (Forrester diagram)

- The bolus drives plasma glucose up; the rise immediately stimulates the pancreatic releasable pool to secrete insulin (F6 ∝ r), so plasma, liver and interstitial insulin all climb within minutes (Fig 12.4b).
- High glucose + rising insulin suppress glucagon secretion (F7 uses two inhibitory −tanh gates), so glucagon dips sharply, as seen.
- In the Forrester diagram the dominant glucose-clearing compartments are the insulin-sensitive peripheral tissues (F4, muscle+adipose) and the large, nearly insulin-independent CNS/RBC sink (F5). Renal loss (F3) stays near zero unless ḡ exceeds the ~180 mg/100 ml renal threshold; here the peak is 250 mg/100 ml, so F3 contributes only 11.1%.
- Insulin acts on the liver (F1/F2 via liver insulin) and on peripheral tissue (F4 via interstitial insulin); the net hepatic balance NHGB swings from a basal source toward uptake as liver insulin rises, helping clear the load.

## Figures

- `ex1_glucose.png` — plasma glucose (Fig 12.4a)
- `ex1_insulin.png` — plasma/liver/interstitial insulin (Fig 12.4b)
- `ex1_glucagon_F2.png` — glucagon concentration & liver uptake F2
- `ex1_disposal_split.png` — cumulative disposal fluxes & % split

## Calibration note

Per CALIBRATION_FINDINGS.md, the literal Table 12.2 is under-specified for reproducing Fig 12.4 (glucose-flux scale ~5 orders too small; basal insulin synthesis ~6 orders too small). The core applies a documented minimal fix (uniform glucose_flux_scale; aw/a71/b52 basal-balance scales) that leaves every tanh feedback shape and transfer rate exactly as printed. Results above are from that calibrated core.

