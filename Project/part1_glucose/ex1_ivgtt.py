"""Exercise 1 -- Normal IVGTT: reproduce Fig 12.4a/b, plot glucagon and liver
glucose-uptake (F2), and answer "where does the majority of glucose go?".

Protocol: a NORMAL 70-kg subject receives a single intravenous glucose bolus
(standard IVGTT, 0.33 g/kg over 2 min) from the calibrated basal steady state.

Produces (figures/):
  ex1_glucose.png       plasma glucose  (Fig 12.4a)
  ex1_insulin.png       plasma / liver / interstitial insulin  (Fig 12.4b)
  ex1_glucagon_F2.png   plasma glucagon  +  hepatic glucose uptake F2
  ex1_disposal_split.png cumulative glucose-disposal fluxes + % split

Writes results/ex1_results.md with the disposal % split and discussion.

Run:  python3 ex1_ivgtt.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb
import ex_common as ec

# --- Protocol constants ---
IVGTT_DOSE_G_PER_KG = 0.33     # standard IVGTT bolus 0.3-0.33 g/kg
BOLUS_DURATION_MIN = 2.0
SIM_DURATION_MIN = 150.0       # observation window (covers full recovery)


def build_patient_and_ic():
    patient = cb.make_patient("normal")
    y0 = patient.basal_amounts.to_array()  # calibrated basal IS a steady state
    return patient, y0


def run_ex1():
    patient, y0 = build_patient_and_ic()
    dose_g = IVGTT_DOSE_G_PER_KG * patient.body_weight_kg
    forcing = ec.single_ivgtt_forcing(dose_g, t_start=0.0, duration=BOLUS_DURATION_MIN)
    res = ec.run(
        patient,
        y0,
        SIM_DURATION_MIN,
        Ig=forcing,
        pulse_times=[0.0, BOLUS_DURATION_MIN],
        max_step=0.5,
    )
    return patient, res, dose_g


def disposal_split(res: cb.SimResult):
    """Integrate the glucose-disposal fluxes over the IVGTT response.

    Sinks in Eq 12.1: dg/dt = NHGB - F3 - F4 - F5 + Ig.
    The disposal channels are F3 (renal), F4 (muscle/adipose), F5 (CNS/RBC).
    NHGB is the *net* hepatic balance (production - uptake); when it is a net
    sink (negative) the liver also disposes glucose. We report cumulative
    integrals (in mg, using the true mg/min fluxes) and the % split of the
    total glucose actually removed.
    """
    t = res.t
    F3 = res.fluxes["F3_mgmin"]
    F4 = res.fluxes["F4_mgmin"]
    F5 = res.fluxes["F5_mgmin"]
    NHGB = res.fluxes["NHGB_mgmin"]

    cum_F3 = ec.cumulative_trapz(F3, t)
    cum_F4 = ec.cumulative_trapz(F4, t)
    cum_F5 = ec.cumulative_trapz(F5, t)
    cum_NHGB = ec.cumulative_trapz(NHGB, t)  # net hepatic balance (signed)

    int_F3 = ec.total_integral(F3, t)
    int_F4 = ec.total_integral(F4, t)
    int_F5 = ec.total_integral(F5, t)
    int_NHGB = ec.total_integral(NHGB, t)

    # Total glucose disposal over the window = renal + muscle/adipose + CNS/RBC
    # minus net hepatic balance (NHGB>0 adds glucose, so it subtracts from net
    # removal). We report the % split among the three peripheral sinks (the
    # exercise's "where does glucose go") and separately the net hepatic term.
    sink_total = int_F3 + int_F4 + int_F5
    pct_F3 = 100.0 * int_F3 / sink_total
    pct_F4 = 100.0 * int_F4 / sink_total
    pct_F5 = 100.0 * int_F5 / sink_total

    return {
        "t": t,
        "cum_F3": cum_F3,
        "cum_F4": cum_F4,
        "cum_F5": cum_F5,
        "cum_NHGB": cum_NHGB,
        "int_F3": int_F3,
        "int_F4": int_F4,
        "int_F5": int_F5,
        "int_NHGB": int_NHGB,
        "sink_total": sink_total,
        "pct_F3": pct_F3,
        "pct_F4": pct_F4,
        "pct_F5": pct_F5,
    }


def metrics(res: cb.SimResult):
    g = res.concentrations["gbar"]
    p = res.concentrations["pbar"]
    c = res.concentrations["cbar"]
    peak_t = float(res.t[int(g.argmax())])
    after = res.t > peak_t
    band = g[0] * 1.05
    rec = res.t[after][g[after] <= band]
    return {
        "basal_g": float(g[0]),
        "peak_g": float(g.max()),
        "peak_t": peak_t,
        "recovery_t": float(rec[0]) if rec.size else float("nan"),
        "insulin_basal": float(p[0]),
        "insulin_peak": float(p.max()),
        "glucagon_basal": float(c[0]),
        "glucagon_min": float(c.min()),
    }


def make_figures(patient, res, dose_g, split, m):
    plt = ec.setup_matplotlib()
    ec.ensure_dirs()
    t = res.t
    figs = {}

    # --- Fig 12.4a : plasma glucose ---
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.plot(t, res.concentrations["gbar"], color="#c0392b", lw=2.2, label="plasma glucose ḡ")
    ax.axhline(m["basal_g"], ls="--", lw=1, color="0.5", label=f"basal {m['basal_g']:.1f}")
    if np.isfinite(m["recovery_t"]):
        ax.axvline(m["recovery_t"], ls=":", lw=1.2, color="#c0392b",
                   label=f"recovery {m['recovery_t']:.0f} min")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("plasma glucose  (mg/100 ml)")
    ax.set_title(f"Ex1 — Normal IVGTT plasma glucose (Fig 12.4a)\n"
                 f"dose {dose_g:.1f} g over {BOLUS_DURATION_MIN:.0f} min, "
                 f"peak {m['peak_g']:.0f} mg/100 ml @ t={m['peak_t']:.0f} min")
    ax.legend()
    fig.tight_layout()
    out = os.path.join(ec.FIG_DIR, "ex1_glucose.png")
    fig.savefig(out); plt.close(fig); figs["glucose"] = out

    # --- Fig 12.4b : plasma / liver / interstitial insulin ---
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.plot(t, res.concentrations["pbar"], color="#2471a3", lw=2.2, label="plasma p̄")
    ax.plot(t, res.concentrations["lbar"], color="#8e44ad", lw=2.0, ls="--", label="liver l̄")
    ax.plot(t, res.concentrations["ibar"], color="#16a085", lw=2.0, ls="-.", label="interstitial ī")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("insulin concentration  (µU/ml)")
    ax.set_title(f"Ex1 — Insulin compartments (Fig 12.4b)\n"
                 f"plasma peak {m['insulin_peak']:.0f} µU/ml (basal {m['insulin_basal']:.0f})")
    ax.legend()
    fig.tight_layout()
    out = os.path.join(ec.FIG_DIR, "ex1_insulin.png")
    fig.savefig(out); plt.close(fig); figs["insulin"] = out

    # --- Glucagon + hepatic glucose uptake F2 ---
    fig, (axc, axf) = plt.subplots(1, 2, figsize=(12, 4.4))
    axc.plot(t, res.concentrations["cbar"], color="#1e8449", lw=2.2)
    axc.axhline(m["glucagon_basal"], ls="--", lw=1, color="0.5",
                label=f"basal {m['glucagon_basal']:.0f}")
    axc.set_xlabel("time (min)")
    axc.set_ylabel("plasma glucagon  (nU/ml)")
    axc.set_title(f"Plasma glucagon (dips to {m['glucagon_min']:.0f} nU/ml)")
    axc.legend()

    axf.plot(t, res.fluxes["F2_mgmin"], color="#d35400", lw=2.2)
    axf.set_xlabel("time (min)")
    axf.set_ylabel("liver glucose uptake F2  (mg/min)")
    axf.set_title("Hepatic glucose uptake rate F2")
    fig.suptitle("Ex1 — Glucagon concentration & liver glucose-uptake rate F2", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(ec.FIG_DIR, "ex1_glucagon_F2.png")
    fig.savefig(out); plt.close(fig); figs["glucagon_F2"] = out

    # --- Cumulative disposal split ---
    fig, (axr, axb) = plt.subplots(1, 2, figsize=(12, 4.6))
    axr.plot(t, split["cum_F4"], color="#2471a3", lw=2.2, label="∫F4 muscle/adipose")
    axr.plot(t, split["cum_F5"], color="#27ae60", lw=2.2, label="∫F5 CNS/RBC")
    axr.plot(t, split["cum_F3"], color="#c0392b", lw=2.2, label="∫F3 renal")
    axr.plot(t, split["cum_NHGB"], color="#7f8c8d", lw=1.8, ls="--", label="∫NHGB (net hepatic)")
    axr.set_xlabel("time (min)")
    axr.set_ylabel("cumulative glucose (mg)")
    axr.set_title("Cumulative glucose-disposal fluxes")
    axr.legend()

    labels = ["F4\nmuscle/adipose", "F5\nCNS/RBC", "F3\nrenal"]
    vals = [split["pct_F4"], split["pct_F5"], split["pct_F3"]]
    colors = ["#2471a3", "#27ae60", "#c0392b"]
    bars = axb.bar(labels, vals, color=colors)
    axb.set_ylabel("% of total peripheral disposal")
    axb.set_title("Where does the glucose go? (% split of F3+F4+F5)")
    for b, v in zip(bars, vals):
        axb.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%",
                 ha="center", va="bottom", fontsize=10)
    axb.set_ylim(0, max(vals) * 1.2)
    fig.suptitle("Ex1 — Glucose disposal over the IVGTT response", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(ec.FIG_DIR, "ex1_disposal_split.png")
    fig.savefig(out); plt.close(fig); figs["disposal"] = out

    return figs


def write_results(patient, res, dose_g, split, m, figs):
    ec.ensure_dirs()
    path = os.path.join(ec.RESULTS_DIR, "ex1_results.md")
    lines = []
    A = lines.append
    A("# Exercise 1 — Normal IVGTT (reproduce Fig 12.4a/b)\n")
    A("**Question.** Code the Cobelli glucose-regulation model and reproduce "
      "Figs 12.4a (plasma glucose) and 12.4b (plasma/liver/interstitial "
      "insulin). Also plot glucagon concentration and the liver glucose-uptake "
      "rate F2. Discuss in light of the Forrester diagram, and answer: **where "
      "does the majority of glucose go?**\n")
    A("**Protocol.** NORMAL 70-kg subject, single IV glucose bolus "
      f"{IVGTT_DOSE_G_PER_KG} g/kg = **{dose_g:.1f} g** delivered over "
      f"{BOLUS_DURATION_MIN:.0f} min, integrated from the calibrated basal "
      "steady state for "f"{SIM_DURATION_MIN:.0f} min (LSODA).\n")

    A("## Key numeric results\n")
    A(f"- Plasma glucose: basal **{m['basal_g']:.1f}** -> peak "
      f"**{m['peak_g']:.0f} mg/100 ml** @ t={m['peak_t']:.0f} min; "
      f"recovery (within 5% of basal) at t = **{m['recovery_t']:.0f} min** "
      "(Fig 12.4 quotes ~90 min).")
    A(f"- Plasma insulin: basal **{m['insulin_basal']:.0f}** -> peak "
      f"**{m['insulin_peak']:.0f} µU/ml** (rises within minutes of the bolus).")
    A(f"- Plasma glucagon: basal **{m['glucagon_basal']:.0f}** -> dips to "
      f"**{m['glucagon_min']:.0f} nU/ml** (suppressed by the glucose+insulin rise).")
    A("")

    A("## Where does the majority of glucose go? (cumulative flux integrals)\n")
    A("Integrating the glucose-disposal fluxes (true mg/min) over the "
      f"{SIM_DURATION_MIN:.0f}-min response:\n")
    A(f"| Sink | Cumulative (mg) | % of peripheral disposal |")
    A(f"|------|-----------------|--------------------------|")
    A(f"| F4 muscle / adipose | {split['int_F4']:.0f} | **{split['pct_F4']:.1f}%** |")
    A(f"| F5 CNS / RBC        | {split['int_F5']:.0f} | **{split['pct_F5']:.1f}%** |")
    A(f"| F3 renal            | {split['int_F3']:.0f} | **{split['pct_F3']:.1f}%** |")
    A(f"| (∫NHGB net hepatic balance, signed) | {split['int_NHGB']:.0f} | — |")
    A("")
    A(f"Total peripheral disposal (F3+F4+F5) = **{split['sink_total']:.0f} mg** "
      "over the window. The net hepatic balance ∫NHGB = "
      f"{split['int_NHGB']:.0f} mg (sign: positive = the liver is a net glucose "
      "*source* on balance over the window; negative = net sink).\n")

    # Pick the dominant sink for the prose answer.
    pairs = [("muscle/adipose tissue (F4)", split["pct_F4"]),
             ("CNS + red blood cells (F5)", split["pct_F5"]),
             ("renal excretion (F3)", split["pct_F3"])]
    pairs.sort(key=lambda x: -x[1])
    A(f"**Answer:** the majority of disposed glucose goes to "
      f"**{pairs[0][0]} ({pairs[0][1]:.1f}%)**, followed by {pairs[1][0]} "
      f"({pairs[1][1]:.1f}%); {pairs[2][0]} is {pairs[2][1]:.1f}%.\n")

    A("## Discussion (Forrester diagram)\n")
    A("- The bolus drives plasma glucose up; the rise immediately stimulates "
      "the pancreatic releasable pool to secrete insulin (F6 ∝ r), so plasma, "
      "liver and interstitial insulin all climb within minutes (Fig 12.4b).")
    A("- High glucose + rising insulin suppress glucagon secretion (F7 uses two "
      "inhibitory −tanh gates), so glucagon dips sharply, as seen.")
    A("- In the Forrester diagram the dominant glucose-clearing compartments "
      "are the insulin-sensitive peripheral tissues (F4, muscle+adipose) and "
      "the large, nearly insulin-independent CNS/RBC sink (F5). Renal loss (F3) "
      "stays near zero unless ḡ exceeds the ~180 mg/100 ml renal threshold; "
      f"here the peak is {m['peak_g']:.0f} mg/100 ml, so F3 contributes "
      f"only {split['pct_F3']:.1f}%.")
    A("- Insulin acts on the liver (F1/F2 via liver insulin) and on peripheral "
      "tissue (F4 via interstitial insulin); the net hepatic balance NHGB swings "
      "from a basal source toward uptake as liver insulin rises, helping clear "
      "the load.")
    A("")

    A("## Figures\n")
    A(f"- `{os.path.basename(figs['glucose'])}` — plasma glucose (Fig 12.4a)")
    A(f"- `{os.path.basename(figs['insulin'])}` — plasma/liver/interstitial insulin (Fig 12.4b)")
    A(f"- `{os.path.basename(figs['glucagon_F2'])}` — glucagon concentration & liver uptake F2")
    A(f"- `{os.path.basename(figs['disposal'])}` — cumulative disposal fluxes & % split")
    A("")
    A("## Calibration note\n")
    A("Per CALIBRATION_FINDINGS.md, the literal Table 12.2 is under-specified "
      "for reproducing Fig 12.4 (glucose-flux scale ~5 orders too small; basal "
      "insulin synthesis ~6 orders too small). The core applies a documented "
      "minimal fix (uniform glucose_flux_scale; aw/a71/b52 basal-balance "
      "scales) that leaves every tanh feedback shape and transfer rate exactly "
      "as printed. Results above are from that calibrated core.\n")

    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def main():
    patient, res, dose_g = run_ex1()
    if not res.success:
        raise SystemExit(f"Ex1 integration failed: {res.message}")
    split = disposal_split(res)
    m = metrics(res)
    figs = make_figures(patient, res, dose_g, split, m)
    path = write_results(patient, res, dose_g, split, m, figs)

    print("Ex1 done.")
    print(f"  glucose peak {m['peak_g']:.0f} mg/100ml @ {m['peak_t']:.0f} min, "
          f"recovery {m['recovery_t']:.0f} min")
    print(f"  insulin basal {m['insulin_basal']:.0f} -> peak {m['insulin_peak']:.0f} µU/ml")
    print(f"  glucagon basal {m['glucagon_basal']:.0f} -> min {m['glucagon_min']:.0f} nU/ml")
    print(f"  DISPOSAL SPLIT  renal F3={split['pct_F3']:.1f}%  "
          f"muscle/adipose F4={split['pct_F4']:.1f}%  CNS/RBC F5={split['pct_F5']:.1f}%")
    for k, v in figs.items():
        print(f"  figure[{k}]: {v}")
    print(f"  results: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
