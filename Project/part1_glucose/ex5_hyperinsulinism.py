"""Exercise 5 - Hyperinsulinism / insulin shock (Haefner Ch. 12, ex. 5).

Part (a): simulate hyperinsulinism by amplifying the insulin-secretion machinery
(the a6 scale in F6, the "promptly releasable" secretion rate) and drive plasma
glucose into the fatal hypoglycemic range. A TERMINAL solve_ivp event "kills" the
patient the instant plasma glucose falls below 20 mg/100 ml. We sweep the a6
multiplier, find the value that drives the untreated patient below 20, and report
the time of death.

Part (b): RESCUE. Starting from a clearly-fatal hyperinsulinism scenario,
administer intravenous glucose (a continuous IV dextrose drip, the textbook's
"short-term treatment") and find by bisection the MINIMUM total glucose dose (in
grams) that keeps plasma glucose >= 20 mg/100 ml for the duration of the crisis.

----------------------------------------------------------------------------
MODELING NOTE (disclosed assumption -- how a6 is scaled into a lethal source)
----------------------------------------------------------------------------
The verified Cobelli core is strongly glucose-buffered: simply raising the a6
scale in F6 does NOT kill the patient. The pancreatic compartments are
donor-controlled and self-limiting -- at steady state d(r+s)/dt = 0 forces the
secretion F6 to equal the synthesis rate W, and the W gate (0.5[1+tanh(bw(Dg+cw))])
*closes* as glucose falls. Endogenous plasma insulin therefore saturates at
~40 uU/ml (x3.6 basal) and plasma glucose merely dips to ~78 mg/100 ml and then
recovers. This is the model's built-in homeostasis and it is correct: a normal
pancreas cannot kill you, which is exactly why clinical insulin shock requires an
*autonomous* insulin source (an insulinoma / exogenous overdose) that does not
shut off when glucose drops -- precisely Guyton's "hyperinsulinism".

We therefore model hyperinsulinism faithfully as an AUTONOMOUS insulinoma: the
hyperactive secretory tissue delivers insulin to plasma at a glucose-INDEPENDENT
rate set by the a6 amplification, on top of the intact native secretion. Tying it
to F6: the autonomous plasma-insulin source is

    Ip_tumor = (a6_multiplier - 1) * F6_basal          [uU/min]

i.e. a multiplier of 1 is the healthy subject (no tumor), and a multiplier of M
means the tumour secretes (M-1)x the basal F6 rate continuously, regardless of
glucose. F6_basal ~ 1.64e4 uU/min is read from the calibrated basal state. This
keeps "increase a6 in F6" as the single control knob, honours the textbook's
"other adjustments may be needed", and is the minimal physiologically-honest
change that produces insulin shock. The native pancreas (and its W=F6 balance,
all tanh shapes, every transfer rate) is left exactly as in Table 12.2.

Run:  python3 ex5_hyperinsulinism.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb

# --- thresholds (Haefner ex.5 text) ---
DEATH_GLUCOSE = 20.0        # mg/100 ml  -> terminal death event
HYPO_GLUCOSE = 70.0         # mg/100 ml  -> hypoglycemia (CNS impairment) line

# --- (a) hyperinsulinism sweep ---
A6_SWEEP = [1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 6.0, 8.0, 10.0]
SWEEP_HORIZON_MIN = 600.0
DEMO_MULT = 8.0             # clearly-fatal multiplier used for the main figures

# --- (b) rescue search ---
RESCUE_WINDOW_MIN = 240.0   # duration of the IV dextrose drip (clinical window)
RESCUE_DOSE_HI_G = 200.0    # bisection upper bound (g)
RESCUE_BISECT_ITERS = 32

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
RES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_death_event(vb: float):
    """solve_ivp terminal event: fires when plasma glucose crosses 20 downward."""
    def death(t, y):
        return y[cb.IDX_G] / vb - DEATH_GLUCOSE

    death.terminal = True
    death.direction = -1.0
    return death


def basal_F6(patient: cb.Patient) -> float:
    """Calibrated basal insulin-secretion rate F6 (uU/min)."""
    y0 = patient.basal_amounts.to_array()
    f0 = cb.compute_fluxes(y0, patient.params, patient.basal_conc,
                           patient.volumes, patient.mode)
    return float(f0.F6)


def tumor_forcing(a6_multiplier: float, f6_basal: float):
    """Autonomous (glucose-independent) plasma-insulin source from the insulinoma.

    Ip_tumor = (a6_multiplier - 1) * F6_basal  uU/min  (constant in time).
    """
    rate = max(a6_multiplier - 1.0, 0.0) * f6_basal

    def Ip(t: float) -> float:
        return rate

    return Ip


def run_hyperinsulinism(patient: cb.Patient, y0: np.ndarray,
                        a6_multiplier: float, horizon: float,
                        Ig=cb.ZERO_FORCING, t_points: int = 3000):
    """Integrate the hyperinsulinism scenario with the terminal death event."""
    f6b = basal_F6(patient)
    Ip = tumor_forcing(a6_multiplier, f6b)
    death = make_death_event(patient.volumes.Vb)
    res = cb.simulate(
        patient, y0, (0.0, horizon),
        Ig=Ig, Ip=Ip,
        t_eval=np.linspace(0.0, horizon, t_points),
        events=[death], max_step=1.0,
    )
    died = bool(res.t_events and len(res.t_events[0]) > 0)
    t_death = float(res.t_events[0][0]) if died else float("nan")
    return res, died, t_death


# ---------------------------------------------------------------------------
# (a) sweep + fatal-decline figure
# ---------------------------------------------------------------------------
def part_a():
    patient = cb.make_patient("normal")
    y0 = patient.basal_amounts.to_array()
    f6b = basal_F6(patient)

    print("=" * 72)
    print("EX 5(a)  HYPERINSULINISM -> insulin shock (terminal death < 20 mg/100ml)")
    print("=" * 72)
    print(f"  basal F6 = {f6b:.4g} uU/min; autonomous source = (mult-1)*F6_basal")
    print(f"  {'a6 mult':>8} {'Ip_tumor(uU/min)':>16} {'min gbar':>9} "
          f"{'died':>6} {'t_death(min)':>12}")

    sweep_rows = []
    threshold_mult = None
    for mult in A6_SWEEP:
        res, died, t_death = run_hyperinsulinism(patient, y0, mult,
                                                 SWEEP_HORIZON_MIN)
        g = res.concentrations["gbar"]
        rate = max(mult - 1.0, 0.0) * f6b
        sweep_rows.append((mult, rate, float(g.min()), died, t_death))
        if died and threshold_mult is None:
            threshold_mult = mult
        print(f"  {mult:8.1f} {rate:16.4g} {g.min():9.2f} "
              f"{str(died):>6} {t_death:12.1f}")

    # Demo fatal trajectory for the figure.
    res_demo, died_demo, t_death_demo = run_hyperinsulinism(
        patient, y0, DEMO_MULT, SWEEP_HORIZON_MIN)
    print(f"\n  demo multiplier {DEMO_MULT:.0f}x: died={died_demo}, "
          f"t_death = {t_death_demo:.1f} min")

    save_fatal_figure(res_demo, t_death_demo, DEMO_MULT)
    return {
        "threshold_mult": threshold_mult,
        "sweep_rows": sweep_rows,
        "demo_mult": DEMO_MULT,
        "demo_t_death": t_death_demo,
        "f6_basal": f6b,
    }


def save_fatal_figure(res, t_death, mult):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(FIG_DIR, exist_ok=True)
    t = res.t
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

    ax = axes[0]
    ax.plot(t, res.concentrations["gbar"], color="#c0392b", lw=2.2,
            label="plasma glucose")
    ax.axhline(HYPO_GLUCOSE, ls="--", lw=1.3, color="#e67e22",
               label=f"hypoglycemia {HYPO_GLUCOSE:.0f}")
    ax.axhline(DEATH_GLUCOSE, ls="-.", lw=1.6, color="black",
               label=f"death {DEATH_GLUCOSE:.0f}")
    if np.isfinite(t_death):
        ax.axvline(t_death, ls=":", lw=1.6, color="#c0392b")
        ax.annotate(f"death\nt = {t_death:.1f} min",
                    xy=(t_death, DEATH_GLUCOSE),
                    xytext=(t_death + 0.08 * t[-1], 45),
                    arrowprops=dict(arrowstyle="->", color="#c0392b"),
                    color="#c0392b", fontsize=10)
    ax.set_ylim(0, 110)
    ax.set_title(f"Fatal hypoglycemic decline  (a6 x {mult:.0f}, autonomous)")
    ax.set_xlabel("time (min)")
    ax.set_ylabel(r"$\bar g$  (mg/100 ml)")
    ax.legend(loc="upper right", fontsize=9)

    ax = axes[1]
    ax.plot(t, res.concentrations["pbar"], color="#2471a3", lw=2.2)
    ax.axhline(res.concentrations["pbar"][0], ls="--", lw=1, color="0.5",
               label=f"basal {res.concentrations['pbar'][0]:.0f}")
    if np.isfinite(t_death):
        ax.axvline(t_death, ls=":", lw=1.6, color="#c0392b")
    ax.set_title("Plasma insulin (autonomous oversecretion)")
    ax.set_xlabel("time (min)")
    ax.set_ylabel(r"$\bar p$  ($\mu$U/ml)")
    ax.legend(loc="upper right", fontsize=9)

    fig.suptitle("Ex 5(a)  Hyperinsulinism / insulin shock  (Cobelli model, 70-kg normal)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(FIG_DIR, "ex5_fatal_decline.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  figure saved: {out}")
    return out


# ---------------------------------------------------------------------------
# (b) rescue dose search
# ---------------------------------------------------------------------------
def survives_with_dose(patient, y0, mult, dose_g):
    """True if a sustained IV glucose drip of dose_g grams (spread over the
    rescue window) keeps glucose >= 20 for the whole window."""
    dose_mg = dose_g * 1000.0
    Ig = cb.make_rectangular_pulse(dose_mg, 0.0, RESCUE_WINDOW_MIN)
    res, died, t_death = run_hyperinsulinism(
        patient, y0, mult, RESCUE_WINDOW_MIN, Ig=Ig, t_points=2000)
    return (not died), res, t_death


def part_b(threshold_info):
    patient = cb.make_patient("normal")
    y0 = patient.basal_amounts.to_array()
    mult = DEMO_MULT

    print("\n" + "=" * 72)
    print("EX 5(b)  RESCUE with IV glucose -> minimum dose to prevent death")
    print("=" * 72)
    print(f"  scenario: a6 x {mult:.0f} (untreated t_death = "
          f"{threshold_info['demo_t_death']:.1f} min)")
    print(f"  rescue   : continuous IV dextrose drip over "
          f"{RESCUE_WINDOW_MIN:.0f} min; bisection on total grams")

    # Confirm zero-dose dies.
    survives0, _, _ = survives_with_dose(patient, y0, mult, 0.0)
    print(f"  no rescue (0 g): survives={survives0}")

    lo, hi = 0.0, RESCUE_DOSE_HI_G
    for _ in range(RESCUE_BISECT_ITERS):
        mid = 0.5 * (lo + hi)
        surv, _, _ = survives_with_dose(patient, y0, mult, mid)
        if surv:
            hi = mid
        else:
            lo = mid
    min_dose_g = hi
    print(f"  MINIMUM rescue dose = {min_dose_g:.2f} g "
          f"(over {RESCUE_WINDOW_MIN:.0f} min)")

    # Trajectories for the figure: un-rescued vs just-rescued.
    _, res_norescue, t_death_nr = survives_with_dose(patient, y0, mult, 0.0)
    surv_r, res_rescue, _ = survives_with_dose(patient, y0, mult, min_dose_g)
    print(f"  rescued at {min_dose_g:.1f} g: survives={surv_r}, "
          f"min gbar = {res_rescue.concentrations['gbar'].min():.2f}")

    save_rescue_figure(res_norescue, res_rescue, t_death_nr, min_dose_g, mult)
    return {"min_dose_g": min_dose_g, "window_min": RESCUE_WINDOW_MIN,
            "t_death_untreated": t_death_nr}


def save_rescue_figure(res_nr, res_r, t_death_nr, dose_g, mult):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 5.0))

    ax.plot(res_nr.t, res_nr.concentrations["gbar"], color="#c0392b", lw=2.2,
            label="un-rescued (dies)")
    ax.plot(res_r.t, res_r.concentrations["gbar"], color="#1e8449", lw=2.2,
            label=f"rescued: {dose_g:.0f} g IV glucose (survives)")
    ax.axhline(HYPO_GLUCOSE, ls="--", lw=1.3, color="#e67e22",
               label=f"hypoglycemia {HYPO_GLUCOSE:.0f}")
    ax.axhline(DEATH_GLUCOSE, ls="-.", lw=1.6, color="black",
               label=f"death {DEATH_GLUCOSE:.0f}")
    if np.isfinite(t_death_nr):
        ax.axvline(t_death_nr, ls=":", lw=1.4, color="#c0392b")
        ax.annotate(f"death t={t_death_nr:.1f}", xy=(t_death_nr, DEATH_GLUCOSE),
                    xytext=(t_death_nr + 20, 40),
                    arrowprops=dict(arrowstyle="->", color="#c0392b"),
                    color="#c0392b", fontsize=10)
    ax.set_ylim(0, 110)
    ax.set_xlabel("time (min)")
    ax.set_ylabel(r"$\bar g$  (mg/100 ml)")
    ax.set_title(f"Ex 5(b)  IV-glucose rescue of insulin shock  (a6 x {mult:.0f})")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    out = os.path.join(FIG_DIR, "ex5_rescue.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  figure saved: {out}")
    return out


# ---------------------------------------------------------------------------
# Results markdown
# ---------------------------------------------------------------------------
def write_results(info_a, info_b):
    os.makedirs(RES_DIR, exist_ok=True)
    rows = "\n".join(
        f"| {m:.1f} | {rate:.4g} | {mn:.2f} | {'yes' if d else 'no'} | "
        f"{(f'{td:.1f}' if np.isfinite(td) else '-')} |"
        for (m, rate, mn, d, td) in info_a["sweep_rows"]
    )
    thr = info_a["threshold_mult"]
    thr_str = f"{thr:.1f}x" if thr is not None else "not reached in sweep"

    md = f"""# Exercise 5 - Hyperinsulinism / insulin shock - Results

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

> `Ip_tumor = (a6_multiplier - 1) * F6_basal`   uU/min,   F6_basal = {info_a['f6_basal']:.4g} uU/min

A multiplier of 1 is the healthy subject; multiplier M means the tumour secretes
(M-1)x basal F6 continuously. The native pancreas (W=F6 balance, all tanh shapes,
all transfer rates) is unchanged. The terminal death event is a solve_ivp
terminal event on `gbar - 20` with downward direction.

## (a) Fatal hyperinsulinism

| a6 mult | Ip_tumor (uU/min) | min gbar (mg/100ml) | died | t_death (min) |
|--------:|------------------:|--------------------:|:----:|--------------:|
{rows}

- **Lethal threshold (first fatal multiplier in the sweep): {thr_str}.**
- Below the threshold the autonomous insulin is not enough to overwhelm hepatic
  output + falling peripheral uptake, and glucose stabilises above 20.
- **Demo scenario a6 x {info_a['demo_mult']:.0f}: death at
  t = {info_a['demo_t_death']:.1f} min.**
- Figure: `figures/ex5_fatal_decline.png` (glucose driven through the 70 and 20
  mg/100 ml lines; insulin rises far above basal).

## (b) IV-glucose rescue
Starting from the clearly-fatal a6 x {DEMO_MULT:.0f} scenario
(untreated death at t = {info_b['t_death_untreated']:.1f} min), a continuous IV
dextrose drip is given over a **{info_b['window_min']:.0f}-min** clinical window
and the total grams is found by bisection (keep gbar >= 20 for the whole window).

- **Minimum rescue dose = {info_b['min_dose_g']:.2f} g** of glucose over
  {info_b['window_min']:.0f} min.
- Below this the nadir still crosses 20 and the patient dies; at/above it the
  glucose floor is held at 20 and the patient survives the window.
- Figure: `figures/ex5_rescue.png` (un-rescued death vs rescued survival).

### Assumption for the rescue dose
Because the modelled insulinoma is permanent, IV glucose is *temporizing*, not
curative (clinically the tumour must be removed) - exactly the textbook's
"short-term treatment = large IV glucose". The minimum dose is therefore quoted
for a defined clinical window (a continuous drip over
{info_b['window_min']:.0f} min); a longer window needs proportionally more
glucose. This is reported as an explicit assumption rather than an unconditional
"grams to survive forever", which is undefined for a permanent source.

## Figures
- `figures/ex5_fatal_decline.png`
- `figures/ex5_rescue.png`
"""
    out = os.path.join(RES_DIR, "ex5_results.md")
    with open(out, "w") as fh:
        fh.write(md)
    print(f"\n  results written: {out}")
    return out


def main():
    info_a = part_a()
    info_b = part_b(info_a)
    write_results(info_a, info_b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
