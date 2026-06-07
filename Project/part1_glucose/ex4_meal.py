"""Part 1, Exercise 4 — Meal as a 60-min glucose infusion vs an IVGTT pulse.

Exercise text (Haefner Ch. 12, §12.5 #4):
    Simulate the glucose infusion diagnostic test by adding glucose NOT as a
    pulse (IVGTT) but as a constant input spread over 60 minutes (a meal).
    Administer 25 g to a 70-kg subject over 60 minutes. Plot plasma glucose &
    insulin. How do these dynamics compare to the IVGTT? Explain in terms of
    model mechanisms.

Approach (uses the verified cobelli.py core unchanged):
  * MEAL  : 25 g delivered as a constant infusion over t in [0, 60] min, i.e.
            25000 mg / 60 min = 416.67 mg/min (first-order approximation of an
            oral meal; see note below and ref3_man_2007.md).
  * IVGTT : the SAME total 25 g delivered as a short ~2-min rectangular bolus,
            so the only difference is the *temporal spread* of the input.

Both start from the NORMAL patient's clinical basal steady state and are
integrated over 0-180 min, then overlaid for comparison.

NOTE (oral meal vs constant infusion; cite Dalla Man, Rizza & Cobelli 2007,
references/ref3_man_2007.md): a real oral meal is not a constant glucose influx.
It passes through a gastro-intestinal absorption stage (stomach -> gut -> plasma)
with nonlinear gastric emptying, producing a smooth, delayed, time-varying
glucose rate of appearance Ra(t) that rises, peaks, then decays. Our constant
60-min infusion is a deliberate first-order approximation of that Ra(t): it
captures the key qualitative difference from an IV bolus (gradual appearance)
without implementing the full 2007 GI submodel, which the exercise does not ask
for.

Run:  python3 ex4_meal.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb

# --- Protocol constants -----------------------------------------------------
MEAL_DOSE_G = 25.0            # g of glucose (same total for meal and IVGTT)
MEAL_DURATION_MIN = 60.0      # meal spread uniformly over 60 min
IVGTT_DURATION_MIN = 2.0      # IV bolus delivered over ~2 min (short pulse)
BODY_WEIGHT_KG = 70.0
SIM_DURATION_MIN = 180.0      # 0-180 min observation horizon
N_EVAL = 900                  # output resolution
RECOVERY_BAND_FRAC = 0.05     # "recovered" = within 5% of basal glucose

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(THIS_DIR, "figures")
RESULTS_DIR = os.path.join(THIS_DIR, "results")


def run_protocol(patient: cb.Patient, y0: np.ndarray, dose_g: float,
                 duration: float):
    """Integrate the model with `dose_g` grams of glucose spread over
    `duration` minutes starting at t=0. Returns the SimResult."""
    dose_mg = dose_g * 1000.0
    forcing = cb.make_rectangular_pulse(dose_mg, t_start=0.0, duration=duration)
    t_eval = np.linspace(0.0, SIM_DURATION_MIN, N_EVAL)
    # Make sure the solver does not step over the (short) input window.
    return cb.simulate(
        patient,
        y0,
        (0.0, SIM_DURATION_MIN),
        Ig=forcing,
        t_eval=t_eval,
        method="LSODA",
        pulse_times=[0.0, duration],
        max_step=min(duration / 4.0, 0.5),
    )


def summarize(res: cb.SimResult) -> dict:
    """Peak/time-to-peak/recovery metrics for glucose and insulin."""
    t = res.t
    g = res.concentrations["gbar"]
    p = res.concentrations["pbar"]
    basal_g = float(g[0])

    peak_g = float(g.max())
    peak_g_t = float(t[int(g.argmax())])
    peak_p = float(p.max())
    peak_p_t = float(t[int(p.argmax())])

    # recovery: first time after the glucose peak within 5% of basal
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
        "recovery_t": recovery_t,
    }


def make_figure(t, meal: cb.SimResult, ivgtt: cb.SimResult,
                m_meal: dict, m_ivgtt: dict) -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(FIG_DIR, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))

    meal_c = "#c0392b"
    ivg_c = "#2471a3"

    # --- glucose ---
    ax = axes[0]
    ax.plot(t, ivgtt.concentrations["gbar"], color=ivg_c, lw=2,
            label=f"IVGTT pulse ({IVGTT_DURATION_MIN:.0f} min)")
    ax.plot(t, meal.concentrations["gbar"], color=meal_c, lw=2,
            label=f"Meal infusion ({MEAL_DURATION_MIN:.0f} min)")
    ax.axhline(m_meal["basal_g"], ls="--", lw=1, color="0.5", label="basal")
    ax.axvspan(0, MEAL_DURATION_MIN, color=meal_c, alpha=0.06)
    ax.set_title("Plasma glucose")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("ḡ  (mg/100 ml)")
    ax.legend(fontsize=8)

    # --- insulin ---
    ax = axes[1]
    ax.plot(t, ivgtt.concentrations["pbar"], color=ivg_c, lw=2, label="IVGTT pulse")
    ax.plot(t, meal.concentrations["pbar"], color=meal_c, lw=2, label="Meal infusion")
    ax.axhline(m_meal["basal_p"], ls="--", lw=1, color="0.5", label="basal")
    ax.axvspan(0, MEAL_DURATION_MIN, color=meal_c, alpha=0.06)
    ax.set_title("Plasma insulin")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("p̄  (µU/ml)")
    ax.legend(fontsize=8)

    # --- glucose input rate (shows the protocol difference) ---
    ax = axes[2]
    meal_rate = MEAL_DOSE_G * 1000.0 / MEAL_DURATION_MIN
    ivg_rate = MEAL_DOSE_G * 1000.0 / IVGTT_DURATION_MIN
    tt = np.linspace(0, SIM_DURATION_MIN, N_EVAL)
    rate_meal = np.where(tt < MEAL_DURATION_MIN, meal_rate, 0.0)
    rate_ivg = np.where(tt < IVGTT_DURATION_MIN, ivg_rate, 0.0)
    ax.plot(tt, rate_ivg, color=ivg_c, lw=2,
            label=f"IVGTT ({ivg_rate:.0f} mg/min)")
    ax.plot(tt, rate_meal, color=meal_c, lw=2,
            label=f"Meal ({meal_rate:.0f} mg/min)")
    ax.set_title("Glucose input rate Ig(t)  (same 25 g total)")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("Ig  (mg/min)")
    ax.set_xlim(0, 75)
    ax.legend(fontsize=8)

    fig.suptitle(
        f"Ex 4 — Meal (60-min infusion) vs IVGTT (2-min pulse): "
        f"same {MEAL_DOSE_G:.0f} g to a {BODY_WEIGHT_KG:.0f}-kg subject",
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(FIG_DIR, "ex4_meal_vs_ivgtt.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def write_results(m_meal: dict, m_ivgtt: dict, fig_path: str) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    meal_rate = MEAL_DOSE_G * 1000.0 / MEAL_DURATION_MIN
    fig_name = os.path.basename(fig_path)

    def g(d, k):
        v = d[k]
        return "n/a" if (isinstance(v, float) and np.isnan(v)) else f"{v:.1f}"

    text = f"""# Exercise 4 — Meal (60-min glucose infusion) vs IVGTT pulse

## Question
Simulate the glucose infusion diagnostic test by adding glucose NOT as an
instantaneous IVGTT pulse but as a constant input spread over 60 minutes (a
meal): administer {MEAL_DOSE_G:.0f} g of glucose to a {BODY_WEIGHT_KG:.0f}-kg
subject over {MEAL_DURATION_MIN:.0f} minutes. Plot plasma glucose and insulin
over 0-{SIM_DURATION_MIN:.0f} min, compare against an IVGTT delivering the SAME
total dose as a short pulse, and explain the differences in terms of model
mechanisms. (Haefner Ch. 12, §12.5 #4.)

## Documented assumptions
- **Subject:** NORMAL patient, {BODY_WEIGHT_KG:.0f} kg, started from the
  clinical basal steady state (gbar = 91.5 mg/100 ml, pbar = 11 µU/ml). The
  same calibrated core model verified against Fig 12.4 is used unchanged.
- **Meal forcing:** {MEAL_DOSE_G:.0f} g = {MEAL_DOSE_G*1000:.0f} mg delivered as
  a *constant* glucose infusion Ig(t) = {meal_rate:.1f} mg/min for
  t in [0, {MEAL_DURATION_MIN:.0f}] min, 0 afterwards (rectangular pulse).
- **IVGTT comparison:** identical total {MEAL_DOSE_G:.0f} g delivered over a
  short {IVGTT_DURATION_MIN:.0f}-min rectangular bolus
  (Ig = {MEAL_DOSE_G*1000.0/IVGTT_DURATION_MIN:.0f} mg/min), so the ONLY
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
| Peak plasma glucose (mg/100 ml) | {g(m_meal,'peak_g')} | {g(m_ivgtt,'peak_g')} |
| Time-to-peak glucose (min) | {g(m_meal,'peak_g_t')} | {g(m_ivgtt,'peak_g_t')} |
| Peak plasma insulin (µU/ml) | {g(m_meal,'peak_p')} | {g(m_ivgtt,'peak_p')} |
| Time-to-peak insulin (min) | {g(m_meal,'peak_p_t')} | {g(m_ivgtt,'peak_p_t')} |
| Glucose recovery (within 5% basal, min) | {g(m_meal,'recovery_t')} | {g(m_ivgtt,'recovery_t')} |

Basal reference: glucose {m_meal['basal_g']:.1f} mg/100 ml,
insulin {m_meal['basal_p']:.1f} µU/ml.

## Figure
- `figures/{fig_name}` — three panels: plasma glucose (overlay), plasma insulin
  (overlay), and the glucose input rate Ig(t) showing the two protocols deliver
  the same 25 g total but with very different temporal spread.

## Discussion (grounded in the output)
**Glucose peak height and timing.** The IVGTT dumps all {MEAL_DOSE_G:.0f} g into
the glucose pool within {IVGTT_DURATION_MIN:.0f} min, faster than any clearance
flux can respond, so glucose spikes to {g(m_ivgtt,'peak_g')} mg/100 ml almost
immediately (t ~= {g(m_ivgtt,'peak_g_t')} min). The meal delivers the identical
mass at only {meal_rate:.0f} mg/min, slow enough that the clearance fluxes
(renal F3, peripheral F4, CNS/RBC F5) and the suppression of hepatic production
remove glucose *as it arrives*. The result is a much lower, broader glucose
excursion peaking at {g(m_meal,'peak_g')} mg/100 ml near the end of the infusion
window (t ~= {g(m_meal,'peak_g_t')} min). Same dose, very different peak.

**Insulin response.** In the Cobelli model insulin secretion is gated by the
standardized glucose deviation Δḡ through the W (synthesis) and F6 (release)
tanh gates, with F6 drawing on the finite releasable pool r. Both protocols show
an early first-phase peak as r is secreted, but the meal peak
({g(m_meal,'peak_p')} µU/ml) is blunted relative to the sharp IVGTT spike
({g(m_ivgtt,'peak_p')} µU/ml) because the gentler glucose rise opens the
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
"""
    out = os.path.join(RESULTS_DIR, "ex4_results.md")
    with open(out, "w") as fh:
        fh.write(text)
    return out


def main() -> int:
    print("=" * 72)
    print("Exercise 4 — Meal (60-min infusion) vs IVGTT pulse")
    print("=" * 72)

    patient = cb.make_patient("normal", body_weight_kg=BODY_WEIGHT_KG)
    y0 = patient.basal_amounts.to_array()  # normal: clinical basal is steady

    meal = run_protocol(patient, y0, MEAL_DOSE_G, MEAL_DURATION_MIN)
    ivgtt = run_protocol(patient, y0, MEAL_DOSE_G, IVGTT_DURATION_MIN)
    if not (meal.success and ivgtt.success):
        print(f"  INTEGRATION FAILED: meal={meal.message!r}, ivgtt={ivgtt.message!r}")
        return 1

    m_meal = summarize(meal)
    m_ivgtt = summarize(ivgtt)

    print(f"\nMeal  : peak glucose {m_meal['peak_g']:.1f} mg/100ml @ "
          f"t={m_meal['peak_g_t']:.1f} min; peak insulin {m_meal['peak_p']:.1f} "
          f"µU/ml @ t={m_meal['peak_p_t']:.1f} min")
    print(f"IVGTT : peak glucose {m_ivgtt['peak_g']:.1f} mg/100ml @ "
          f"t={m_ivgtt['peak_g_t']:.1f} min; peak insulin {m_ivgtt['peak_p']:.1f} "
          f"µU/ml @ t={m_ivgtt['peak_p_t']:.1f} min")

    fig_path = make_figure(meal.t, meal, ivgtt, m_meal, m_ivgtt)
    res_path = write_results(m_meal, m_ivgtt, fig_path)
    print(f"\nFigure  : {fig_path}")
    print(f"Results : {res_path}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
