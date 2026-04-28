"""
BME5113 HW4 — Parameter Estimation, Growth Models, Model Discrimination,
              and Predator-Prey Validation
==============================================================================
Problem 1 (25%) Michaelis-Menten fit by 4 methods:
    (a) Lineweaver-Burke transform
    (b) Eadie-Hofstee transform
    (c) Levenberg-Marquardt (untransformed nonlinear LSQ)
    (d) Nelder-Mead simplex (untransformed nonlinear LSQ)

Problem 2 (25%) Boston-lettuce growth: fit Logistic and Gompertz to two
              lighting treatments (16-hr / 24-hr); derive AGR(t), RGR(t).

Problem 3 (25%) Reilly (1970) Fig 8.7 data — evaluate 4 candidate models by
              1:1 regression, paired t test, and Theil's U.

Problem 4 (25%) Harrison (1995) standard predator-prey model on Luckinbill's
              Didinium / Paramecium data (Luckinbill18*.dat). Compare model
              vs data with Chapter 8 statistics: 1:1 regression, paired t,
              Theil's U.

Outputs: ./hw4_figures/*.png ; printed parameter and statistics tables.
Run    : python hw4_solution.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit, minimize
from scipy.stats import t as student_t

# Chinese font fallback
for _font in ["Noto Sans CJK TC", "Microsoft JhengHei", "SimHei", "Arial Unicode MS"]:
    try:
        plt.rcParams["font.family"] = _font
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "hw4_figures")
os.makedirs(OUT, exist_ok=True)


# =====================================================================
# Generic statistics — Chapter 8 model-validation tools
# =====================================================================
@dataclass
class ValidationStats:
    """Container for the 1:1 regression, paired t test, and Theil's U."""

    n: int
    rmse: float
    mae: float
    bias: float                 # mean(pred - obs)
    r2_11: float                # 1:1 line R² (variance-explained reference = obs)
    slope: float                # OLS slope of pred on obs (target = 1)
    intercept: float            # OLS intercept of pred on obs (target = 0)
    slope_se: float
    intercept_se: float
    slope_t: float              # t for H0: slope = 1
    slope_p: float
    intercept_t: float          # t for H0: intercept = 0
    intercept_p: float
    paired_t: float             # paired t on residuals (H0: mean diff = 0)
    paired_p: float
    theil_u1: float             # 0..1, lower better (Theil's inequality coef)
    theil_u2: float             # vs naive forecast (lag-1 obs)


def validation_stats(obs: np.ndarray, pred: np.ndarray) -> ValidationStats:
    """Compute Chapter-8 style model-validation statistics.

    1:1 regression — fit pred = a + b·obs; ideally a=0, b=1.
    Paired t test  — H0: mean(pred − obs) = 0 (i.e. no systematic bias).
    Theil's U1     — sqrt(MSPE)/(sqrt(mean(pred²)) + sqrt(mean(obs²))).
    Theil's U2     — sqrt(sum(diff²)) / sqrt(sum((obs_t − obs_{t−1})²))
                     compares against naive 'no-change' forecast.
    """
    obs = np.asarray(obs, dtype=float)
    pred = np.asarray(pred, dtype=float)
    n = len(obs)
    diff = pred - obs
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    mae = float(np.mean(np.abs(diff)))
    bias = float(np.mean(diff))

    # 1:1 line "R²" using observations as reference (Spain Ch. 8)
    ss_res = float(np.sum(diff ** 2))
    ss_tot = float(np.sum((obs - np.mean(obs)) ** 2))
    r2_11 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    # OLS regression of pred on obs (target slope=1, intercept=0)
    x_mean = np.mean(obs)
    y_mean = np.mean(pred)
    Sxx = float(np.sum((obs - x_mean) ** 2))
    Sxy = float(np.sum((obs - x_mean) * (pred - y_mean)))
    slope = Sxy / Sxx if Sxx > 0 else float("nan")
    intercept = y_mean - slope * x_mean
    resid = pred - (intercept + slope * obs)
    df_reg = max(n - 2, 1)
    sigma2 = float(np.sum(resid ** 2) / df_reg)
    slope_se = float(np.sqrt(sigma2 / Sxx)) if Sxx > 0 else float("nan")
    intercept_se = float(np.sqrt(sigma2 * (1.0 / n + x_mean ** 2 / Sxx))) if Sxx > 0 else float("nan")
    slope_t = (slope - 1.0) / slope_se if slope_se > 0 else float("nan")
    intercept_t = (intercept - 0.0) / intercept_se if intercept_se > 0 else float("nan")
    slope_p = 2.0 * (1.0 - student_t.cdf(abs(slope_t), df_reg)) if np.isfinite(slope_t) else float("nan")
    intercept_p = 2.0 * (1.0 - student_t.cdf(abs(intercept_t), df_reg)) if np.isfinite(intercept_t) else float("nan")

    # Paired t test (one-sample on residuals)
    sd_diff = float(np.std(diff, ddof=1)) if n > 1 else float("nan")
    paired_t = bias / (sd_diff / np.sqrt(n)) if sd_diff > 0 else float("nan")
    df_t = n - 1
    paired_p = (
        2.0 * (1.0 - student_t.cdf(abs(paired_t), df_t)) if np.isfinite(paired_t) else float("nan")
    )

    # Theil's U1 (inequality coefficient) and U2 (vs naive lag-1)
    num = np.sqrt(np.mean(diff ** 2))
    den = np.sqrt(np.mean(pred ** 2)) + np.sqrt(np.mean(obs ** 2))
    theil_u1 = float(num / den) if den > 0 else float("nan")
    if n >= 2:
        naive = np.sqrt(np.sum((obs[1:] - obs[:-1]) ** 2))
        u2_num = np.sqrt(np.sum((pred[1:] - obs[1:]) ** 2))
        theil_u2 = float(u2_num / naive) if naive > 0 else float("nan")
    else:
        theil_u2 = float("nan")

    return ValidationStats(
        n=n, rmse=rmse, mae=mae, bias=bias, r2_11=r2_11,
        slope=slope, intercept=intercept,
        slope_se=slope_se, intercept_se=intercept_se,
        slope_t=slope_t, slope_p=slope_p,
        intercept_t=intercept_t, intercept_p=intercept_p,
        paired_t=paired_t, paired_p=paired_p,
        theil_u1=theil_u1, theil_u2=theil_u2,
    )


def print_stats(label: str, st: ValidationStats) -> None:
    print(f"  {label}")
    print(f"    n={st.n}  RMSE={st.rmse:.4g}  MAE={st.mae:.4g}  bias={st.bias:+.4g}")
    print(f"    1:1 R² (vs obs mean) = {st.r2_11:.4f}")
    print(f"    1:1 regression  slope = {st.slope:.4f} ± {st.slope_se:.4f}"
          f"   (t vs 1 = {st.slope_t:+.3f}, p = {st.slope_p:.3f})")
    print(f"                    intercept = {st.intercept:+.4g} ± {st.intercept_se:.4g}"
          f"   (t vs 0 = {st.intercept_t:+.3f}, p = {st.intercept_p:.3f})")
    print(f"    paired t (resid)  t = {st.paired_t:+.3f},  p = {st.paired_p:.3f}")
    print(f"    Theil  U1 = {st.theil_u1:.4f}    U2 (vs naive) = {st.theil_u2:.4f}")


# =====================================================================
# Problem 1 — Michaelis-Menten fitting by 4 methods
# =====================================================================
#
#   v(S) = V_max * S / (Km + S)
#
# (a) Lineweaver-Burke (double reciprocal):
#       1/v = (Km/V_max) (1/S) + 1/V_max
#     OLS of (1/S, 1/v) gives slope m, intercept b
#       V_max = 1/b,  Km = m·V_max = m/b
#
# (b) Eadie-Hofstee (the "v vs v/S" linearisation):
#       v = V_max  -  Km · (v/S)
#     OLS of (v/S, v) gives slope = -Km, intercept = V_max
#
# (c) Levenberg-Marquardt — scipy.optimize.curve_fit (untransformed, weight = 1)
#
# (d) Nelder-Mead simplex — scipy.optimize.minimize on SSE (untransformed)


PREY_S = np.array([4.0, 10.0, 30.0, 90.0, 173.0, 256.0])     # prey density (S)
PREY_V = np.array([2.5, 9.5, 12.5, 19.5, 21.5, 19.0])        # prey eaten (v)


def mm_model(S, Vmax, Km):
    return Vmax * S / (Km + S)


def fit_lineweaver_burke(S, v):
    x = 1.0 / S
    y = 1.0 / v
    A = np.vstack([x, np.ones_like(x)]).T
    (m, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    Vmax = 1.0 / b
    Km = m * Vmax
    return Vmax, Km


def fit_eadie_hofstee(S, v):
    # v = Vmax - Km * (v/S)
    x = v / S
    y = v.copy()
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, intercept), *_ = np.linalg.lstsq(A, y, rcond=None)
    Vmax = intercept
    Km = -slope
    return Vmax, Km


def fit_levenberg_marquardt(S, v, p0=(25.0, 50.0)):
    # scipy curve_fit defaults to LM when no bounds are passed.
    popt, _ = curve_fit(mm_model, S, v, p0=p0, method="lm", maxfev=20000)
    return float(popt[0]), float(popt[1])


def fit_nelder_mead(S, v, p0=(25.0, 50.0)):
    def sse(p):
        Vmax, Km = p
        if Km <= 0 or Vmax <= 0:
            return 1e12
        return float(np.sum((mm_model(S, Vmax, Km) - v) ** 2))
    res = minimize(sse, p0, method="Nelder-Mead",
                   options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 5000})
    return float(res.x[0]), float(res.x[1])


def problem1_michaelis_menten():
    print("=" * 72)
    print("Problem 1 — Michaelis-Menten by 4 methods")
    print("=" * 72)
    print("  Data: S =", PREY_S.tolist())
    print("        v =", PREY_V.tolist())

    methods = []
    methods.append(("(a) Lineweaver-Burke", *fit_lineweaver_burke(PREY_S, PREY_V)))
    methods.append(("(b) Eadie-Hofstee",   *fit_eadie_hofstee(PREY_S, PREY_V)))
    methods.append(("(c) Levenberg-Marquardt", *fit_levenberg_marquardt(PREY_S, PREY_V)))
    methods.append(("(d) Nelder-Mead simplex", *fit_nelder_mead(PREY_S, PREY_V)))

    print(f"\n  {'Method':28s} {'Vmax':>10s} {'Km':>10s}  {'SSE':>10s}  {'R²':>8s}")
    results = []
    for name, Vmax, Km in methods:
        v_pred = mm_model(PREY_S, Vmax, Km)
        sse = float(np.sum((v_pred - PREY_V) ** 2))
        ss_tot = float(np.sum((PREY_V - PREY_V.mean()) ** 2))
        r2 = 1 - sse / ss_tot
        results.append((name, Vmax, Km, sse, r2, v_pred))
        print(f"  {name:28s} {Vmax:10.4f} {Km:10.4f}  {sse:10.3f}  {r2:8.4f}")

    # Plot: data + 4 fits, plus the two transform plots
    S_grid = np.linspace(0.5, max(PREY_S) * 1.1, 300)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    ax = axes[0]
    ax.scatter(PREY_S, PREY_V, s=70, color="k", zorder=5, label="data")
    colors = ["#1565C0", "#2E7D32", "#EF6C00", "#C62828"]
    styles = ["-", "--", "-.", ":"]
    for (name, Vmax, Km, _sse, _r2, _vp), c, ls in zip(results, colors, styles):
        ax.plot(S_grid, mm_model(S_grid, Vmax, Km), ls, color=c, lw=2.0,
                label=f"{name}\n  Vmax={Vmax:.2f}, Km={Km:.2f}")
    ax.set_xlabel("Prey density S")
    ax.set_ylabel("Prey eaten v")
    ax.set_title("Michaelis-Menten fits — 4 methods")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)

    # Lineweaver-Burke plot
    ax = axes[1]
    ax.scatter(1.0 / PREY_S, 1.0 / PREY_V, s=60, color="k", zorder=5, label="data")
    Vmax_lb, Km_lb = methods[0][1], methods[0][2]
    x_lb = np.linspace(0, 1.0 / min(PREY_S) * 1.1, 100)
    ax.plot(x_lb, (Km_lb / Vmax_lb) * x_lb + 1.0 / Vmax_lb, "b-", lw=2.0,
            label=f"slope=Km/Vmax={Km_lb/Vmax_lb:.4f}\n"
                  f"intercept=1/Vmax={1/Vmax_lb:.4f}")
    ax.set_xlabel("1/S"); ax.set_ylabel("1/v")
    ax.set_title("(a) Lineweaver-Burke transform")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # Eadie-Hofstee plot
    ax = axes[2]
    ax.scatter(PREY_V / PREY_S, PREY_V, s=60, color="k", zorder=5, label="data")
    Vmax_eh, Km_eh = methods[1][1], methods[1][2]
    x_eh = np.linspace(0, max(PREY_V / PREY_S) * 1.1, 100)
    ax.plot(x_eh, Vmax_eh - Km_eh * x_eh, "g-", lw=2.0,
            label=f"slope=−Km={-Km_eh:.4f}\nintercept=Vmax={Vmax_eh:.4f}")
    ax.set_xlabel("v/S"); ax.set_ylabel("v")
    ax.set_title("(b) Eadie-Hofstee transform")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    fig.suptitle("Problem 1 — Michaelis-Menten parameter estimation",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_mm_fits.png"), dpi=140)
    plt.close(fig)
    print("  -> fig1_mm_fits.png")

    return results


# =====================================================================
# Problem 2 — Boston lettuce growth: Logistic vs Gompertz
# =====================================================================
#
# Three-parameter logistic (Paine et al. 2012, Table 1):
#   M(t)  = M0 K / (M0 + (K - M0) exp(-r t))
#   AGR   = dM/dt = r M (1 - M/K)            (function of M)
#         = r M0 K (K-M0) e^{-r t} / (M0 + (K-M0) e^{-r t})²   (function of t)
#   RGR   = AGR / M = r (1 - M/K) = r (K-M0) e^{-r t} / (M0 + (K-M0) e^{-r t})
#
# Gompertz (Paine et al. 2012, Table 1):
#   M(t)  = K (M0/K)^{exp(-r t)}        equivalently  K exp[-ln(K/M0) e^{-rt}]
#   AGR   = r M ln(K/M)
#   RGR   = r ln(K/M)
#
# We fit r, K (with M0 fixed at the first observation) by Levenberg-Marquardt.

def load_lettuce_excel(path: str):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    rows = [r for r in rows if r[0] is not None]
    t = np.array([float(r[0]) for r in rows])
    a = np.array([float(r[1]) for r in rows])     # 16-hr (curve A)
    b = np.array([float(r[2]) for r in rows])     # 24-hr (curve B)
    return t, a, b


def logistic_M(t, r, K, M0):
    return M0 * K / (M0 + (K - M0) * np.exp(-r * t))


def logistic_AGR_t(t, r, K, M0):
    e = np.exp(-r * t)
    denom = (M0 + (K - M0) * e) ** 2
    return r * M0 * K * (K - M0) * e / denom


def logistic_RGR_t(t, r, K, M0):
    e = np.exp(-r * t)
    M = M0 * K / (M0 + (K - M0) * e)
    return r * (1.0 - M / K)


def gompertz_M(t, r, K, M0):
    # M(t) = K * (M0/K)^{exp(-r t)}  =  K * exp(-ln(K/M0) * exp(-r t))
    return K * np.exp(-np.log(K / M0) * np.exp(-r * t))


def gompertz_AGR_t(t, r, K, M0):
    M = gompertz_M(t, r, K, M0)
    return r * M * np.log(K / np.maximum(M, 1e-12))


def gompertz_RGR_t(t, r, K, M0):
    M = gompertz_M(t, r, K, M0)
    return r * np.log(K / np.maximum(M, 1e-12))


def fit_growth(model_fn, t, M, M0, p0):
    f = lambda t, r, K: model_fn(t, r, K, M0)
    popt, pcov = curve_fit(f, t, M, p0=p0, maxfev=20000)
    return float(popt[0]), float(popt[1]), pcov


def problem2_lettuce():
    print("\n" + "=" * 72)
    print("Problem 2 — Boston lettuce growth (Logistic vs Gompertz)")
    print("=" * 72)
    t, A, B = load_lettuce_excel(os.path.join(HERE, "HW4-PROBLEM-2.xlsx"))
    print(f"  N = {len(t)} time points,  t in [{t.min():.2f}, {t.max():.2f}] days")
    print(f"  curve A (16-hr): M0 = {A[0]:.2f}, M_end = {A[-1]:.2f}")
    print(f"  curve B (24-hr): M0 = {B[0]:.2f}, M_end = {B[-1]:.2f}")

    fits = {}
    for name, M in [("16-hr (curve A)", A), ("24-hr (curve B)", B)]:
        M0 = M[0]
        print(f"\n  --- {name} ---  (M0 fixed at first obs = {M0:.3f})")

        # Logistic fit
        r_l, K_l, _ = fit_growth(logistic_M, t, M, M0, p0=(0.4, M.max() * 1.1))
        M_logistic = logistic_M(t, r_l, K_l, M0)
        st_l = validation_stats(M, M_logistic)
        # Gompertz fit
        r_g, K_g, _ = fit_growth(gompertz_M, t, M, M0, p0=(0.2, M.max() * 1.2))
        M_gompertz = gompertz_M(t, r_g, K_g, M0)
        st_g = validation_stats(M, M_gompertz)

        print(f"    Logistic : r = {r_l:.4f}/day,  K = {K_l:7.2f},  RMSE = {st_l.rmse:.3f}, R²= {st_l.r2_11:.4f}")
        print(f"    Gompertz : r = {r_g:.4f}/day,  K = {K_g:7.2f},  RMSE = {st_g.rmse:.3f}, R²= {st_g.r2_11:.4f}")

        # Closed-form characteristic growth-rate stats
        # Logistic: AGR max at M = K/2  =>  t = (1/r) ln((K-M0)/M0), AGR_max = rK/4
        t_peak_l = (1.0 / r_l) * np.log((K_l - M0) / M0) if M0 < K_l else float("nan")
        agr_max_l = r_l * K_l / 4.0
        # Gompertz: AGR max at M = K/e  =>  t = (1/r) ln(ln(K/M0)),  AGR_max = rK/e
        t_peak_g = (1.0 / r_g) * np.log(np.log(K_g / M0)) if M0 < K_g else float("nan")
        agr_max_g = r_g * K_g / np.e
        # RGR(0) and RGR at t_end
        rgr0_l = r_l * (1.0 - M0 / K_l)
        rgr_end_l = r_l * (1.0 - logistic_M(t[-1], r_l, K_l, M0) / K_l)
        rgr0_g = r_g * np.log(K_g / M0)
        rgr_end_g = r_g * np.log(K_g / gompertz_M(t[-1], r_g, K_g, M0))
        print(f"    Logistic AGR peak: t={t_peak_l:5.2f} d, AGR_max={agr_max_l:5.2f}; "
              f"RGR(0)={rgr0_l:.3f}, RGR(t_end)={rgr_end_l:.3f}")
        print(f"    Gompertz AGR peak: t={t_peak_g:5.2f} d, AGR_max={agr_max_g:5.2f}; "
              f"RGR(0)={rgr0_g:.3f}, RGR(t_end)={rgr_end_g:.3f}")

        fits[name] = dict(M0=M0, M=M, t=t,
                          logistic=(r_l, K_l, M_logistic, st_l),
                          gompertz=(r_g, K_g, M_gompertz, st_g))

    # ------------- Figures -------------
    t_grid = np.linspace(t.min(), t.max(), 400)

    # Fig 2a: data + fits for both treatments
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for row, (name, M) in enumerate([("16-hr (curve A)", A), ("24-hr (curve B)", B)]):
        f = fits[name]
        r_l, K_l, _, st_l = f["logistic"]
        r_g, K_g, _, st_g = f["gompertz"]
        M0 = f["M0"]

        ax = axes[row, 0]
        ax.scatter(t, M, s=35, color="k", zorder=5, label="data")
        ax.plot(t_grid, logistic_M(t_grid, r_l, K_l, M0), "b-", lw=2.0,
                label=f"Logistic\n  r={r_l:.3f}, K={K_l:.1f}\n  R²={st_l.r2_11:.3f}")
        ax.plot(t_grid, gompertz_M(t_grid, r_g, K_g, M0), "r--", lw=2.0,
                label=f"Gompertz\n  r={r_g:.3f}, K={K_g:.1f}\n  R²={st_g.r2_11:.3f}")
        ax.set_xlabel("Time (day)"); ax.set_ylabel("Projected leaf area (cm²)")
        ax.set_title(f"{name} — fits"); ax.grid(alpha=0.3); ax.legend(fontsize=8)

        ax = axes[row, 1]
        ax.plot(t_grid, logistic_AGR_t(t_grid, r_l, K_l, M0), "b-", lw=2.0,
                label="Logistic AGR")
        ax.plot(t_grid, gompertz_AGR_t(t_grid, r_g, K_g, M0), "r--", lw=2.0,
                label="Gompertz AGR")
        ax.set_xlabel("Time (day)"); ax.set_ylabel("AGR (cm²/day)")
        ax.set_title(f"{name} — AGR(t)"); ax.grid(alpha=0.3); ax.legend(fontsize=9)

        ax = axes[row, 2]
        ax.plot(t_grid, logistic_RGR_t(t_grid, r_l, K_l, M0), "b-", lw=2.0,
                label="Logistic RGR")
        ax.plot(t_grid, gompertz_RGR_t(t_grid, r_g, K_g, M0), "r--", lw=2.0,
                label="Gompertz RGR")
        ax.set_xlabel("Time (day)"); ax.set_ylabel("RGR (1/day)")
        ax.set_title(f"{name} — RGR(t)"); ax.grid(alpha=0.3); ax.legend(fontsize=9)

    fig.suptitle("Problem 2 — Boston lettuce: data, AGR(t), RGR(t)",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_lettuce_growth.png"), dpi=140)
    plt.close(fig)

    # Fig 2b: side-by-side comparison of two treatments using the *better* model
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    for name, M, color in [("16-hr (curve A)", A, "#1565C0"),
                           ("24-hr (curve B)", B, "#C62828")]:
        f = fits[name]
        r_g, K_g, _, _ = f["gompertz"]
        M0 = f["M0"]
        ax.scatter(t, M, s=30, color=color, alpha=0.6, label=f"{name} data")
        ax.plot(t_grid, gompertz_M(t_grid, r_g, K_g, M0), "-", color=color, lw=2.2,
                label=f"{name} Gompertz: r={r_g:.3f}, K={K_g:.1f}")
    ax.set_xlabel("Time (day)"); ax.set_ylabel("Projected leaf area (cm²)")
    ax.set_title("Treatment comparison — Gompertz fits"); ax.grid(alpha=0.3); ax.legend(fontsize=9)

    ax = axes[1]
    for name, color in [("16-hr (curve A)", "#1565C0"), ("24-hr (curve B)", "#C62828")]:
        f = fits[name]
        r_g, K_g, _, _ = f["gompertz"]
        M0 = f["M0"]
        ax.plot(t_grid, gompertz_RGR_t(t_grid, r_g, K_g, M0), "-",
                color=color, lw=2.2, label=f"{name}")
    ax.set_xlabel("Time (day)"); ax.set_ylabel("RGR (1/day)")
    ax.set_title("RGR(t) — both treatments (Gompertz)"); ax.grid(alpha=0.3); ax.legend(fontsize=9)
    fig.suptitle("Problem 2 — comparison of 16-hr vs 24-hr lighting", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2b_lettuce_compare.png"), dpi=140)
    plt.close(fig)
    print("\n  -> fig2_lettuce_growth.png, fig2b_lettuce_compare.png")
    return fits


# =====================================================================
# Problem 3 — Reilly (1970) Fig 8.7 model discrimination
# =====================================================================
#
# Reilly (1970) example data:
#   x = 0, 1, 2, 3
#   y = -1.290, 5.318, 7.049, 19.886
#
# Four candidate models (Spain Fig 8.7):
#   M1 — linear no-intercept:      y = a x
#   M2 — linear with intercept:    y = a + b x
#   M3 — exponential:              y = a exp(b x)
#   M4 — quadratic with intercept: y = a + b x + c x²
#
# Discrimination:
#   * 1:1 regression (slope vs 1, intercept vs 0)
#   * paired t test on residuals
#   * Theil's U  (smaller = better)

REILLY_X = np.array([0.0, 1.0, 2.0, 3.0])
REILLY_Y = np.array([-1.290, 5.318, 7.049, 19.886])


def fit_M1(x, y):
    a, *_ = np.linalg.lstsq(x.reshape(-1, 1), y, rcond=None)
    return float(a[0]),


def fit_M2(x, y):
    A = np.vstack([np.ones_like(x), x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0]), float(coef[1])


def fit_M3(x, y):
    # Nonlinear LM; LB initial guess from log-fit on positive y subset.
    pos = y > 0
    if pos.sum() >= 2:
        b0, log_a0 = np.polyfit(x[pos], np.log(y[pos]), 1)
        a0 = np.exp(log_a0)
        p0 = (a0, b0)
    else:
        p0 = (1.0, 1.0)
    popt, _ = curve_fit(lambda x, a, b: a * np.exp(b * x), x, y, p0=p0, maxfev=20000)
    return float(popt[0]), float(popt[1])


def fit_M4(x, y):
    A = np.vstack([np.ones_like(x), x, x ** 2]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0]), float(coef[1]), float(coef[2])


def problem3_reilly():
    print("\n" + "=" * 72)
    print("Problem 3 — Reilly (1970) Fig 8.7  ·  4-model discrimination")
    print("=" * 72)
    x, y = REILLY_X, REILLY_Y
    print(f"  data  x = {x.tolist()}")
    print(f"        y = {y.tolist()}")

    p1 = fit_M1(x, y)
    p2 = fit_M2(x, y)
    p3 = fit_M3(x, y)
    p4 = fit_M4(x, y)

    yhat = {
        "M1: y = a x":              p1[0] * x,
        "M2: y = a + b x":          p2[0] + p2[1] * x,
        "M3: y = a exp(b x)":       p3[0] * np.exp(p3[1] * x),
        "M4: y = a + b x + c x²":   p4[0] + p4[1] * x + p4[2] * x ** 2,
    }
    params = {
        "M1: y = a x":              f"a = {p1[0]:+.4f}",
        "M2: y = a + b x":          f"a = {p2[0]:+.4f}, b = {p2[1]:+.4f}",
        "M3: y = a exp(b x)":       f"a = {p3[0]:+.4f}, b = {p3[1]:+.4f}",
        "M4: y = a + b x + c x²":   f"a = {p4[0]:+.4f}, b = {p4[1]:+.4f}, c = {p4[2]:+.4f}",
    }

    stats = {}
    print()
    for name, yh in yhat.items():
        st = validation_stats(y, yh)
        stats[name] = st
        print(f"\n  ▶ {name}   ({params[name]})")
        print_stats("validation", st)

    # Ranking
    print("\n  Ranking summary (smaller is better for RMSE & U; closer to 1 / 0 better for slope / paired-p):")
    print(f"  {'Model':28s} {'RMSE':>8s} {'R²':>8s} {'slope':>8s} {'paired p':>10s} {'U1':>8s} {'U2':>10s}")
    for name, st in stats.items():
        print(f"  {name:28s} {st.rmse:8.3f} {st.r2_11:8.3f} {st.slope:8.3f} "
              f"{st.paired_p:10.3f} {st.theil_u1:8.4f} {st.theil_u2:10.4f}")

    # Figure
    x_grid = np.linspace(0, 3.2, 120)
    yh_grid = {
        "M1: y = a x":           p1[0] * x_grid,
        "M2: y = a + b x":       p2[0] + p2[1] * x_grid,
        "M3: y = a exp(b x)":    p3[0] * np.exp(p3[1] * x_grid),
        "M4: y = a + b x + c x²": p4[0] + p4[1] * x_grid + p4[2] * x_grid ** 2,
    }
    colors = ["#1565C0", "#2E7D32", "#C62828", "#6A1B9A"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    ax = axes[0]
    ax.scatter(x, y, s=80, color="k", zorder=5, label="Reilly data")
    for (name, yh), c in zip(yh_grid.items(), colors):
        ax.plot(x_grid, yh, "-", color=c, lw=2.0, label=name)
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.set_title("Reilly's Fig 8.7 — 4 candidate models")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # 1:1 plot
    ax = axes[1]
    lim = (min(y.min(), -3), max(y.max() * 1.05, 22))
    ax.plot(lim, lim, "k--", lw=1.0, label="1:1 line")
    for (name, yh), c, st in zip(yhat.items(), colors, stats.values()):
        ax.scatter(y, yh, s=70, color=c, marker="o", edgecolor="k",
                   label=f"{name} (U1={st.theil_u1:.3f})")
    ax.set_xlabel("Observed y"); ax.set_ylabel("Predicted ŷ")
    ax.set_title("1:1 plot — observed vs predicted")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    fig.suptitle("Problem 3 — Reilly (1970) Fig 8.7 model discrimination",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_reilly_models.png"), dpi=140)
    plt.close(fig)
    print("\n  -> fig3_reilly_models.png")
    return stats


# =====================================================================
# Problem 4 — Harrison (1995) standard predator-prey model
# =====================================================================
#
#   dx/dt = ρ (1 - x/K) x  -  ω y · x / (φ + x)            (prey, Paramecium)
#   dy/dt = σ y · x / (φ + x)  -  γ y                       (predator, Didinium)
#
#   ICs (Luckinbill 18-day, Harrison Table 1):  x(0)=15.0, y(0)=5.833
#   Parameters: ρ=1.85, K=898, ω=25.5, φ=284.1, σ=12.40, γ=2.07
#
# Compare to Luckinbill18_Paurelia.dat (prey) and Luckinbill18_Dnasutum.dat
# (predator) using Chapter 8 statistics.

H_PARAMS = dict(rho=1.85, K=898.0, omega=25.5, phi=284.1, sigma=12.40, gamma=2.07)
H_X0 = 15.0
H_Y0 = 5.833


def harrison_rhs(t, s, p):
    x, y = s
    x = max(x, 0.0)
    y = max(y, 0.0)
    fx = x / (p["phi"] + x) if (p["phi"] + x) > 0 else 0.0
    dx = p["rho"] * (1.0 - x / p["K"]) * x - p["omega"] * y * fx
    dy = p["sigma"] * y * fx - p["gamma"] * y
    return [dx, dy]


def load_dat(path: str):
    """Load a 'Day  #/ml' Luckinbill data file. Skips text header rows."""
    t_list, n_list = [], []
    with open(path, "r") as fh:
        for line in fh:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            try:
                t_list.append(float(parts[0]))
                n_list.append(float(parts[1]))
            except ValueError:
                continue
    return np.asarray(t_list), np.asarray(n_list)


def problem4_harrison():
    print("\n" + "=" * 72)
    print("Problem 4 — Harrison (1995) standard model vs Luckinbill 18-day data")
    print("=" * 72)
    print(f"  Parameters: ρ={H_PARAMS['rho']}, K={H_PARAMS['K']}, ω={H_PARAMS['omega']},"
          f" φ={H_PARAMS['phi']}, σ={H_PARAMS['sigma']}, γ={H_PARAMS['gamma']}")
    print(f"  ICs:        x(0) = {H_X0} (Paramecium/mL),  y(0) = {H_Y0} (Didinium/mL)")

    t_prey, x_obs = load_dat(os.path.join(HERE, "Luckinbill18_Paurelia.dat"))
    t_pred, y_obs = load_dat(os.path.join(HERE, "Luckinbill18_Dnasutum.dat"))
    t_max = float(max(t_prey.max(), t_pred.max())) + 0.5
    print(f"  Loaded prey n = {len(t_prey)}, predator n = {len(t_pred)},"
          f" t_max = {t_max:.2f}")

    sol = solve_ivp(
        lambda t, s: harrison_rhs(t, s, H_PARAMS),
        (0.0, t_max), [H_X0, H_Y0],
        method="LSODA", rtol=1e-8, atol=1e-10,
        dense_output=True, max_step=0.05,
    )
    t_grid = np.linspace(0.0, t_max, 1500)
    xy = sol.sol(t_grid)
    x_sim = xy[0]
    y_sim = xy[1]

    # Interpolate model at each observation time
    x_model_at_obs = np.interp(t_prey, t_grid, x_sim)
    y_model_at_obs = np.interp(t_pred, t_grid, y_sim)

    print("\n  Prey (Paramecium) validation:")
    st_prey = validation_stats(x_obs, x_model_at_obs)
    print_stats("model vs observed prey", st_prey)

    print("\n  Predator (Didinium) validation:")
    st_pred = validation_stats(y_obs, y_model_at_obs)
    print_stats("model vs observed predator", st_pred)

    # Combined (after rescaling so prey/predator weighted similarly)
    # Concatenate scaled values to give an overall figure of merit.
    sx = max(np.std(x_obs), 1.0)
    sy = max(np.std(y_obs), 1.0)
    obs_all = np.concatenate([x_obs / sx, y_obs / sy])
    pred_all = np.concatenate([x_model_at_obs / sx, y_model_at_obs / sy])
    st_all = validation_stats(obs_all, pred_all)
    print("\n  Joint (scaled) validation:")
    print_stats("model vs observed (combined, /σ)", st_all)

    # Equilibrium / nullcline algebra (for SOLUTION.md cross-check)
    rho = H_PARAMS["rho"]; K = H_PARAMS["K"]; omega = H_PARAMS["omega"]
    phi = H_PARAMS["phi"]; sigma = H_PARAMS["sigma"]; gamma = H_PARAMS["gamma"]
    x_star = gamma * phi / (sigma - gamma)
    y_star = (rho / omega) * (1.0 - x_star / K) * (phi + x_star)
    vertex = (K - phi) / 2.0
    print(f"\n  Equilibrium analysis:")
    print(f"    predator nullcline x* = γφ/(σ-γ) = {x_star:.3f}")
    print(f"    y* = (ρ/ω)(1 - x*/K)(φ + x*) = {y_star:.3f}")
    print(f"    prey nullcline vertex (K-φ)/2 = {vertex:.3f}")
    print(f"    Rosenzweig-MacArthur stability: x* > vertex ?  {x_star > vertex}"
          f"   (x*={x_star:.1f}, vertex={vertex:.1f}) -> "
          f"{'stable' if x_star > vertex else 'UNSTABLE'} equilibrium")

    # Figure
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9))

    ax = axes[0, 0]
    ax.plot(t_grid, x_sim, "b-", lw=2.0, label="Model: Paramecium x(t)")
    ax.scatter(t_prey, x_obs, s=30, color="b", marker="o", alpha=0.6, label="Luckinbill data")
    ax.set_xlabel("Time (day)"); ax.set_ylabel("Paramecium / mL")
    ax.set_title("Prey: Paramecium (model vs data)"); ax.grid(alpha=0.3); ax.legend(fontsize=9)

    ax = axes[0, 1]
    ax.plot(t_grid, y_sim, "r-", lw=2.0, label="Model: Didinium y(t)")
    ax.scatter(t_pred, y_obs, s=30, color="r", marker="s", alpha=0.6, label="Luckinbill data")
    ax.set_xlabel("Time (day)"); ax.set_ylabel("Didinium / mL")
    ax.set_title("Predator: Didinium (model vs data)"); ax.grid(alpha=0.3); ax.legend(fontsize=9)

    # 1:1 plot
    ax = axes[1, 0]
    lo = 0; hi = max(x_obs.max(), x_model_at_obs.max()) * 1.05
    ax.plot([lo, hi], [lo, hi], "k--", lw=1.0)
    ax.scatter(x_obs, x_model_at_obs, s=40, color="b", alpha=0.7,
               label=f"prey  R²={st_prey.r2_11:.3f}, U1={st_prey.theil_u1:.3f}")
    ax.set_xlabel("Observed prey"); ax.set_ylabel("Modelled prey")
    ax.set_title("1:1 plot — prey"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    ax = axes[1, 1]
    lo = 0; hi = max(y_obs.max(), y_model_at_obs.max()) * 1.05
    ax.plot([lo, hi], [lo, hi], "k--", lw=1.0)
    ax.scatter(y_obs, y_model_at_obs, s=40, color="r", alpha=0.7,
               label=f"predator  R²={st_pred.r2_11:.3f}, U1={st_pred.theil_u1:.3f}")
    ax.set_xlabel("Observed predator"); ax.set_ylabel("Modelled predator")
    ax.set_title("1:1 plot — predator"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    fig.suptitle("Problem 4 — Harrison (1995) standard model vs Luckinbill 18-day data",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_harrison_validation.png"), dpi=140)
    plt.close(fig)

    # phase-plane figure
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.plot(x_sim, y_sim, "k-", lw=1.0, alpha=0.7, label="model trajectory")
    ax.scatter(x_obs, np.interp(t_prey, t_pred, y_obs)
               if len(t_prey) > 1 and len(t_pred) > 1 else y_obs[: len(x_obs)],
               s=20, color="b", alpha=0.4, label="observed (prey-time grid)")
    # nullclines of the basic model
    K = H_PARAMS["K"]; phi = H_PARAMS["phi"]; rho = H_PARAMS["rho"]; omega = H_PARAMS["omega"]
    sigma = H_PARAMS["sigma"]; gamma = H_PARAMS["gamma"]
    x_n = np.linspace(0.5, K, 400)
    y_xnull = rho / omega * (1.0 - x_n / K) * (phi + x_n)
    ax.plot(x_n, y_xnull, "g--", lw=1.5, label="prey nullcline dx/dt = 0")
    x_pnull = gamma * phi / (sigma - gamma) if sigma > gamma else None
    if x_pnull is not None and 0 < x_pnull < K:
        ax.axvline(x_pnull, color="m", ls="--", lw=1.5, label=f"predator nullcline x*={x_pnull:.1f}")
    ax.set_xlabel("Prey x (Paramecium/mL)"); ax.set_ylabel("Predator y (Didinium/mL)")
    ax.set_title("Phase plane — Harrison standard model")
    ax.grid(alpha=0.3); ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4b_harrison_phase.png"), dpi=140)
    plt.close(fig)
    print("\n  -> fig4_harrison_validation.png, fig4b_harrison_phase.png")
    return st_prey, st_pred, st_all


# =====================================================================
# Main
# =====================================================================
if __name__ == "__main__":
    print(f"Output directory: {OUT}\n")
    problem1_michaelis_menten()
    problem2_lettuce()
    problem3_reilly()
    problem4_harrison()
    print(f"\nDone. Figures in {OUT}/")
