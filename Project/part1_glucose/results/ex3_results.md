# Exercise 3 — Repeated glucose pulses: diabetic vs normal

**Question.** Using the DIABETIC parameter set, administer the Fig 12.5 glucose-pulse sequence (0.5, 1.0, 2.5, 5, 10, 20, 40 g to a 70-kg subject at t = 0, 30, 70, 110, 180, 270, 400 min). Plot plasma glucose and insulin and compare to the same protocol on a NORMAL subject.

**Protocol.** Identical escalating pulse train applied to both subjects over 800 min. Both use the single canonical configuration from the verified core (`cobelli.make_patient`). Normal starts from its calibrated clinical basal. The diabetic uses the Table 12.3 secretion/uptake-shape changes (bw, cw, b6, c6, b42, c42), the insulin-driven hepatic (F2) and peripheral (H4) uptake gates frozen to scale-consistent constants, and a calibration to its OWN elevated operating point; its calibrated basal_amounts ARE the diabetic steady state, used directly as the IC (settle_to_basal is a no-op on it).

> **Finding (disclosed).** Table 12.3 lists `F2 = 0.037`, but that value is in the textbook's native (un-scaled) flux units. Our core multiplies the four glucose fluxes by glucose_flux_scale=1e5 (CALIBRATION_FINDINGS.md), so the literal 0.037 would become a ~3700 mg/min constant hepatic *vacuum* (~70x the normal basal F2 of ~52 mg/min) that clamps glucose flat -- physiologically backwards. The scale-consistent reading of "F2/H2 replaced by a constant" is that the diabetic liver can no longer RAMP uptake with insulin: we freeze F2 near the NORMAL basal hepatic-uptake flux (~5.25e-4 unscaled), and freeze H4 at the Table 12.3 0.0012. The elevated diabetic basal does not emerge from freezing alone (M1 glucose self-suppression and the glucagon gate make 91.5 a strong attractor), so the diabetic is calibrated to its own operating point (DIABETIC_BASAL = 140/7/75) by the same under-determined scales (aw, a71, b52) the normal subject uses -- no feedback shape is changed. At that low liver-insulin state the UNFROZEN H1 gate naturally sits high (~0.66 vs 0.25 normal): hepatic production is no longer suppressed by insulin (the textbook diabetic mechanism, emergent not forced). This yields the correct signature below.

## Key numeric results

| Quantity | Normal | Diabetic |
|----------|--------|----------|
| Basal glucose (mg/100 ml) | 91.5 | 140.0 |
| Peak glucose (mg/100 ml)  | 366 | 418 |
| Final glucose (mg/100 ml) | 89.9 | 139.7 |
| Basal insulin (µU/ml)     | 11.0 | 7.00 |
| Peak insulin (µU/ml)      | 62 | 18.3 |
| Recovery after last pulse (min, within 5% of basal) | 462 | 524 |

## Discussion

- **Basal level.** Diabetic basal glucose (140.0 mg/100 ml) is higher than normal (91.5) — this is the diabetic's own calibrated operating point (DIABETIC_BASAL), with impaired insulin-driven uptake (F2, H4 frozen) and a high H1 gate keeping hepatic production up. Diabetic basal insulin (7.00 µU/ml) is below the normal 11.0 µU/ml (blunted secretion).
- **Insulin response.** The diabetic peak insulin (18.3 µU/ml) is blunted vs the normal peak (62 µU/ml) — blunted synthesis/secretion parameters (Table 12.3) limit the pancreatic response.
- **Recovery.** With insulin-driven hepatic and peripheral uptake impaired (F2 and H4 frozen low) and production not insulin-suppressed (high H1), the diabetic clears each pulse far more slowly; glucose stacks across the escalating ladder and stays elevated above its already-high basal, whereas the normal subject returns toward basal between pulses. On a standard IVGTT this same configuration recovers in ~100 min vs ~52 min for normal (~1.9x), the model expression of the textbook's '~2x slower recovery' for diabetes (§12.3.6).
- **The hump.** In the normal subject the closely-spaced later pulses produce the insulin hump (Ex 2: F6 ∝ r pool depletion/refill). In the diabetic subject the blunted secretion machinery cannot mount the same overshoot, so the characteristic insulin hump is suppressed even though glucose remains high.

## Figure

- `ex3_diabetic_vs_normal.png` — overlay (row 1) and side-by-side (row 2) plasma glucose and insulin for normal vs diabetic.
