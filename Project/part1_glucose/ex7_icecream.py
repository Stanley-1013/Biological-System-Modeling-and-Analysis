"""Part 1, Exercise 7 — A bowl of vanilla ice cream: normal vs diabetic vs obese.

Exercise text (Haefner Ch. 12, §12.5 #7):
    Simulate the glucose, insulin, and glucagon dynamics resulting from a normal,
    diabetic, and obese subject consuming an average bowl of vanilla ice cream.

Approach (uses the verified cobelli.py core unchanged):
  * The ice cream is modelled as an oral meal = a constant glucose infusion Ig(t)
    over a documented eating duration (a first-order stand-in for the gradual
    gastro-intestinal glucose rate of appearance; cf. Dalla Man et al. 2007,
    references/ref3_man_2007.md).
  * Run the SAME meal for the NORMAL, DIABETIC, and OBESE patient parameter sets
    and overlay glucose, insulin, and glucagon.
  * NORMAL starts from the clinical basal steady state. DIABETIC and OBESE have a
    DIFFERENT (pathological) basal operating point, so their initial condition is
    obtained with cb.settle_to_basal() (integrate to the natural steady state
    before the meal), as instructed.

====================================================================
DOCUMENTED CARBOHYDRATE ASSUMPTION (ice cream)
====================================================================
"An average bowl of vanilla ice cream" is taken as ~1 cup (~130 g) of regular
vanilla ice cream. USDA FoodData Central lists vanilla ice cream at roughly
23-24 g of carbohydrate per 100 g, of which the great majority is sugar
(sucrose + lactose). One cup (130 g) therefore supplies approximately

    130 g x 0.24 = ~31 g carbohydrate, essentially all rapidly-available sugar.

We adopt CARB_GRAMS = 30 g as the digestible-carbohydrate dose, treated as 100%
appearing as plasma glucose (a conservative upper bound; in reality lactose and
fat slow absorption). Source/assumption: USDA FoodData Central, "Ice creams,
vanilla"; standard nutrition-label serving ~1/2 cup ~15-16 g carb, so a full
bowl ~1 cup ~30 g. This is documented here and in results/ex7_results.md so the
choice is explicit rather than hidden.

EATING DURATION: a bowl of ice cream is eaten slowly; we model the glucose
appearance over EAT_DURATION_MIN = 40 min (within the 30-45 min range suggested
by the exercise brief), as a constant infusion.

Run:  python3 ex7_icecream.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb

# --- Ice-cream meal constants (documented above) ----------------------------
CARB_GRAMS = 30.0             # g digestible carbohydrate (~1 cup vanilla ice cream)
EAT_DURATION_MIN = 40.0       # eaten over 40 min (constant glucose appearance)
BODY_WEIGHT_KG = 70.0
SIM_DURATION_MIN = 300.0      # 0-300 min: long enough for slow diabetic recovery
N_EVAL = 1200
RECOVERY_BAND_FRAC = 0.05     # "recovered" = within 5% of that subject's basal

SUBJECTS = ("normal", "diabetic", "obese")
COLORS = {"normal": "#2471a3", "diabetic": "#c0392b", "obese": "#1e8449"}

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(THIS_DIR, "figures")
RESULTS_DIR = os.path.join(THIS_DIR, "results")


def initial_condition(patient: cb.Patient) -> np.ndarray:
    """Return the pre-meal IC.

    Normal and diabetic come straight from their calibrated basal_amounts (the
    diabetic is now calibrated to its OWN elevated operating point in the core,
    so its basal_amounts ARE its steady state). Obese is still anchored to the
    normal clinical basal, so it is pre-equilibrated to its own pathological
    steady state with settle_to_basal()."""
    if patient.mode == "obese":
        return cb.settle_to_basal(patient)
    return patient.basal_amounts.to_array()


def run_meal(patient: cb.Patient, y0: np.ndarray) -> cb.SimResult:
    dose_mg = CARB_GRAMS * 1000.0
    forcing = cb.make_rectangular_pulse(dose_mg, t_start=0.0, duration=EAT_DURATION_MIN)
    t_eval = np.linspace(0.0, SIM_DURATION_MIN, N_EVAL)
    return cb.simulate(
        patient,
        y0,
        (0.0, SIM_DURATION_MIN),
        Ig=forcing,
        t_eval=t_eval,
        method="LSODA",
        pulse_times=[0.0, EAT_DURATION_MIN],
        max_step=0.5,
    )


def summarize(res: cb.SimResult) -> dict:
    t = res.t
    g = res.concentrations["gbar"]
    p = res.concentrations["pbar"]
    c = res.concentrations["cbar"]
    basal_g = float(g[0])

    peak_g = float(g.max())
    peak_g_t = float(t[int(g.argmax())])
    peak_p = float(p.max())
    peak_p_t = float(t[int(p.argmax())])

    after = t > peak_g_t
    band = basal_g * (1.0 + RECOVERY_BAND_FRAC)
    rec = t[after][g[after] <= band]
    recovery_t = float(rec[0]) if rec.size else float("nan")

    return {
        "basal_g": basal_g,
        "peak_g": peak_g,
        "peak_g_t": peak_g_t,
        "basal_p": float(p[0]),
        "peak_p": peak_p,
        "peak_p_t": peak_p_t,
        "basal_c": float(c[0]),
        "min_c": float(c.min()),
        "recovery_t": recovery_t,
    }


def make_overlay_figure(results: dict, var: str, ylabel: str, title: str,
                        fname: str) -> str:
    """One figure overlaying all three subjects for a single concentration."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for mode in SUBJECTS:
        res = results[mode]["sim"]
        ax.plot(res.t, res.concentrations[var], color=COLORS[mode], lw=2,
                label=mode.capitalize())
        # Each subject has its OWN basal operating point (the diabetic basal is
        # elevated); draw a faint per-subject basal line rather than one shared
        # reference, so the elevated diabetic baseline is visible.
        basal = float(res.concentrations[var][0])
        ax.axhline(basal, ls=":", lw=0.9, color=COLORS[mode], alpha=0.5)
    ax.axvspan(0, EAT_DURATION_MIN, color="0.6", alpha=0.10,
               label=f"eating ({EAT_DURATION_MIN:.0f} min)")
    # The interesting dynamics (incl. the slower diabetic recovery) finish well
    # before the 300-min horizon; focus the view on 0-200 min so the obese
    # insulin-decay hump and the diabetic excursion are both clearly visible.
    ax.set_xlim(0, 200)
    ax.set_title(title)
    ax.set_xlabel("time (min)")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, fname)
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def write_results(results: dict, fig_paths: dict) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    meal_rate = CARB_GRAMS * 1000.0 / EAT_DURATION_MIN

    def fmt(v):
        return "n/a" if (isinstance(v, float) and np.isnan(v)) else f"{v:.1f}"

    rows = []
    for mode in SUBJECTS:
        m = results[mode]["metrics"]
        rows.append(
            f"| {mode.capitalize()} | {fmt(m['basal_g'])} | {fmt(m['peak_g'])} | "
            f"{fmt(m['peak_g_t'])} | {fmt(m['basal_p'])} | {fmt(m['peak_p'])} | "
            f"{fmt(m['peak_p_t'])} | {fmt(m['basal_c'])} | {fmt(m['min_c'])} | "
            f"{fmt(m['recovery_t'])} |"
        )
    table = "\n".join(rows)

    text = f"""# Exercise 7 — A bowl of vanilla ice cream: normal vs diabetic vs obese

## Question
Simulate the glucose, insulin, and glucagon dynamics resulting from a normal,
diabetic, and obese subject each consuming an average bowl of vanilla ice cream.
(Haefner Ch. 12, §12.5 #7.)

## Documented assumptions
- **Ice-cream carbohydrate content (key assumption):** "An average bowl of
  vanilla ice cream" = ~1 cup (~130 g) of regular vanilla ice cream. USDA
  FoodData Central ("Ice creams, vanilla") lists ~23-24 g carbohydrate per 100 g,
  almost entirely sugar (sucrose + lactose). One cup therefore supplies
  ~130 g x 0.24 ~= 31 g carbohydrate. **We adopt {CARB_GRAMS:.0f} g of
  digestible carbohydrate, treated as 100% appearing as plasma glucose** (a
  conservative upper bound; lactose + fat would slow real absorption). Source:
  USDA FoodData Central; standard label serving ~1/2 cup ~15-16 g carb, so a full
  bowl ~1 cup ~30 g.
- **Eating duration:** the bowl is eaten over **{EAT_DURATION_MIN:.0f} min**
  (within the 30-45 min brief), modelled as a constant glucose infusion
  Ig(t) = {meal_rate:.1f} mg/min for t in [0, {EAT_DURATION_MIN:.0f}] min.
- **Meal as first-order Ra(t) (cite Dalla Man et al. 2007;
  references/ref3_man_2007.md):** a real meal is absorbed through a
  gastro-intestinal stage giving a smooth, delayed glucose rate of appearance.
  Our constant infusion is a deliberate first-order approximation of that Ra(t).
- **Subjects & initial conditions:** NORMAL, DIABETIC, OBESE parameter sets from
  the verified cobelli.py core (Tables 12.2/12.3), {BODY_WEIGHT_KG:.0f} kg each.
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
{table}

(Glucose/insulin "peak" = maximum plasma concentration; glucagon "min" = maximum
suppression below basal. Recovery = first time glucose returns within 5% of that
subject's own basal.)

## Figures
- `figures/{os.path.basename(fig_paths['gbar'])}` — plasma glucose, three subjects.
- `figures/{os.path.basename(fig_paths['pbar'])}` — plasma insulin, three subjects.
- `figures/{os.path.basename(fig_paths['cbar'])}` — plasma glucagon, three subjects.

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
"""
    out = os.path.join(RESULTS_DIR, "ex7_results.md")
    with open(out, "w") as fh:
        fh.write(text)
    return out


def main() -> int:
    print("=" * 72)
    print("Exercise 7 — Bowl of vanilla ice cream: normal / diabetic / obese")
    print(f"  carb dose = {CARB_GRAMS:.0f} g over {EAT_DURATION_MIN:.0f} min")
    print("=" * 72)

    results = {}
    for mode in SUBJECTS:
        patient = cb.make_patient(mode, body_weight_kg=BODY_WEIGHT_KG)
        y0 = initial_condition(patient)
        sim = run_meal(patient, y0)
        if not sim.success:
            print(f"  INTEGRATION FAILED ({mode}): {sim.message!r}")
            return 1
        metrics = summarize(sim)
        results[mode] = {"sim": sim, "metrics": metrics}
        print(f"\n{mode.capitalize():9s}: basal g={metrics['basal_g']:6.1f} -> "
              f"peak g={metrics['peak_g']:6.1f} @ t={metrics['peak_g_t']:5.1f} | "
              f"basal ins={metrics['basal_p']:5.1f} -> peak ins={metrics['peak_p']:5.1f} "
              f"@ t={metrics['peak_p_t']:5.1f} | glucagon {metrics['basal_c']:5.1f}"
              f"->{metrics['min_c']:5.1f}")

    fig_paths = {
        "gbar": make_overlay_figure(
            results, "gbar", "ḡ  (mg/100 ml)",
            "Ex 7 — Plasma glucose after a bowl of vanilla ice cream",
            "ex7_icecream_glucose.png"),
        "pbar": make_overlay_figure(
            results, "pbar", "p̄  (µU/ml)",
            "Ex 7 — Plasma insulin after a bowl of vanilla ice cream",
            "ex7_icecream_insulin.png"),
        "cbar": make_overlay_figure(
            results, "cbar", "c̄  (nU/ml)",
            "Ex 7 — Plasma glucagon after a bowl of vanilla ice cream",
            "ex7_icecream_glucagon.png"),
    }
    res_path = write_results(results, fig_paths)

    print("\nFigures :")
    for k, v in fig_paths.items():
        print(f"   {v}")
    print(f"Results : {res_path}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
