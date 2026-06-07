# Exercise 2 — The insulin "hump"

**Question.** Why does the "hump" in insulin concentration develop in Fig 12.5 (repeated glucose pulses, normal subject)? Why is there a similar hump for obese persons in Fig 12.7?

## Simulations

- (i) NORMAL subject, escalating repeated-pulse train ([0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 40.0] g at t=[0.0, 30.0, 70.0, 110.0, 180.0, 270.0, 400.0] min), 700 min.
- (ii) OBESE subject, single IVGTT 23.1 g, from the pre-equilibrated obese basal (settle_to_basal).

## Quantitative hump detection

- Normal repeated-pulse insulin: hump detected = **True**; insulin re-rises to ~37 µU/ml near t=450 min after dipping to ~31 µU/ml.
- Obese single-IVGTT insulin decay: hump detected = **True**; secondary insulin rise to ~32 µU/ml near t=105 min (dip ~22 µU/ml).
- Obese peak plasma insulin = 36 µU/ml vs basal 11 µU/ml.

## Mechanism — common origin of both humps

The pancreatic secretion flux is **F6 = 0.5·a6·[1 + tanh(b6(Δḡ + c6))]·r** (Eq 12.6), i.e. secretion is *proportional to the releasable pool r*. r is refilled from the stored pool s on its own slow timescale (dr/dt = k21·s − k12·r − F6; ds/dt = −k21·s + k12·r + W). You cannot secrete insulin you do not have, and you cannot refill r instantly.

**(i) Repeated pulses (Fig 12.5).** Each glucose pulse opens the F6 gate and drains r into the liver pool. Because the pulses are spaced shorter than the pool-refill / glucose-clearance time, r is repeatedly depleted and then over-refilled from s; the escalating dose ladder makes each later pulse drain more. The multi-compartment lag (r→liver l→plasma p→interstitial i) stacks the delayed contributions of successive pulses, so plasma insulin does NOT decay exponentially between pulses — it accumulates into a delayed **hump** after the later, larger pulses, which greatly delays recovery. The r/s and F6 panels in the figure show the depletion-refill cycling that drives this.

**(ii) Obese subject (Fig 12.7).** Same pool dynamics, but driven by the parameter changes rather than repeated input. Obese overrides make secretion **hypersensitive**: b6 = 0.5 (vs nominal 9.23e-2) hugely steepens the F6 gate, so a single glucose load triggers an outsized, abrupt drain-and-refill of r; and m02 = 0.13 alters liver-insulin clearance so the downstream insulin clears sluggishly. The pools overshoot and the secretion flux re-engages as r refills, producing an abnormal **hump in the insulin-decay curve** even though the glucose response is near-normal. The same F6 ∝ r over-refill mechanism underlies both figures — repeated forcing in 12.5, hypersensitive parameters in 12.7.

## Figures

- `ex2_normal_hump.png` — normal repeated-pulse run (glucose, insulin, r/s pools, F6).
- `ex2_obese_hump.png` — obese single-IVGTT run (glucose, insulin, r/s pools, F6).
