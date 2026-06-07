"""Part 2 — Question (b): Total COST of vaccination ($10 per vaccination) and
cost-effectiveness (cost per infection averted).

Uses the model's built-in cost accumulator V(t) (dV/dt = nu*(S_f2 + S_m2)) so the
cumulative number of vaccinations is integrated alongside the state (no post-hoc
quadrature error). Each vaccination costs $10, so total cost = $10 * V(T).
Vaccinations RECUR because protection wanes (P -> S at rate l) and new
susceptibles age in (S_m1/S_f1 -> S_*2), so once the protected fraction
saturates near nu/(nu+l) the program re-vaccinates at a roughly steady annual
rate and cumulative cost grows ~linearly.

Infections averted = cumulative new infections (baseline) - cumulative new
infections (vaccine), obtained by trapezoidal integration of the incidence
auxiliary lambda_Sf2*S_f2 + lambda_Sm2*S_m2.

Modeling assumption (documented in every results file):
  gamma = 0.1/yr (mean ~10 yr HIV->AIDS; R0 ~ 2.35 > 1), NOT the literal
  Table 15.2 gamma = 1.16 (R0 < 1, no epidemic). Seed = infectious males
  I_m2 = 5. Vaccine: nu = 0.65/yr, l = 0.1/yr.

Run:  python3 q_b_cost.py
Saves: figures/qb_cost.png   (cumulative cost + infections-averted panels)
Units: time YEARS, vaccinations COUNT (people), cost USD, infections COUNT.
"""

from __future__ import annotations

import math
import os

import numpy as np

import sic

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")

GAMMA_CALIBRATED = 0.1
NU = 0.65
L_WANE = 0.1
SEED_I_M2 = 5.0
HORIZONS = [20.0, 30.0, 50.0]   # reporting horizons (years)
MAX_HORIZON = 50.0
N_EVAL = 6000
COST_PER_VAX = sic.COST_PER_VACCINATION_USD  # $10


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 140,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "font.size": 10,
        }
    )
    return plt


def compute_R0(p: sic.Params) -> float:
    dur = 1.0 / (p.mu + p.gamma)
    return p.c * dur * math.sqrt(p.beta_mf * p.beta_fm)


def _cumtrap(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Cumulative trapezoidal integral of y over t (same length as t, starts 0)."""
    out = np.zeros_like(y, dtype=float)
    dt = np.diff(t)
    out[1:] = np.cumsum(0.5 * (y[1:] + y[:-1]) * dt)
    return out


def _interp(t: np.ndarray, series: np.ndarray, t_query: float) -> float:
    return float(np.interp(t_query, t, series))


def run() -> int:
    os.makedirs(FIG_DIR, exist_ok=True)
    plt = _plt()

    base = sic.Params().with_(gamma=GAMMA_CALIBRATED)        # nu = 0
    vac = base.with_(nu=NU, l=L_WANE)                        # vaccine ON
    y0 = sic.initial_conditions(seed_A_m2=0.0, seed_I_m2=SEED_I_M2)

    R0 = compute_R0(base)
    print("=" * 74)
    print("Q(b)  Total cost of vaccination ($10/vaccination) & cost-effectiveness")
    print("=" * 74)
    print(f"  gamma = {GAMMA_CALIBRATED}/yr   R0 = {R0:.3f}   "
          f"vaccine nu = {NU}/yr, l = {L_WANE}/yr   $/vax = {COST_PER_VAX:.0f}")

    res_b = sic.simulate(y0, MAX_HORIZON, base, n_eval=N_EVAL)
    res_v = sic.simulate(y0, MAX_HORIZON, vac, n_eval=N_EVAL)
    if not (res_b.success and res_v.success):
        print("  SOLVER FAILED:", res_b.message, "|", res_v.message)
        return 1
    aux_b = sic.auxiliaries(res_b)
    aux_v = sic.auxiliaries(res_v)
    t = aux_v["t"]

    # cumulative vaccinations & cost from the accumulator state V(t)
    cum_vax = aux_v["cum_vaccinations"]
    cost = aux_v["cost_usd"]                 # = $10 * V(t)

    # cumulative infections (trapezoid of incidence) for both scenarios
    cum_inf_b = _cumtrap(t, aux_b["incidence"])
    cum_inf_v = _cumtrap(t, aux_v["incidence"])
    averted = cum_inf_b - cum_inf_v

    # annual steady vaccination rate / cost (slope over the last 10 yr)
    mask = t >= (MAX_HORIZON - 10.0)
    annual_vax = float(np.polyfit(t[mask], cum_vax[mask], 1)[0])
    annual_cost = annual_vax * COST_PER_VAX

    print("\n  HORIZON TABLE")
    print(f"  {'T(yr)':>6} {'cum.vax':>12} {'cost($)':>14} "
          f"{'inf.baseline':>13} {'inf.vaccine':>12} {'averted':>10} {'$/averted':>11}")
    rows = []
    for T in HORIZONS:
        v_T = _interp(t, cum_vax, T)
        c_T = _interp(t, cost, T)
        ib_T = _interp(t, cum_inf_b, T)
        iv_T = _interp(t, cum_inf_v, T)
        av_T = ib_T - iv_T
        cpa = c_T / av_T if av_T > 0 else float("nan")
        rows.append((T, v_T, c_T, ib_T, iv_T, av_T, cpa))
        print(f"  {T:6.0f} {v_T:12.0f} {c_T:14,.0f} {ib_T:13.0f} "
              f"{iv_T:12.0f} {av_T:10.0f} {cpa:11,.0f}")

    print(f"\n  Annual STEADY cost (slope, last 10 yr) = "
          f"{annual_vax:,.0f} vaccinations/yr  ->  ${annual_cost:,.0f}/yr")
    print("  (Cost grows ~linearly once P saturates near nu/(nu+l): waning + "
          "ageing-in keep re-vaccinating people.)")

    # =====================================================================
    # FIGURE: two panels - cumulative cost(t) and cumulative infections-averted(t)
    # =====================================================================
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.8, 7.4), sharex=True)

    # Panel 1: cumulative cost (and cumulative vaccinations on twin axis)
    ax1.plot(t, cost / 1e3, color="#b9770e", lw=2.3, label="cumulative cost")
    ax1.set_ylabel("cumulative cost  (thousand USD)")
    ax1.set_title("Q(b) Cumulative vaccination cost ($10 per vaccination)")
    ax1b = ax1.twinx()
    ax1b.plot(t, cum_vax / 1e3, color="#6c3483", lw=1.6, ls="--",
              label="cumulative vaccinations")
    ax1b.set_ylabel("cumulative vaccinations (thousands)", color="#6c3483")
    ax1b.tick_params(axis="y", labelcolor="#6c3483")
    ax1b.grid(False)
    for T in HORIZONS:
        ax1.axvline(T, color="#888", lw=0.8, ls=":")
        ax1.annotate(f"${_interp(t, cost, T)/1e3:,.0f}k",
                     xy=(T, _interp(t, cost, T) / 1e3),
                     xytext=(T - 1.5, _interp(t, cost, T) / 1e3 * 1.02),
                     fontsize=8, ha="right", color="#b9770e")
    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax1b.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc="upper left", fontsize=9)

    # Panel 2: cumulative infections averted, with cumulative-incidence context
    ax2.plot(t, cum_inf_b / 1e3, color="#b03a2e", lw=1.6, ls="--",
             label="cumulative infections (baseline)")
    ax2.plot(t, cum_inf_v / 1e3, color="#1f6f8b", lw=1.6, ls="--",
             label="cumulative infections (vaccine)")
    ax2.plot(t, averted / 1e3, color="#117a65", lw=2.4,
             label="infections AVERTED (baseline - vaccine)")
    ax2.fill_between(t, 0, averted / 1e3, color="#117a65", alpha=0.10)
    ax2.set_xlabel("time (years)")
    ax2.set_ylabel("cumulative infections (thousands)")
    ax2.set_title("Q(b) Cumulative infections averted by vaccination")
    for T in HORIZONS:
        ax2.axvline(T, color="#888", lw=0.8, ls=":")
    ax2.legend(loc="upper left", fontsize=9)
    ax2.set_xlim(0, MAX_HORIZON)

    fig.tight_layout()
    f1 = os.path.join(FIG_DIR, "qb_cost.png")
    fig.savefig(f1)
    plt.close(fig)
    print(f"\n  saved {f1}")

    # ---- summary block for results write-up ----
    print("\n  SUMMARY (for qb_results.md):")
    for (T, v_T, c_T, ib_T, iv_T, av_T, cpa) in rows:
        print(f"    T={T:.0f}: vax={v_T:.0f} cost=${c_T:,.0f} "
              f"averted={av_T:.0f} cost_per_averted=${cpa:,.0f}")
    print(f"    annual_steady_cost=${annual_cost:,.0f}/yr "
          f"({annual_vax:,.0f} vax/yr)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
