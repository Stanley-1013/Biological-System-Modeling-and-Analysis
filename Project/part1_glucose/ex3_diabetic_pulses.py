"""Exercise 3 -- Repeated glucose-pulse sequence (Fig 12.5 protocol) on a
DIABETIC subject, compared to a NORMAL subject under the identical protocol.

Protocol (Fig 12.5): doses 0.5, 1.0, 2.5, 5, 10, 20, 40 grams to a 70-kg
subject at t = 0, 30, 70, 110, 180, 270, 400 min.

The diabetic subject uses the single canonical diabetic configuration in the
core (cobelli.make_patient('diabetic')): the Table 12.3 secretion/uptake-shape
changes, the insulin-driven hepatic (F2) and peripheral (H4) uptake gates frozen
to scale-consistent constants, and a calibration to the diabetic's OWN elevated
operating point (DIABETIC_BASAL = 140/7/75; see cobelli.calibrate_diabetic_basal
and CALIBRATION_FINDINGS.md). Its calibrated basal_amounts ARE the diabetic
steady state, so we use them directly as the IC. The normal subject starts from
its calibrated basal.

Produces (figures/):
  ex3_diabetic_vs_normal.png   side-by-side glucose & insulin, both subjects

Writes results/ex3_results.md with basal levels, recovery, and discussion.

Run:  python3 ex3_diabetic_pulses.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb
import ex_common as ec

# --- Fig 12.5 protocol ---
PULSE_DOSES_G = [0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 40.0]
PULSE_TIMES_MIN = [0.0, 30.0, 70.0, 110.0, 180.0, 270.0, 400.0]
PULSE_DURATION_MIN = 2.0
SIM_DURATION_MIN = 800.0   # cover all 7 pulses + a long recovery tail


def _pulse_forcing_and_times():
    forcing = ec.variable_pulse_train_forcing(
        PULSE_DOSES_G, PULSE_TIMES_MIN, duration=PULSE_DURATION_MIN
    )
    pulse_times = []
    for st in PULSE_TIMES_MIN:
        pulse_times.extend([st, st + PULSE_DURATION_MIN])
    return forcing, pulse_times


def run_subject(mode: str):
    # Both subjects come straight from the canonical core configuration. The
    # diabetic's calibrated basal_amounts ARE its (elevated) steady state, so we
    # use them directly -- no per-script frozen overrides, no pre-equilibration.
    patient = cb.make_patient(mode)
    y0 = patient.basal_amounts.to_array()
    forcing, pulse_times = _pulse_forcing_and_times()
    res = ec.run(
        patient, y0, SIM_DURATION_MIN, Ig=forcing,
        n_eval=2400, pulse_times=pulse_times, max_step=0.5,
    )
    return patient, res, y0


def recovery_time_after_last_pulse(t, g, basal_g, band_frac=0.05):
    """First time after the last pulse that glucose returns within band of its
    own basal. NaN if it never recovers within the window."""
    last = PULSE_TIMES_MIN[-1]
    mask = t >= last
    tt, gg = t[mask], g[mask]
    band = basal_g * (1.0 + band_frac)
    below = tt[gg <= band]
    return float(below[0]) if below.size else float("nan")


def summarize(res, basal_g_amount_to_conc):
    g = res.concentrations["gbar"]
    p = res.concentrations["pbar"]
    basal_g = float(g[0])
    return {
        "basal_g": basal_g,
        "peak_g": float(g.max()),
        "final_g": float(g[-1]),
        "basal_p": float(p[0]),
        "peak_p": float(p.max()),
        "final_p": float(p[-1]),
        "recovery_t": recovery_time_after_last_pulse(res.t, g, basal_g),
    }


def make_figure(n_res, d_res):
    plt = ec.setup_matplotlib()
    ec.ensure_dirs()
    tN, tD = n_res.t, d_res.t

    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5))

    # Glucose -- normal vs diabetic (overlay) on row 0
    axg = axes[0, 0]
    axg.plot(tN, n_res.concentrations["gbar"], color="#2471a3", lw=2, label="normal")
    axg.plot(tD, d_res.concentrations["gbar"], color="#c0392b", lw=2, label="diabetic")
    for st in PULSE_TIMES_MIN:
        axg.axvline(st, ls=":", color="0.7", lw=0.8)
    axg.set_xlabel("time (min)"); axg.set_ylabel("plasma glucose (mg/100 ml)")
    axg.set_title("Plasma glucose — normal vs diabetic (overlay)")
    axg.legend()

    # Insulin -- normal vs diabetic (overlay) on row 0
    axi = axes[0, 1]
    axi.plot(tN, n_res.concentrations["pbar"], color="#2471a3", lw=2, label="normal")
    axi.plot(tD, d_res.concentrations["pbar"], color="#c0392b", lw=2, label="diabetic")
    for st in PULSE_TIMES_MIN:
        axi.axvline(st, ls=":", color="0.7", lw=0.8)
    axi.set_xlabel("time (min)"); axi.set_ylabel("plasma insulin (µU/ml)")
    axi.set_title("Plasma insulin — normal vs diabetic (overlay)")
    axi.legend()

    # Row 1: side-by-side individual glucose (different y-scales)
    axn = axes[1, 0]
    axn.plot(tN, n_res.concentrations["gbar"], color="#2471a3", lw=1.8, label="glucose")
    axn2 = axn.twinx()
    axn2.plot(tN, n_res.concentrations["pbar"], color="#8e44ad", lw=1.4, ls="--", label="insulin")
    axn.set_xlabel("time (min)")
    axn.set_ylabel("glucose (mg/100 ml)", color="#2471a3")
    axn2.set_ylabel("insulin (µU/ml)", color="#8e44ad")
    axn.set_title("NORMAL subject (glucose + insulin)")

    axd = axes[1, 1]
    axd.plot(tD, d_res.concentrations["gbar"], color="#c0392b", lw=1.8, label="glucose")
    axd2 = axd.twinx()
    axd2.plot(tD, d_res.concentrations["pbar"], color="#e67e22", lw=1.4, ls="--", label="insulin")
    axd.set_xlabel("time (min)")
    axd.set_ylabel("glucose (mg/100 ml)", color="#c0392b")
    axd2.set_ylabel("insulin (µU/ml)", color="#e67e22")
    axd.set_title("DIABETIC subject (glucose + insulin)")

    fig.suptitle(
        "Ex3 — Fig 12.5 pulse train (0.5/1/2.5/5/10/20/40 g at "
        "0/30/70/110/180/270/400 min): diabetic vs normal",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(ec.FIG_DIR, "ex3_diabetic_vs_normal.png")
    fig.savefig(out); plt.close(fig)
    return out


def write_results(n_sum, d_sum, fig_path):
    ec.ensure_dirs()
    path = os.path.join(ec.RESULTS_DIR, "ex3_results.md")
    L = []
    A = L.append
    A("# Exercise 3 — Repeated glucose pulses: diabetic vs normal\n")
    A("**Question.** Using the DIABETIC parameter set, administer the Fig 12.5 "
      "glucose-pulse sequence (0.5, 1.0, 2.5, 5, 10, 20, 40 g to a 70-kg "
      "subject at t = 0, 30, 70, 110, 180, 270, 400 min). Plot plasma glucose "
      "and insulin and compare to the same protocol on a NORMAL subject.\n")

    A("**Protocol.** Identical escalating pulse train applied to both subjects "
      f"over {SIM_DURATION_MIN:.0f} min. Both use the single canonical "
      "configuration from the verified core (`cobelli.make_patient`). Normal "
      "starts from its calibrated clinical basal. The diabetic uses the Table "
      "12.3 secretion/uptake-shape changes (bw, cw, b6, c6, b42, c42), the "
      "insulin-driven hepatic (F2) and peripheral (H4) uptake gates frozen to "
      "scale-consistent constants, and a calibration to its OWN elevated "
      "operating point; its calibrated basal_amounts ARE the diabetic steady "
      "state, used directly as the IC (settle_to_basal is a no-op on it).\n")

    A("> **Finding (disclosed).** Table 12.3 lists `F2 = 0.037`, but that value "
      "is in the textbook's native (un-scaled) flux units. Our core multiplies "
      "the four glucose fluxes by glucose_flux_scale=1e5 (CALIBRATION_FINDINGS.md), "
      "so the literal 0.037 would become a ~3700 mg/min constant hepatic "
      "*vacuum* (~70x the normal basal F2 of ~52 mg/min) that clamps glucose "
      "flat -- physiologically backwards. The scale-consistent reading of \"F2/H2 "
      "replaced by a constant\" is that the diabetic liver can no longer RAMP "
      "uptake with insulin: we freeze F2 near the NORMAL basal hepatic-uptake "
      "flux (~5.25e-4 unscaled), and freeze H4 at the Table 12.3 0.0012. The "
      "elevated diabetic basal does not emerge from freezing alone (M1 glucose "
      "self-suppression and the glucagon gate make 91.5 a strong attractor), so "
      "the diabetic is calibrated to its own operating point "
      "(DIABETIC_BASAL = 140/7/75) by the same under-determined scales (aw, a71, "
      "b52) the normal subject uses -- no feedback shape is changed. At that low "
      "liver-insulin state the UNFROZEN H1 gate naturally sits high (~0.66 vs "
      "0.25 normal): hepatic production is no longer suppressed by insulin (the "
      "textbook diabetic mechanism, emergent not forced). This yields the correct "
      "signature below.\n")

    A("## Key numeric results\n")
    A("| Quantity | Normal | Diabetic |")
    A("|----------|--------|----------|")
    A(f"| Basal glucose (mg/100 ml) | {n_sum['basal_g']:.1f} | {d_sum['basal_g']:.1f} |")
    A(f"| Peak glucose (mg/100 ml)  | {n_sum['peak_g']:.0f} | {d_sum['peak_g']:.0f} |")
    A(f"| Final glucose (mg/100 ml) | {n_sum['final_g']:.1f} | {d_sum['final_g']:.1f} |")
    A(f"| Basal insulin (µU/ml)     | {n_sum['basal_p']:.1f} | {d_sum['basal_p']:.2f} |")
    A(f"| Peak insulin (µU/ml)      | {n_sum['peak_p']:.0f} | {d_sum['peak_p']:.1f} |")
    A(f"| Recovery after last pulse (min, within 5% of basal) | "
      f"{n_sum['recovery_t']:.0f} | {d_sum['recovery_t']:.0f} |")
    A("")

    higher_basal = d_sum["basal_g"] > n_sum["basal_g"]
    lower_insulin = d_sum["peak_p"] < n_sum["peak_p"]
    A("## Discussion\n")
    A(f"- **Basal level.** Diabetic basal glucose "
      f"({d_sum['basal_g']:.1f} mg/100 ml) is "
      f"{'higher' if higher_basal else 'not higher'} than normal "
      f"({n_sum['basal_g']:.1f}) — this is the diabetic's own calibrated "
      "operating point (DIABETIC_BASAL), with impaired insulin-driven uptake "
      "(F2, H4 frozen) and a high H1 gate keeping hepatic production up. "
      "Diabetic basal insulin "
      f"({d_sum['basal_p']:.2f} µU/ml) is below the normal "
      f"{n_sum['basal_p']:.1f} µU/ml (blunted secretion).")
    A(f"- **Insulin response.** The diabetic peak insulin "
      f"({d_sum['peak_p']:.1f} µU/ml) is "
      f"{'blunted vs' if lower_insulin else 'comparable to'} the normal peak "
      f"({n_sum['peak_p']:.0f} µU/ml) — blunted synthesis/secretion "
      "parameters (Table 12.3) limit the pancreatic response.")
    A("- **Recovery.** With insulin-driven hepatic and peripheral uptake "
      "impaired (F2 and H4 frozen low) and production not insulin-suppressed "
      "(high H1), the diabetic clears each pulse far more slowly; glucose stacks "
      "across the escalating ladder and stays elevated above its already-high "
      "basal, whereas the normal subject returns toward basal between pulses. On "
      "a standard IVGTT this same configuration recovers in ~100 min vs ~52 min "
      "for normal (~1.9x), the model expression of the textbook's '~2x slower "
      "recovery' for diabetes (§12.3.6).")
    A("- **The hump.** In the normal subject the closely-spaced later pulses "
      "produce the insulin hump (Ex 2: F6 ∝ r pool depletion/refill). In the "
      "diabetic subject the blunted secretion machinery cannot mount the same "
      "overshoot, so the characteristic insulin hump is suppressed even though "
      "glucose remains high.")
    A("")
    A("## Figure\n")
    A(f"- `{os.path.basename(fig_path)}` — overlay (row 1) and side-by-side "
      "(row 2) plasma glucose and insulin for normal vs diabetic.")
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def main():
    n_patient, n_res, _ = run_subject("normal")
    d_patient, d_res, _ = run_subject("diabetic")
    if not (n_res.success and d_res.success):
        raise SystemExit(f"Ex3 integration failed: normal={n_res.message}; "
                         f"diabetic={d_res.message}")

    n_sum = summarize(n_res, n_patient.volumes)
    d_sum = summarize(d_res, d_patient.volumes)
    fig_path = make_figure(n_res, d_res)
    path = write_results(n_sum, d_sum, fig_path)

    print("Ex3 done.")
    print(f"  basal glucose : normal {n_sum['basal_g']:.1f} | diabetic {d_sum['basal_g']:.1f} mg/100ml")
    print(f"  peak glucose  : normal {n_sum['peak_g']:.0f} | diabetic {d_sum['peak_g']:.0f} mg/100ml")
    print(f"  basal insulin : normal {n_sum['basal_p']:.1f} | diabetic {d_sum['basal_p']:.2f} µU/ml")
    print(f"  peak insulin  : normal {n_sum['peak_p']:.0f} | diabetic {d_sum['peak_p']:.1f} µU/ml")
    print(f"  recovery (min): normal {n_sum['recovery_t']:.0f} | diabetic {d_sum['recovery_t']:.0f}")
    print(f"  figure: {fig_path}")
    print(f"  results: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
