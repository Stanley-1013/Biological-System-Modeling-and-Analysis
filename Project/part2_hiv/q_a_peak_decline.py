"""Part 2 — Question (a): Does vaccination make the HIV epidemic PEAK then DECLINE?

Compares the ignited sIC baseline (nu = 0) against the vaccinated scenario
(nu = 0.65/yr, l = 0.1/yr) over a multi-decade horizon and characterises whether
HIV PREVALENCE and INCIDENCE reach a peak and then fall under vaccination.

Modeling assumption (documented in every results file):
  Uses the biologically grounded gamma = 0.1/yr (mean ~10 yr HIV->AIDS, within
  the textbook's stated 1-10 yr range), NOT the literal Table 15.2 gamma = 1.16
  which gives R0 < 1 (no epidemic). With gamma = 0.1 the two-sex
  R0 = c*sqrt(beta_mf*beta_fm)/(mu+gamma) ~ 2.35 > 1. Seed = infectious males
  I_m2 = 5 (the literal A_m2 = 5 cannot ignite because A is excluded from lambda).

Run:  python3 q_a_peak_decline.py
Saves: figures/qa_prevalence.png
       figures/qa_incidence.png
       figures/qa_protected_fraction.png
Units: time YEARS, prevalence/incidence proportions or new infections/yr.
"""

from __future__ import annotations

import math
import os

import numpy as np

import sic

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")

# --- scenario constants ---
GAMMA_CALIBRATED = 0.1   # /yr  (mean ~10 yr HIV->AIDS; R0 ~ 2.35)
NU = 0.65                # /yr  vaccination rate of S_{.,2} -> P
L_WANE = 0.1             # /yr  waning rate P -> S (mean 10-yr protection)
SEED_I_M2 = 5.0          # infectious-male ignition seed
HORIZON_YEARS = 80.0     # primary display horizon
LONG_HORIZON = 200.0     # long horizon used only to locate the true prevalence peak
N_EVAL = 4000


# ---------------------------------------------------------------------------
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
    """Two-sex R0 = c*sqrt(beta_mf*beta_fm)/(mu+gamma) (geometric-mean form)."""
    dur = 1.0 / (p.mu + p.gamma)
    return p.c * dur * math.sqrt(p.beta_mf * p.beta_fm)


def _peak(t: np.ndarray, series: np.ndarray) -> tuple[float, float, bool]:
    """Return (peak_value, peak_time, peaked_interior).

    ``peaked_interior`` is True only if the maximum is a genuine interior turning
    point (not the very first or very last sample), i.e. the series rises then
    falls within the horizon.
    """
    k = int(np.argmax(series))
    interior = 0 < k < len(series) - 1
    return float(series[k]), float(t[k]), interior


def _decline_start(t: np.ndarray, series: np.ndarray) -> float:
    """First time after the peak at which the series is clearly falling.

    Defined as the peak time itself (the instant growth turns to decline). NaN
    if no interior peak exists.
    """
    _, t_peak, interior = _peak(t, series)
    return t_peak if interior else float("nan")


def run() -> int:
    os.makedirs(FIG_DIR, exist_ok=True)
    plt = _plt()

    base = sic.Params().with_(gamma=GAMMA_CALIBRATED)            # nu = 0
    vac = base.with_(nu=NU, l=L_WANE)                            # vaccine ON
    y0 = sic.initial_conditions(seed_A_m2=0.0, seed_I_m2=SEED_I_M2)

    R0 = compute_R0(base)
    p_c = 1.0 - 1.0 / R0
    ceiling = sic.waning_protection_ceiling(vac)

    print("=" * 74)
    print("Q(a)  Vaccination: peak & decline of HIV prevalence / incidence")
    print("=" * 74)
    print(f"  gamma = {GAMMA_CALIBRATED}/yr (mean infectious "
          f"{1/(base.mu+GAMMA_CALIBRATED):.1f} yr)   R0 = {R0:.3f}   "
          f"p_c = 1-1/R0 = {p_c:.3f}")
    print(f"  vaccine: nu = {NU}/yr, l = {L_WANE}/yr   "
          f"waning ceiling nu/(nu+l) = {ceiling:.3f}")
    print(f"  seed: I_m2 = {SEED_I_M2}")

    # Primary horizon runs
    res_b = sic.simulate(y0, HORIZON_YEARS, base, n_eval=N_EVAL)
    res_v = sic.simulate(y0, HORIZON_YEARS, vac, n_eval=N_EVAL)
    if not (res_b.success and res_v.success):
        print("  SOLVER FAILED:", res_b.message, "|", res_v.message)
        return 1
    aux_b = sic.auxiliaries(res_b)
    aux_v = sic.auxiliaries(res_v)
    t = aux_b["t"]

    # Long horizon (locate the true prevalence peak which can lie beyond 80 yr)
    res_bL = sic.simulate(y0, LONG_HORIZON, base, n_eval=N_EVAL)
    res_vL = sic.simulate(y0, LONG_HORIZON, vac, n_eval=N_EVAL)
    auxbL = sic.auxiliaries(res_bL)
    auxvL = sic.auxiliaries(res_vL)

    # ---- incidence peak/decline (the cleanest peak signal) ----
    inc_b_peak, inc_b_tp, _ = _peak(t, aux_b["incidence"])
    inc_v_peak, inc_v_tp, inc_v_interior = _peak(t, aux_v["incidence"])
    print("\n  INCIDENCE (new infections / yr):")
    print(f"    baseline peak = {inc_b_peak:7.1f}/yr @ t = {inc_b_tp:5.1f} yr;  "
          f"final({HORIZON_YEARS:.0f}yr) = {aux_b['incidence'][-1]:.1f}/yr")
    print(f"    vaccine  peak = {inc_v_peak:7.1f}/yr @ t = {inc_v_tp:5.1f} yr;  "
          f"final({HORIZON_YEARS:.0f}yr) = {aux_v['incidence'][-1]:.1f}/yr  "
          f"({'PEAKS then DECLINES' if inc_v_interior else 'monotone'})")
    print(f"    decline begins (vaccine) at t = {_decline_start(t, aux_v['incidence']):.1f} yr")
    inc_supp = 1.0 - inc_v_peak / inc_b_peak
    print(f"    peak incidence suppressed by {100*inc_supp:.0f}% vs baseline")

    # ---- prevalence peak/decline (slow S-I-death structure -> plateau) ----
    prev_b_peak, prev_b_tp, _ = _peak(auxbL["t"], auxbL["prev_overall"])
    prev_v_peak, prev_v_tp, prev_v_int = _peak(auxvL["t"], auxvL["prev_overall"])
    print("\n  PREVALENCE (overall (I+A)/living):")
    print(f"    baseline peak = {prev_b_peak:.3f} @ t = {prev_b_tp:.1f} yr "
          f"(then high endemic plateau)")
    print(f"    vaccine  peak = {prev_v_peak:.3f} @ t = {prev_v_tp:.1f} yr  "
          f"({'interior peak/decline' if prev_v_int else 'plateau'})")
    print(f"    vaccine holds prevalence at ~{prev_v_peak:.2f} vs baseline "
          f"~{prev_b_peak:.2f}  (~{100*(1-prev_v_peak/prev_b_peak):.0f}% lower ceiling)")

    # ---- effective transmission: incidence per susceptible (R_eff proxy) ----
    sus_v = res_v.get("S_f2") + res_v.get("S_m2")
    rate_v = np.where(sus_v > 0, aux_v["incidence"] / sus_v, 0.0)
    sus_b = res_b.get("S_f2") + res_b.get("S_m2")
    rate_b = np.where(sus_b > 0, aux_b["incidence"] / sus_b, 0.0)
    print("\n  PER-SUSCEPTIBLE HAZARD (force of infection proxy for R_eff):")
    print(f"    baseline final = {rate_b[-1]:.4f}/yr   vaccine final = {rate_v[-1]:.4f}/yr")

    # ---- protected fraction ----
    P = res_v.get("P_f2") + res_v.get("P_m2")
    age2 = (res_v.get("S_f2") + res_v.get("S_m2")
            + res_v.get("I_f2") + res_v.get("I_m2")
            + res_v.get("A_f2") + res_v.get("A_m2")
            + res_v.get("P_f2") + res_v.get("P_m2"))
    pfrac = np.where(age2 > 0, P / age2, 0.0)
    # fraction of the *eligible* (S or P) age-2 pool that is protected -> ceiling
    elig = res_v.get("S_f2") + res_v.get("S_m2") + P
    pfrac_elig = np.where(elig > 0, P / elig, 0.0)
    print("\n  PROTECTED FRACTION (vaccine):")
    print(f"    P/(age-2 living) final = {pfrac[-1]:.3f}")
    print(f"    P/(S+P age-2) final    = {pfrac_elig[-1]:.3f}  -> "
          f"ceiling nu/(nu+l) = {ceiling:.3f}")

    # =====================================================================
    # FIGURE 1: prevalence vaccinated vs baseline
    # =====================================================================
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    ax.plot(t, aux_b["prev_overall"], color="#b03a2e", lw=2.2, label="baseline (no vaccine)")
    ax.plot(t, aux_v["prev_overall"], color="#1f6f8b", lw=2.2, label=f"vaccine (nu={NU}, l={L_WANE})")
    ax.fill_between(t, aux_v["prev_overall"], aux_b["prev_overall"],
                    color="#1f6f8b", alpha=0.10)
    ax.set_xlabel("time (years)")
    ax.set_ylabel("HIV prevalence  (I+A)/living population")
    ax.set_title("Q(a) HIV prevalence: vaccination vs baseline")
    ax.set_xlim(0, HORIZON_YEARS)
    ax.set_ylim(0, max(0.5, aux_b["prev_overall"].max() * 1.1))
    ax.legend(loc="upper left")
    fig.tight_layout()
    f1 = os.path.join(FIG_DIR, "qa_prevalence.png")
    fig.savefig(f1)
    plt.close(fig)
    print(f"\n  saved {f1}")

    # =====================================================================
    # FIGURE 2: incidence vaccinated vs baseline (the clear peak+decline)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    ax.plot(t, aux_b["incidence"], color="#b03a2e", lw=2.2, label="baseline (no vaccine)")
    ax.plot(t, aux_v["incidence"], color="#1f6f8b", lw=2.2, label=f"vaccine (nu={NU}, l={L_WANE})")
    ax.scatter([inc_b_tp], [inc_b_peak], color="#b03a2e", zorder=5, s=40)
    ax.annotate(f"peak {inc_b_peak:.0f}/yr\n@ {inc_b_tp:.0f} yr",
                xy=(inc_b_tp, inc_b_peak), xytext=(inc_b_tp + 4, inc_b_peak * 0.9),
                fontsize=8, color="#b03a2e")
    ax.scatter([inc_v_tp], [inc_v_peak], color="#1f6f8b", zorder=5, s=40)
    ax.annotate(f"peak {inc_v_peak:.0f}/yr\n@ {inc_v_tp:.0f} yr, then declines",
                xy=(inc_v_tp, inc_v_peak), xytext=(inc_v_tp + 4, inc_v_peak + 90),
                fontsize=8, color="#1f6f8b")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("incidence  (new infections / year)")
    ax.set_title("Q(a) HIV incidence: vaccination drives a peak then decline")
    ax.set_xlim(0, HORIZON_YEARS)
    ax.set_ylim(0, inc_b_peak * 1.12)
    ax.legend(loc="upper right")
    fig.tight_layout()
    f2 = os.path.join(FIG_DIR, "qa_incidence.png")
    fig.savefig(f2)
    plt.close(fig)
    print(f"  saved {f2}")

    # =====================================================================
    # FIGURE 3: protected fraction saturating toward nu/(nu+l)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    ax.plot(t, pfrac_elig, color="#117a65", lw=2.2,
            label="P / (S+P), age-2  (eligible pool)")
    ax.plot(t, pfrac, color="#7d3c98", lw=1.8, ls="--",
            label="P / (all age-2 living)")
    ax.axhline(ceiling, color="#117a65", lw=1.0, ls=":",
               label=f"ceiling nu/(nu+l) = {ceiling:.3f}")
    ax.set_xlabel("time (years)")
    ax.set_ylabel("protected fraction of age-2")
    ax.set_title("Q(a) Vaccine-protected fraction saturates near nu/(nu+l)")
    ax.set_xlim(0, HORIZON_YEARS)
    ax.set_ylim(0, 1.0)
    ax.legend(loc="lower right")
    fig.tight_layout()
    f3 = os.path.join(FIG_DIR, "qa_protected_fraction.png")
    fig.savefig(f3)
    plt.close(fig)
    print(f"  saved {f3}")

    # ---- machine-readable summary block for the results write-up ----
    print("\n  SUMMARY (for qa_results.md):")
    print(f"    R0={R0:.3f}  p_c={p_c:.3f}  ceiling={ceiling:.3f}")
    print(f"    inc_baseline_peak={inc_b_peak:.1f}@{inc_b_tp:.1f}yr")
    print(f"    inc_vaccine_peak={inc_v_peak:.1f}@{inc_v_tp:.1f}yr "
          f"decline_from={inc_v_tp:.1f}yr final={aux_v['incidence'][-1]:.1f}")
    print(f"    prev_baseline_peak={prev_b_peak:.3f}@{prev_b_tp:.1f}yr")
    print(f"    prev_vaccine_peak={prev_v_peak:.3f}@{prev_v_tp:.1f}yr")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
