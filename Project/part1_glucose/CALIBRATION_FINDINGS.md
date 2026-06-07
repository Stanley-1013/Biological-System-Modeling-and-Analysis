# Part 1 — Calibration findings (must be disclosed in the report)

**Finding (verified independently by two agents):** Haefner's Table 12.2, taken literally in an
amount-based formulation, **does not reproduce Figs 12.4a/b**. This is a genuine textbook gap, not a
units bug on our side (an amount↔concentration Vb≈140 factor closes <1% of it).

## Quantitative evidence (literal Table 12.2, 70 kg)
- Basal glucose amount g_basal = 91.5 mg/100ml × Vb(14000 ml) = **12,810 mg**.
- Literal basal glucose clearance F3+F4+F5 ≈ **8.4×10⁻⁴ mg/min** ⟹ clearance timescale ≈ **1.5×10⁷ min**
  (vs the ~90 min recovery in Fig 12.4). Glucose essentially never clears.
- Basal plasma insulin amount = 11 µU/ml × Vp(3150 ml) = **34,650 µU**; required basal secretion
  F6 ≈ **1.6×10⁴ µU/min**; but literal synthesis **W(basal) ≈ 0.017 µU/min** (~10⁶× too small).
  The insulin (and glucagon) axes collapse to ~0 → no IVGTT response is possible.

## Minimal, structure-preserving calibration applied (all disclosed)
1. **`glucose_flux_scale` (uniform, default 1e5)** on the four glucose fluxes (NHGB, F3, F4, F5):
   sets the clearance timescale to ~90 min. Because NHGB = F3+F4+F5 at basal, a *common* scale cancels
   → basal steady state and all tanh feedback shapes are **exactly unchanged** (verified: basal
   residual identical, 3.6e-12, for scale ∈ {1, 1e3, 1e5, 1e7}). Set to 1.0 to recover the literal table.
2. **`aw`, `a71`** (insulin-synthesis & glucagon-secretion source scales): chosen so the published
   clinical basal is an exact steady state. No tanh slope (b) or centre (c), and no transfer rate
   (mij/kij), is altered.
3. **`b52`** (insulin-independent CNS/RBC baseline glucose sink, an F5 *offset*): shifted by the tiny
   published NHGB−(F3+F4+F5) imbalance so dg/dt = 0 at basal exactly. A constant offset, not a shape.

## Why this is the honest, rigorous framing
- The model is explicitly "semi-phenomenological … tailored/scaled to a particular patient" (Haefner
  §12.3; Cobelli et al. 1982). Choosing under-determined *source/clearance scales* to sit the model at
  a patient's basal operating point is exactly the intended use; we changed **no feedback structure**.
- Verification after calibration: basal residual 3.6e-12; normal IVGTT (0.33 g/kg) → glucose peak
  **250 mg/100ml**, recovery within ~52 min; plasma insulin 11→40 µU/ml fast then decays; glucagon dips
  then recovers; LSODA vs Radau agree to 1.6e-4. These match Fig 12.4 qualitatively.
- **What we do NOT claim:** that 1e5 / the recalibrated aw, a71, b52 are the original Cobelli (1982)
  coefficients. They are a documented fit to reproduce the published figures from an under-specified table.

> Report Part 1 / Exercise 1 should present this as a finding ("the literal table is under-specified;
> here is the minimal documented calibration to reproduce Fig 12.4"), not bury it.

---

# Diabetic subject — canonical configuration (Ex 3 & Ex 7)

**Finding.** Two issues had to be resolved for the diabetic subject (§12.3.6 / Fig 12.6):

1. **Table 12.3's `F2 = 0.037` is in un-scaled units.** Our core multiplies the four glucose fluxes
   by `glucose_flux_scale = 1e5`. Feeding the literal 0.037 through that scale makes the frozen hepatic
   uptake a constant **~3700 mg/min** — ~70x the normal basal F2 (~52 mg/min) — turning the diabetic
   liver into a glucose *vacuum* that **clamps glucose flat** (the previous ex7 artifact) and gives
   faster-than-normal clearance (the opposite of diabetes). The scale-consistent reading of "F2/H2
   replaced by a constant" (the liver can no longer **ramp** uptake with insulin) is to freeze F2 near
   the **normal basal hepatic-uptake flux** (`F2_const = 5.25e-4` unscaled ≈ 52 mg/min). H4 is frozen
   at the Table 12.3 `0.0012` (already below the normal basal H4 ≈ 0.041, i.e. impaired peripheral
   uptake).

2. **The elevated diabetic basal cannot emerge from freezing alone.** The glucose self-suppression
   gate M1 and the glucagon gate G1 make the normal basal (91.5 mg/100 ml) a **strong attractor**:
   with the normal calibration, freezing the uptake gates leaves the basal at ~91.5 (verified — the
   system relaxes straight back). Reproducing Fig 12.6's elevated fasting glucose therefore requires
   calibrating the diabetic to its **own operating point**, exactly as the normal subject is calibrated
   to its own (the intended "scale the model to a particular patient" use; Cobelli et al. 1982).

**Canonical diabetic calibration (`cobelli.calibrate_diabetic_basal`).** Deviations stay framed against
the NORMAL clinical reference (91.5/11/75), so the diabetic state is genuinely elevated/blunted. We
target a documented diabetic fasting state `DIABETIC_BASAL = {gbar:140, pbar:7, cbar:75}` and recalibrate
ONLY the same three under-determined source/clearance scales the normal calibration uses (`aw`, `a71`,
`b52`) so that state is an **exact** steady state (residual ~3e-13). No tanh shape parameter (b/c), no
transfer rate (mij/kij), the glucose_flux_scale, and no Table 12.3 override is changed. At this low
liver-insulin state the **unfrozen** hepatic-production gate `H1` naturally sits high (~0.66 vs 0.25
normal): hepatic production is no longer suppressed by insulin — the textbook diabetic mechanism,
emergent rather than hand-forced. Glucagon is kept at the normal reference (75) because pushing it higher
inflates the hypersensitive G1 gate into an unphysical hepatic-production regime.

**Verification (through the real core).**
- Diabetic fasting basal **140 mg/100 ml** (elevated vs normal 91.5); basal insulin **7.0 µU/ml**
  (blunted vs 11); glucagon 75; residual 3.4e-13; `settle_to_basal` is a no-op refinement.
- Standard IVGTT (0.33 g/kg): diabetic recovery **~100 min vs ~52 min** normal (**~1.9x slower**),
  peak insulin **~13 µU/ml vs ~40** normal (blunted). Ice-cream meal (Ex 7): diabetic peak glucose
  ~253 (highest of the three), recovery ~126 vs ~77 min normal.
- Normal and obese paths are **unchanged** (verify_core still PASS; obese still anchored to 91.5 via
  settle_to_basal). F2 is frozen ONLY in `mode == 'diabetic'`.

**Single source of truth.** Both Ex 3 and Ex 7 now use `cb.make_patient('diabetic')` directly — the
per-script frozen-override workarounds (`F2_const=H4_const=0`) and the ex7 flat-clamp artifact are gone.

**What we do NOT claim:** that 140/7/75 or the recalibrated aw/a71/b52 are original Cobelli (1982)
values. They are a documented operating-point fit to reproduce Fig 12.6 qualitatively from an
under-specified table, exactly analogous to the normal calibration above.
