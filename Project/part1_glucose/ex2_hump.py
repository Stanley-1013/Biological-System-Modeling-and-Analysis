"""Exercise 2 -- The insulin "hump": why it develops under repeated glucose
pulses (Fig 12.5, normal) and why a similar hump appears for obese subjects
(Fig 12.7).

Two simulations:
  (i)  NORMAL subject, repeated glucose-pulse train -> insulin hump after the
       later pulses (Fig 12.5).
  (ii) OBESE subject, single IVGTT -> abnormal hump in the insulin DECAY curve
       (Fig 12.7); obese parameters b6=0.5 (hypersensitive secretion) and
       m02=0.13 (altered liver-insulin clearance).

For both we also plot the releasable (r) and stored (s) pancreatic insulin
pools and the secretion flux F6 ∝ r, which is the mechanistic origin of the
hump (pool depletion / over-refill + multi-compartment lag).

Produces (figures/):
  ex2_normal_hump.png   normal repeated-pulse run (glucose, insulin, r/s, F6)
  ex2_obese_hump.png    obese single-IVGTT run    (glucose, insulin, r/s, F6)

Writes results/ex2_results.md with the mechanistic explanation.

Run:  python3 ex2_hump.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb
import ex_common as ec

# --- Fig 12.5-style repeated-pulse protocol (escalating dose ladder) ---
# Doses (g) and times (min) per the Fig 12.5 description used in Ex 3 too.
PULSE_DOSES_G = [0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 40.0]
PULSE_TIMES_MIN = [0.0, 30.0, 70.0, 110.0, 180.0, 270.0, 400.0]
PULSE_DURATION_MIN = 2.0
NORMAL_SIM_MIN = 700.0          # cover all 7 pulses + recovery tail

# --- Obese single-IVGTT protocol ---
OBESE_DOSE_G_PER_KG = 0.33
OBESE_BOLUS_MIN = 2.0
OBESE_SIM_MIN = 200.0


def run_normal_pulse_train():
    patient = cb.make_patient("normal")
    y0 = patient.basal_amounts.to_array()
    forcing = ec.variable_pulse_train_forcing(
        PULSE_DOSES_G, PULSE_TIMES_MIN, duration=PULSE_DURATION_MIN
    )
    pulse_times = []
    for st in PULSE_TIMES_MIN:
        pulse_times.extend([st, st + PULSE_DURATION_MIN])
    res = ec.run(
        patient, y0, NORMAL_SIM_MIN, Ig=forcing,
        n_eval=2000, pulse_times=pulse_times, max_step=0.5,
    )
    return patient, res


def run_obese_ivgtt():
    patient = cb.make_patient("obese")
    # Obese basal differs from the normal clinical reference -> pre-equilibrate.
    y0 = cb.settle_to_basal(patient)
    dose_g = OBESE_DOSE_G_PER_KG * patient.body_weight_kg
    forcing = ec.single_ivgtt_forcing(dose_g, 0.0, OBESE_BOLUS_MIN)
    res = ec.run(
        patient, y0, OBESE_SIM_MIN, Ig=forcing,
        n_eval=1600, pulse_times=[0.0, OBESE_BOLUS_MIN], max_step=0.5,
    )
    return patient, res, dose_g, y0


def detect_hump(t, p):
    """Detect a non-monotone 'hump' in the insulin decay: a local minimum
    followed by a later local maximum (insulin rises again after starting to
    fall). Returns (has_hump, hump_time, hump_value, dip_value)."""
    p = np.asarray(p)
    peak_idx = int(p.argmax())
    if peak_idx >= len(p) - 3:
        return False, float("nan"), float("nan"), float("nan")
    tail = p[peak_idx:]
    ttail = t[peak_idx:]
    # find first local minimum in the tail, then a subsequent local maximum
    dmin_idx = None
    for k in range(1, len(tail) - 1):
        if tail[k] <= tail[k - 1] and tail[k] < tail[k + 1]:
            dmin_idx = k
            break
    if dmin_idx is None:
        return False, float("nan"), float("nan"), float("nan")
    after = tail[dmin_idx:]
    tafter = ttail[dmin_idx:]
    rise_idx = int(after.argmax())
    has = after[rise_idx] > tail[dmin_idx] * 1.02 and rise_idx > 0
    return (has, float(tafter[rise_idx]), float(after[rise_idx]),
            float(tail[dmin_idx]))


def _plot_run(plt, patient, res, title, out, extra_lines=None):
    t = res.t
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    ax = axes[0, 0]
    ax.plot(t, res.concentrations["gbar"], color="#c0392b", lw=2)
    ax.set_xlabel("time (min)"); ax.set_ylabel("plasma glucose (mg/100 ml)")
    ax.set_title("Plasma glucose ḡ")

    ax = axes[0, 1]
    ax.plot(t, res.concentrations["pbar"], color="#2471a3", lw=2, label="plasma p̄")
    ax.plot(t, res.concentrations["lbar"], color="#8e44ad", lw=1.6, ls="--", label="liver l̄")
    ax.set_xlabel("time (min)"); ax.set_ylabel("insulin (µU/ml)")
    ax.set_title("Insulin (the HUMP appears here)")
    if extra_lines:
        for tx, lab in extra_lines:
            ax.axvline(tx, ls=":", color="#e67e22", lw=1.3)
        ax.plot([], [], ls=":", color="#e67e22", label=extra_lines[0][1])
    ax.legend()

    ax = axes[1, 0]
    ax.plot(t, res.y[cb.IDX_R], color="#27ae60", lw=2, label="releasable r")
    ax.plot(t, res.y[cb.IDX_S], color="#d35400", lw=2, ls="--", label="stored s")
    ax.set_xlabel("time (min)"); ax.set_ylabel("pancreatic insulin pool (µU)")
    ax.set_title("Releasable r & stored s pools (F6 ∝ r)")
    ax.legend()

    ax = axes[1, 1]
    ax.plot(t, res.fluxes["F6"], color="#c0392b", lw=2)
    ax.set_xlabel("time (min)"); ax.set_ylabel("secretion F6 (µU/min)")
    ax.set_title("Insulin secretion flux F6 = 0.5·a6·[1+tanh(b6(Δḡ+c6))]·r")

    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out); plt.close(fig)
    return out


def make_figures(n_patient, n_res, o_patient, o_res, o_dose_g):
    plt = ec.setup_matplotlib()
    ec.ensure_dirs()
    figs = {}

    pulse_marks = [(PULSE_TIMES_MIN[0], "glucose pulses")]
    figs["normal"] = _plot_run(
        plt, n_patient, n_res,
        "Ex2 (i) — Normal subject, repeated glucose pulses (Fig 12.5)\n"
        f"doses {PULSE_DOSES_G} g at t={PULSE_TIMES_MIN} min",
        os.path.join(ec.FIG_DIR, "ex2_normal_hump.png"),
        extra_lines=pulse_marks,
    )
    figs["obese"] = _plot_run(
        plt, o_patient, o_res,
        "Ex2 (ii) — Obese subject, single IVGTT (Fig 12.7)\n"
        f"dose {o_dose_g:.1f} g; obese b6=0.5, m02=0.13 — note insulin-decay hump",
        os.path.join(ec.FIG_DIR, "ex2_obese_hump.png"),
    )
    return figs


def write_results(n_res, o_res, o_dose_g, n_hump, o_hump, figs):
    ec.ensure_dirs()
    path = os.path.join(ec.RESULTS_DIR, "ex2_results.md")
    L = []
    A = L.append
    A("# Exercise 2 — The insulin \"hump\"\n")
    A("**Question.** Why does the \"hump\" in insulin concentration develop in "
      "Fig 12.5 (repeated glucose pulses, normal subject)? Why is there a "
      "similar hump for obese persons in Fig 12.7?\n")

    A("## Simulations\n")
    A("- (i) NORMAL subject, escalating repeated-pulse train "
      f"({PULSE_DOSES_G} g at t={PULSE_TIMES_MIN} min), {NORMAL_SIM_MIN:.0f} min.")
    A(f"- (ii) OBESE subject, single IVGTT {o_dose_g:.1f} g, from the "
      "pre-equilibrated obese basal (settle_to_basal).\n")

    A("## Quantitative hump detection\n")
    A(f"- Normal repeated-pulse insulin: hump detected = **{n_hump[0]}**; "
      f"insulin re-rises to ~{n_hump[2]:.0f} µU/ml near t={n_hump[1]:.0f} min "
      f"after dipping to ~{n_hump[3]:.0f} µU/ml.")
    A(f"- Obese single-IVGTT insulin decay: hump detected = **{o_hump[0]}**; "
      f"secondary insulin rise to ~{o_hump[2]:.0f} µU/ml near "
      f"t={o_hump[1]:.0f} min (dip ~{o_hump[3]:.0f} µU/ml).")
    A(f"- Obese peak plasma insulin = {float(o_res.concentrations['pbar'].max()):.0f} µU/ml "
      f"vs basal {float(o_res.concentrations['pbar'][0]):.0f} µU/ml.\n")

    A("## Mechanism — common origin of both humps\n")
    A("The pancreatic secretion flux is **F6 = 0.5·a6·[1 + tanh(b6(Δḡ + c6))]·r** "
      "(Eq 12.6), i.e. secretion is *proportional to the releasable pool r*. "
      "r is refilled from the stored pool s on its own slow timescale "
      "(dr/dt = k21·s − k12·r − F6; ds/dt = −k21·s + k12·r + W). You cannot "
      "secrete insulin you do not have, and you cannot refill r instantly.\n")
    A("**(i) Repeated pulses (Fig 12.5).** Each glucose pulse opens the F6 gate "
      "and drains r into the liver pool. Because the pulses are spaced shorter "
      "than the pool-refill / glucose-clearance time, r is repeatedly depleted "
      "and then over-refilled from s; the escalating dose ladder makes each "
      "later pulse drain more. The multi-compartment lag (r→liver l→plasma "
      "p→interstitial i) stacks the delayed contributions of successive pulses, "
      "so plasma insulin does NOT decay exponentially between pulses — it "
      "accumulates into a delayed **hump** after the later, larger pulses, which "
      "greatly delays recovery. The r/s and F6 panels in the figure show the "
      "depletion-refill cycling that drives this.\n")
    A("**(ii) Obese subject (Fig 12.7).** Same pool dynamics, but driven by the "
      "parameter changes rather than repeated input. Obese overrides make "
      "secretion **hypersensitive**: b6 = 0.5 (vs nominal 9.23e-2) hugely "
      "steepens the F6 gate, so a single glucose load triggers an outsized, "
      "abrupt drain-and-refill of r; and m02 = 0.13 alters liver-insulin "
      "clearance so the downstream insulin clears sluggishly. The pools "
      "overshoot and the secretion flux re-engages as r refills, producing an "
      "abnormal **hump in the insulin-decay curve** even though the glucose "
      "response is near-normal. The same F6 ∝ r over-refill mechanism underlies "
      "both figures — repeated forcing in 12.5, hypersensitive parameters in "
      "12.7.\n")

    A("## Figures\n")
    A(f"- `{os.path.basename(figs['normal'])}` — normal repeated-pulse run "
      "(glucose, insulin, r/s pools, F6).")
    A(f"- `{os.path.basename(figs['obese'])}` — obese single-IVGTT run "
      "(glucose, insulin, r/s pools, F6).")
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def main():
    n_patient, n_res = run_normal_pulse_train()
    o_patient, o_res, o_dose_g, _ = run_obese_ivgtt()
    if not (n_res.success and o_res.success):
        raise SystemExit(f"Ex2 integration failed: normal={n_res.message}; "
                         f"obese={o_res.message}")

    n_hump = detect_hump(n_res.t, n_res.concentrations["pbar"])
    o_hump = detect_hump(o_res.t, o_res.concentrations["pbar"])

    figs = make_figures(n_patient, n_res, o_patient, o_res, o_dose_g)
    path = write_results(n_res, o_res, o_dose_g, n_hump, o_hump, figs)

    print("Ex2 done.")
    print(f"  normal repeated-pulse hump detected: {n_hump[0]} "
          f"(re-rise ~{n_hump[2]:.0f} µU/ml @ {n_hump[1]:.0f} min)")
    print(f"  obese IVGTT decay hump detected: {o_hump[0]} "
          f"(re-rise ~{o_hump[2]:.0f} µU/ml @ {o_hump[1]:.0f} min)")
    for k, v in figs.items():
        print(f"  figure[{k}]: {v}")
    print(f"  results: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
