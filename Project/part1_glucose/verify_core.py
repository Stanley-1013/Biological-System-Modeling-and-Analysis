"""Verification harness for the Cobelli (1982) glucose-insulin core module.

Runs three checks and prints a PASS/FAIL summary with the key numbers:

  (a) BASAL EQUILIBRIUM   -- residual max|dy/dt| at the basal IC; if not ~0,
      locate the nearby equilibrium and report the offset from physiological
      basal.
  (b) NORMAL IVGTT        -- a standard glucose bolus from the basal IC; check
      the response is qualitatively like Fig 12.4 (glucose peaks then returns
      toward basal within ~90 min; insulin rises fast; glucagon dips). Saves
      figures/verify_normal_ivgtt.png.
  (c) LSODA vs RADAU      -- same IVGTT with both integrators; report the max
      relative difference (should be tiny).

Run:  python3 verify_core.py
"""

from __future__ import annotations

import os

import numpy as np

import cobelli as cb

# --- IVGTT protocol constants (standard clinical bolus) ---
IVGTT_DOSE_G_PER_KG = 0.33          # g/kg  (standard IVGTT 0.3-0.33 g/kg)
IVGTT_DURATION_MIN = 2.0            # bolus delivered over ~2 min
SIM_DURATION_MIN = 150.0           # observation window
RECOVERY_BAND_FRAC = 0.05          # "recovered" = within 5% of basal
RESIDUAL_TOL = 1e-3                # |dy/dt| considered steady (per-state max)
CROSSVAL_TOL = 1e-3                # max relative LSODA-vs-Radau difference

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")


def _ivgtt_forcing(body_weight_kg: float):
    dose_mg = IVGTT_DOSE_G_PER_KG * body_weight_kg * 1000.0  # g/kg -> mg
    return cb.make_rectangular_pulse(dose_mg, t_start=0.0, duration=IVGTT_DURATION_MIN), dose_mg


def check_basal_equilibrium(patient: cb.Patient):
    """Return (passed, info_dict). Reports residual and, if needed, the nearby
    equilibrium offset from physiological basal."""
    y0 = patient.basal_amounts.to_array()
    residual = cb.basal_residual(patient, y0)
    info = {"residual": residual, "used_literal_basal": True}

    if residual <= RESIDUAL_TOL:
        info["canonical_ic"] = y0
        return True, info

    # Not a steady state at the literal basal: find the nearby equilibrium.
    y_eq, eq_res, ok = cb.find_equilibrium(patient, y0)
    c0 = cb.amounts_to_concentrations(y0, patient.volumes)
    ce = cb.amounts_to_concentrations(y_eq, patient.volumes)
    info.update(
        {
            "used_literal_basal": False,
            "eq_residual": eq_res,
            "eq_success": ok,
            "canonical_ic": y_eq,
            "offset_gbar_pct": 100.0 * (ce.gbar - c0.gbar) / c0.gbar,
            "offset_pbar_pct": 100.0 * (ce.pbar - c0.pbar) / max(c0.pbar, 1e-12),
        }
    )
    return (eq_res <= RESIDUAL_TOL), info


def run_ivgtt(patient: cb.Patient, y0: np.ndarray, method: str = "LSODA"):
    forcing, dose_mg = _ivgtt_forcing(patient.body_weight_kg)
    t_eval = np.linspace(0.0, SIM_DURATION_MIN, 600)
    res = cb.simulate(
        patient,
        y0,
        (0.0, SIM_DURATION_MIN),
        Ig=forcing,
        t_eval=t_eval,
        method=method,
        pulse_times=[0.0, IVGTT_DURATION_MIN],
        max_step=0.5,
    )
    return res, dose_mg


def analyze_ivgtt(res: cb.SimResult):
    g = res.concentrations["gbar"]
    p = res.concentrations["pbar"]
    c = res.concentrations["cbar"]
    basal_g = g[0]
    peak_g = float(g.max())
    peak_t = float(res.t[int(g.argmax())])

    # recovery: first time after the peak that glucose is within band of basal
    after = res.t > peak_t
    band = basal_g * (1.0 + RECOVERY_BAND_FRAC)
    rec_times = res.t[after][g[after] <= band]
    recovery_t = float(rec_times[0]) if rec_times.size else float("nan")

    insulin_peak = float(p.max())
    insulin_peak_t = float(res.t[int(p.argmax())])
    glucagon_min = float(c.min())

    return {
        "basal_g": basal_g,
        "peak_g": peak_g,
        "peak_t": peak_t,
        "recovery_t": recovery_t,
        "insulin_basal": float(p[0]),
        "insulin_peak": insulin_peak,
        "insulin_peak_t": insulin_peak_t,
        "glucagon_basal": float(c[0]),
        "glucagon_min": glucagon_min,
    }


def save_ivgtt_figure(res: cb.SimResult, metrics: dict, dose_mg: float):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(FIG_DIR, exist_ok=True)
    t = res.t
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

    ax = axes[0]
    ax.plot(t, res.concentrations["gbar"], color="#c0392b", lw=2)
    ax.axhline(metrics["basal_g"], ls="--", lw=1, color="0.5")
    if np.isfinite(metrics["recovery_t"]):
        ax.axvline(metrics["recovery_t"], ls=":", lw=1, color="#c0392b")
    ax.set_title(f"Plasma glucose (peak {metrics['peak_g']:.0f} mg/100ml)")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("ḡ  (mg/100 ml)")

    ax = axes[1]
    ax.plot(t, res.concentrations["pbar"], color="#2471a3", lw=2)
    ax.axhline(metrics["insulin_basal"], ls="--", lw=1, color="0.5")
    ax.set_title(f"Plasma insulin (peak {metrics['insulin_peak']:.0f} µU/ml)")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("p̄  (µU/ml)")

    ax = axes[2]
    ax.plot(t, res.concentrations["cbar"], color="#1e8449", lw=2)
    ax.axhline(metrics["glucagon_basal"], ls="--", lw=1, color="0.5")
    ax.set_title(f"Plasma glucagon (dips to {metrics['glucagon_min']:.0f})")
    ax.set_xlabel("time (min)")
    ax.set_ylabel("c̄  (nU/ml)")

    fig.suptitle(
        f"Normal IVGTT verification  (dose {dose_mg/1000:.1f} g over "
        f"{IVGTT_DURATION_MIN:.0f} min)  — compare Fig 12.4",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(FIG_DIR, "verify_normal_ivgtt.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def cross_validate(patient: cb.Patient, y0: np.ndarray):
    res_lsoda, _ = run_ivgtt(patient, y0, method="LSODA")
    res_radau, _ = run_ivgtt(patient, y0, method="Radau")

    # Compare on shared t_eval grid (same nodes were requested).
    g1 = res_lsoda.concentrations["gbar"]
    g2 = res_radau.concentrations["gbar"]
    p1 = res_lsoda.concentrations["pbar"]
    p2 = res_radau.concentrations["pbar"]

    def max_rel_diff(a, b):
        scale = np.maximum(np.abs(a), np.maximum(np.abs(b), 1.0))
        return float(np.max(np.abs(a - b) / scale))

    return max(max_rel_diff(g1, g2), max_rel_diff(p1, p2))


def main():
    print("=" * 72)
    print("Cobelli (1982) glucose-insulin CORE verification")
    print("=" * 72)

    patient = cb.make_patient("normal")
    print(f"\nCalibrated basal scales: aw={patient.params['aw']:.4g}, "
          f"a71={patient.params['a71']:.4g}, "
          f"glucose_flux_scale={patient.params['glucose_flux_scale']:.3g}")
    bc = patient.basal_conc
    print(f"Basal concentrations: gbar={bc.gbar} mg/100ml, pbar={bc.pbar} uU/ml, "
          f"lbar={bc.lbar:.2f}, ibar={bc.ibar:.2f}, cbar={bc.cbar} nU/ml")

    results = {}

    # ---- (a) Basal equilibrium ----
    print("\n--- (a) BASAL EQUILIBRIUM ---")
    pass_a, info_a = check_basal_equilibrium(patient)
    results["a"] = pass_a
    canonical_ic = info_a["canonical_ic"]
    if info_a["used_literal_basal"]:
        print(f"  Literal clinical basal IS a steady state.")
        print(f"  residual max|dy/dt| = {info_a['residual']:.3e}  "
              f"(tol {RESIDUAL_TOL:.0e})  -> {'PASS' if pass_a else 'FAIL'}")
        print(f"  Canonical baseline IC = literal basal amounts.")
    else:
        print(f"  Literal basal residual = {info_a['residual']:.3e} (not steady).")
        print(f"  Nearby equilibrium residual = {info_a['eq_residual']:.3e} "
              f"(success={info_a['eq_success']}).")
        print(f"  Offset from physiological basal: "
              f"gbar {info_a['offset_gbar_pct']:+.3f}%, "
              f"pbar {info_a['offset_pbar_pct']:+.3f}%.")
        print(f"  -> using the nearby equilibrium as canonical baseline IC.")

    # ---- (b) Normal IVGTT ----
    print("\n--- (b) NORMAL IVGTT (compare Fig 12.4) ---")
    res_ivgtt, dose_mg = run_ivgtt(patient, canonical_ic, method="LSODA")
    metrics = analyze_ivgtt(res_ivgtt)
    print(f"  dose = {dose_mg/1000:.2f} g ({IVGTT_DOSE_G_PER_KG} g/kg) "
          f"over {IVGTT_DURATION_MIN:.0f} min; success={res_ivgtt.success}")
    print(f"  glucose : basal {metrics['basal_g']:.1f} -> peak "
          f"{metrics['peak_g']:.1f} mg/100ml @ t={metrics['peak_t']:.1f} min")
    print(f"  recovery (within {int(RECOVERY_BAND_FRAC*100)}% of basal) at "
          f"t = {metrics['recovery_t']:.1f} min")
    print(f"  insulin : basal {metrics['insulin_basal']:.1f} -> peak "
          f"{metrics['insulin_peak']:.1f} uU/ml @ t={metrics['insulin_peak_t']:.1f} min")
    print(f"  glucagon: basal {metrics['glucagon_basal']:.1f} -> min "
          f"{metrics['glucagon_min']:.1f} nU/ml (should dip)")

    # qualitative criteria for Fig 12.4 likeness
    peak_ok = 150.0 <= metrics["peak_g"] <= 400.0          # rises into hundreds
    recovery_ok = (np.isfinite(metrics["recovery_t"])
                   and 40.0 <= metrics["recovery_t"] <= 130.0)  # ~90 min ballpark
    insulin_ok = metrics["insulin_peak"] > 1.5 * metrics["insulin_basal"]  # rises
    insulin_fast = metrics["insulin_peak_t"] <= 30.0       # rises quickly
    glucagon_dips = metrics["glucagon_min"] < metrics["glucagon_basal"]
    pass_b = peak_ok and recovery_ok and insulin_ok and insulin_fast and glucagon_dips
    results["b"] = pass_b
    print(f"  criteria: peak_in_range={peak_ok}, recovery~90min={recovery_ok}, "
          f"insulin_rises={insulin_ok}, insulin_fast={insulin_fast}, "
          f"glucagon_dips={glucagon_dips}")
    fig_path = save_ivgtt_figure(res_ivgtt, metrics, dose_mg)
    print(f"  figure saved: {fig_path}")
    print(f"  -> {'PASS' if pass_b else 'FAIL'}")

    # ---- (c) Cross-validation LSODA vs Radau ----
    print("\n--- (c) CROSS-VALIDATION (LSODA vs Radau) ---")
    max_rel = cross_validate(patient, canonical_ic)
    pass_c = max_rel <= CROSSVAL_TOL
    results["c"] = pass_c
    print(f"  max relative difference (gbar, pbar) = {max_rel:.3e} "
          f"(tol {CROSSVAL_TOL:.0e})  -> {'PASS' if pass_c else 'FAIL'}")

    # ---- Summary ----
    print("\n" + "=" * 72)
    all_pass = all(results.values())
    print("SUMMARY:  " + "   ".join(
        f"({k}) {'PASS' if v else 'FAIL'}" for k, v in results.items()))
    print("OVERALL:  " + ("PASS" if all_pass else "FAIL"))
    print("=" * 72)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
