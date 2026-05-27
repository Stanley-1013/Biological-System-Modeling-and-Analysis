"""
BME5113 Biological Systems Modeling and Analysis — Homework 5
=============================================================

Problem 1: Variance propagation (Eq. 9.3 + Table 9.2)
Problem 2: Parameter perturbation sensitivity for extinction model (Eq. 9.4)
Problem 3: Local stability analysis of Gause Case III (Fig. 9.11c)
Problem 4: Nullclines, equilibria, and stability of a 2-variable system

Outputs: figures in hw5_figures/, numeric summary on stdout
"""

import os
from pathlib import Path

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow

FIG_DIR = Path(__file__).parent / "hw5_figures"
FIG_DIR.mkdir(exist_ok=True)


# ============================================================
# Problem 1 — Error propagation: Eq. 9.3 with Table 9.2 logic
# ============================================================
def problem1():
    """Symbolic variance propagation for the three given z = f(...) forms.

    The general formula (Eq. 9.3, p. 186):
        var(z) ≈ Σ_i Σ_j (∂f/∂x_i)(∂f/∂x_j) ⟨(x_i - x̄_i)(x_j - x̄_j)⟩
    With ⟨(x-x̄)²⟩ = σ_x²  and  ⟨(x-x̄)(y-ȳ)⟩ = σ_xy (=0 if uncorrelated).
    """
    print("\n" + "=" * 60)
    print("Problem 1: Error propagation (Eq. 9.3 + Table 9.2 logic)")
    print("=" * 60)

    # ------ (1)  z = exp(k1 * x) ------
    x, k1, sx, sk1, sxk1 = sp.symbols("x k_1 sigma_x sigma_{k_1} sigma_{xk_1}", real=True)
    z1 = sp.exp(k1 * x)
    dz_dk1 = sp.diff(z1, k1)
    dz_dx  = sp.diff(z1, x)
    var1_uncorr = dz_dk1**2 * sk1**2 + dz_dx**2 * sx**2
    var1_corr   = dz_dk1**2 * sk1**2 + dz_dx**2 * sx**2 + 2 * dz_dk1 * dz_dx * sxk1

    print("\n(1) z = exp(k1*x)")
    print("    ∂z/∂k1 =", dz_dk1, "    ∂z/∂x =", dz_dx)
    print("    var(z) [uncorr]  =", sp.simplify(var1_uncorr))
    print("    var(z) [corr]    =", sp.simplify(var1_corr))

    # ------ (2)  z = k1*cos(k2*x) + k3*sin(k4*y) ------
    k2, k3, k4, y = sp.symbols("k_2 k_3 k_4 y", real=True)
    sk2, sk3, sk4, sy = sp.symbols("sigma_{k_2} sigma_{k_3} sigma_{k_4} sigma_y", real=True)
    sxy = sp.symbols("sigma_{xy}", real=True)
    z2 = k1 * sp.cos(k2 * x) + k3 * sp.sin(k4 * y)
    # Variables: k1, k2, k3, k4, x, y  (6 vars)
    var2_uncorr = (
        sp.diff(z2, k1) ** 2 * sk1 ** 2
        + sp.diff(z2, k2) ** 2 * sk2 ** 2
        + sp.diff(z2, k3) ** 2 * sk3 ** 2
        + sp.diff(z2, k4) ** 2 * sk4 ** 2
        + sp.diff(z2, x ) ** 2 * sx  ** 2
        + sp.diff(z2, y ) ** 2 * sy  ** 2
    )
    var2_corr = var2_uncorr + 2 * sp.diff(z2, x) * sp.diff(z2, y) * sxy
    print("\n(2) z = k1*cos(k2*x) + k3*sin(k4*y)")
    print("    var(z) [uncorr] =")
    sp.pprint(sp.simplify(var2_uncorr))
    print("    extra correlated cross-term (x,y only):  2(∂z/∂x)(∂z/∂y)σ_xy =")
    sp.pprint(2 * sp.diff(z2, x) * sp.diff(z2, y) * sxy)

    # ------ (3)  z = x^3 * y^{-3} ------
    z3 = x ** 3 * y ** (-3)
    dz3_dx, dz3_dy = sp.diff(z3, x), sp.diff(z3, y)
    var3_uncorr = dz3_dx ** 2 * sx ** 2 + dz3_dy ** 2 * sy ** 2
    var3_corr   = var3_uncorr + 2 * dz3_dx * dz3_dy * sxy

    print("\n(3) z = x^3 * y^(-3)")
    print("    ∂z/∂x =", dz3_dx, "    ∂z/∂y =", dz3_dy)
    print("    var(z) [uncorr] =")
    sp.pprint(sp.simplify(var3_uncorr))
    print("    var(z) [corr]   =")
    sp.pprint(sp.simplify(var3_corr))

    # Numerical illustration with arbitrary means (x̄=2, ȳ=1, σ_x=0.1, σ_y=0.05, σ_xy=±0.003)
    subs_nom = {x: 2.0, y: 1.0, sx: 0.1, sy: 0.05, sxy: 0.003}
    print("\nNumeric illustration (x̄=2, ȳ=1, σx=0.1, σy=0.05, σxy=0.003):")
    print("  (3) uncorr var(z) =", float(var3_uncorr.subs(subs_nom)))
    print("  (3) corr   var(z) =", float(var3_corr.subs(subs_nom)))


# ============================================================
# Problem 2 — Perturbation sensitivity on the extinction model
# ============================================================
def extinction_P(d, b, n):
    return (d / b) ** n


def var_P_analytical(d, b, n, sd, sb, sn):
    """Eq. 9.5 (textbook, p.188) — uncorrelated form."""
    # ∂P/∂d = n*d^{n-1}/b^n
    dP_dd = n * d ** (n - 1) / b ** n
    # ∂P/∂b = -n*d^n / b^{n+1}
    dP_db = -n * d ** n / b ** (n + 1)
    # ∂P/∂n = (d/b)^n * ln(d/b)
    dP_dn = (d / b) ** n * np.log(d / b)
    return dP_dd ** 2 * sd ** 2 + dP_db ** 2 * sb ** 2 + dP_dn ** 2 * sn ** 2


def problem2(seed=20260527):
    print("\n" + "=" * 60)
    print("Problem 2: Sensitivity of extinction P = (d/b)^n  (Eq. 9.4)")
    print("=" * 60)

    means = {"d": 0.8, "b": 0.9, "n": 10.0}
    stds  = {"d": 0.157, "b": 0.174, "n": 0.69}

    P_nominal = extinction_P(**means)
    print(f"Nominal P (Eq 9.4) = {P_nominal:.4f}")

    # (a) Eq. 9.1 single-parameter sensitivity index
    # S = ((R_a - R_n)/R_n) / ((P_a - P_n)/P_n)
    perturb_levels = [0.02, 0.10, 0.20]
    param_names = ["d", "b", "n"]

    sens_table = {}  # {param: {level: (S_plus, S_minus)}}
    for p in param_names:
        sens_table[p] = {}
        for lvl in perturb_levels:
            mp_plus  = dict(means); mp_plus[p]  = means[p] * (1 + lvl)
            mp_minus = dict(means); mp_minus[p] = means[p] * (1 - lvl)
            R_plus  = extinction_P(**mp_plus)
            R_minus = extinction_P(**mp_minus)
            S_plus  = ((R_plus  - P_nominal) / P_nominal) / lvl
            S_minus = ((R_minus - P_nominal) / P_nominal) / (-lvl)
            sens_table[p][lvl] = (S_plus, S_minus, R_plus, R_minus)

    # print table
    print("\nSingle-parameter sensitivity S (Eq. 9.1):")
    print(f"{'param':<6}{'level':>8}{'R+':>10}{'R-':>10}{'S+':>10}{'S-':>10}")
    for p in param_names:
        for lvl in perturb_levels:
            S_plus, S_minus, R_plus, R_minus = sens_table[p][lvl]
            print(f"{p:<6}{lvl*100:>7.0f}%{R_plus:>10.4f}{R_minus:>10.4f}"
                  f"{S_plus:>10.4f}{S_minus:>10.4f}")

    # Average |S| across levels and directions for ranking
    avg_abs_S = {}
    for p in param_names:
        vals = []
        for lvl in perturb_levels:
            vals.append(abs(sens_table[p][lvl][0]))
            vals.append(abs(sens_table[p][lvl][1]))
        avg_abs_S[p] = float(np.mean(vals))
    ranking = sorted(avg_abs_S.items(), key=lambda kv: kv[1], reverse=True)
    print("\nRanking by mean |S| across all perturbations:")
    for rank, (p, S) in enumerate(ranking, 1):
        print(f"  {rank}. {p}: mean |S| = {S:.4f}")

    # (b) Analytical variance (Eq. 9.5)
    varP_an = var_P_analytical(means["d"], means["b"], means["n"],
                               stds["d"], stds["b"], stds["n"])
    print(f"\nAnalytical var(P) [Eq. 9.5] = {varP_an:.4f}  →  σ_P = {np.sqrt(varP_an):.4f}")
    print(f"95% CI (normal approx)     = "
          f"[{P_nominal - 1.96*np.sqrt(varP_an):.3f}, "
          f"{P_nominal + 1.96*np.sqrt(varP_an):.3f}]")

    # individual analytical contributions
    d, b, n = means["d"], means["b"], means["n"]
    dP_dd = n * d ** (n - 1) / b ** n
    dP_db = -n * d ** n / b ** (n + 1)
    dP_dn = (d / b) ** n * np.log(d / b)
    contrib = {
        "d": (dP_dd ** 2) * stds["d"] ** 2,
        "b": (dP_db ** 2) * stds["b"] ** 2,
        "n": (dP_dn ** 2) * stds["n"] ** 2,
    }
    total = sum(contrib.values())
    print("\nVariance contribution shares (Eq. 9.5 term-by-term):")
    for p in param_names:
        print(f"  {p}: {contrib[p]:.4f}  ({100*contrib[p]/total:.1f}%)")

    # (c) Monte Carlo error analysis with log-normal samples & rejection (d<b)
    rng = np.random.default_rng(seed)
    n_mc = 10_000

    def lognormal_with_mean_std(mean, std, size):
        # parametrize log-normal via desired mean & std
        var = std ** 2
        mu = np.log(mean ** 2 / np.sqrt(var + mean ** 2))
        sigma = np.sqrt(np.log(1 + var / mean ** 2))
        return rng.lognormal(mu, sigma, size=size)

    accepted = []
    batch = 20_000
    while len(accepted) < n_mc:
        d_s = lognormal_with_mean_std(means["d"], stds["d"], batch)
        b_s = lognormal_with_mean_std(means["b"], stds["b"], batch)
        n_s = lognormal_with_mean_std(means["n"], stds["n"], batch)
        mask = d_s < b_s
        for tup in zip(d_s[mask], b_s[mask], n_s[mask]):
            accepted.append(tup)
            if len(accepted) >= n_mc:
                break
    arr = np.array(accepted)
    P_mc = (arr[:, 0] / arr[:, 1]) ** arr[:, 2]
    P_mc = P_mc[np.isfinite(P_mc) & (P_mc <= 1.0) & (P_mc >= 0.0)]
    print(f"\nMonte Carlo (N={len(P_mc)}):  mean={P_mc.mean():.4f}  "
          f"median={np.median(P_mc):.4f}  std={P_mc.std():.4f}")
    print(f"  2.5%, 97.5% percentiles: "
          f"[{np.percentile(P_mc, 2.5):.4f}, {np.percentile(P_mc, 97.5):.4f}]")

    # ---- Figures ----
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    # Bar plot: |S| by parameter and level
    width = 0.25
    xs = np.arange(len(param_names))
    for j, lvl in enumerate(perturb_levels):
        ys = [0.5 * (abs(sens_table[p][lvl][0]) + abs(sens_table[p][lvl][1]))
              for p in param_names]
        axes[0].bar(xs + (j - 1) * width, ys, width, label=f"{int(lvl*100)}%")
    axes[0].set_xticks(xs); axes[0].set_xticklabels(param_names)
    axes[0].set_xlabel("Parameter"); axes[0].set_ylabel("mean |S| ((R+,R-) averaged)")
    axes[0].set_title("Single-parameter sensitivity (Eq. 9.1)")
    axes[0].legend(title="Perturbation level"); axes[0].grid(alpha=0.3)

    # Monte Carlo histogram
    axes[1].hist(P_mc, bins=60, color="#2c7fb8", alpha=0.85, edgecolor="white")
    axes[1].axvline(P_nominal, color="red", lw=2, label=f"Deterministic = {P_nominal:.3f}")
    axes[1].axvline(P_mc.mean(), color="green", lw=2, ls="--",
                    label=f"MC mean = {P_mc.mean():.3f}")
    axes[1].axvline(np.percentile(P_mc, 2.5), color="black", lw=1, ls=":")
    axes[1].axvline(np.percentile(P_mc, 97.5), color="black", lw=1, ls=":",
                    label="2.5 / 97.5 percentile")
    axes[1].set_xlabel("Extinction probability P"); axes[1].set_ylabel("frequency")
    axes[1].set_title("Monte Carlo error analysis (Eq. 9.4)")
    axes[1].legend()
    plt.tight_layout(); plt.savefig(FIG_DIR / "fig2_problem2_sensitivity_mc.png", dpi=160)
    plt.close()

    return sens_table, varP_an, P_mc


# ============================================================
# Problem 3 — Gause Case III, local stability
# ============================================================
def gause_rhs(t, state, r1, K1, alpha, r2, K2, beta):
    n1, n2 = state
    dn1 = r1 * n1 * (1 - (n1 + alpha * n2) / K1)
    dn2 = r2 * n2 * (1 - (n2 + beta  * n1) / K2)
    return np.array([dn1, dn2])


def gause_jacobian(n1, n2, r1, K1, alpha, r2, K2, beta):
    """Eq. 9.40a/b textbook p.207."""
    J11 = r1 - 2 * r1 * n1 / K1 - r1 * n2 * alpha / K1
    J12 = -r1 * n1 * alpha / K1
    J21 = -r2 * n2 * beta / K2
    J22 = r2 - 2 * r2 * n2 / K2 - r2 * n1 * beta / K2
    return np.array([[J11, J12], [J21, J22]])


def problem3():
    print("\n" + "=" * 60)
    print("Problem 3: Gause Case III — local stability (Fig. 9.11c)")
    print("=" * 60)

    r1, K1, alpha = 0.05, 200.0, 0.2
    r2, K2, beta  = 0.05, 800.0, 3.0          # problem says K2=800, β=3

    # Case condition checks: Case III ⇔ K1/α > K2 AND K2/β > K1
    print(f"  K1/α = {K1/alpha:.2f}  >  K2 = {K2:.2f}?  {K1/alpha > K2}")
    print(f"  K2/β = {K2/beta:.2f}  >  K1 = {K1:.2f}?  {K2/beta > K1}")

    # Equilibria (Eq. 9.17, 9.18)
    n1_star = (K1 - alpha * K2) / (1 - alpha * beta)
    n2_star = (K2 - beta  * K1) / (1 - alpha * beta)
    print(f"  coexistence eq (Eq 9.17/9.18):  n1* = {n1_star},  n2* = {n2_star}")

    equilibria = {
        "(0,0)":       (0.0, 0.0),
        "(K1,0)":      (K1, 0.0),
        "(0,K2)":      (0.0, K2),
        "(n1*,n2*)":   (n1_star, n2_star),
    }

    for label, (n1, n2) in equilibria.items():
        J = gause_jacobian(n1, n2, r1, K1, alpha, r2, K2, beta)
        eigs = np.linalg.eigvals(J)
        tr, det = J.trace(), np.linalg.det(J)
        # classify
        if np.iscomplexobj(eigs) and np.any(np.iscomplex(eigs)) and not np.all(np.isreal(eigs)):
            kind = "spiral"
        else:
            real = eigs.real
            if np.all(real < 0): kind = "stable node"
            elif np.all(real > 0): kind = "unstable node"
            elif np.any(real > 0) and np.any(real < 0): kind = "saddle"
            else: kind = "non-hyperbolic"
        print(f"  {label} at {n1, n2}")
        print(f"    J = {J.tolist()}")
        print(f"    tr={tr:.5f}, det={det:.6f}, eigs={eigs}, kind={kind}")

    # ---- Figure: nullclines + flow field ----
    fig, ax = plt.subplots(figsize=(9, 8))
    n1g = np.linspace(0, 1100, 30)
    n2g = np.linspace(0, 1100, 30)
    N1, N2 = np.meshgrid(n1g, n2g)
    DN1 = r1 * N1 * (1 - (N1 + alpha * N2) / K1)
    DN2 = r2 * N2 * (1 - (N2 + beta  * N1) / K2)
    mag = np.sqrt(DN1 ** 2 + DN2 ** 2) + 1e-12
    ax.streamplot(N1, N2, DN1, DN2, density=1.2,
                  color=np.log10(mag), cmap="viridis", linewidth=0.7)

    # nullclines:  n2 = (K1 - n1)/α   for dn1/dt = 0 (non-trivial)
    #             n2 = K2 - β*n1      for dn2/dt = 0 (non-trivial)
    x_line = np.linspace(0, 1100, 200)
    null_n1 = (K1 - x_line) / alpha      # solve K1 = n1 + α n2 for n2
    null_n2 = K2 - beta * x_line         # solve K2 = n2 + β n1 for n2
    ax.plot(x_line, null_n1, "b-", lw=2.5,
            label=r"$dn_1/dt = 0$: $n_2 = (K_1-n_1)/\alpha$ — flow ⟂")
    ax.plot(x_line, null_n2, "r-", lw=2.5,
            label=r"$dn_2/dt = 0$: $n_2 = K_2-\beta n_1$ — flow ‖")
    ax.axvline(0, color="b", ls="--", alpha=0.6, lw=2,
               label="$n_1=0$ nullcline (n2 only)")
    ax.axhline(0, color="r", ls="--", alpha=0.6, lw=2,
               label="$n_2=0$ nullcline (n1 only)")

    # ---- Vectors on nullclines (one arrow per segment, magnitude-encoded) ----
    # On dn1/dt = 0 (blue line, non-trivial): motion only in n2 (vertical arrows)
    for n1_pt in [50, 150, 250, 400, 600, 800]:
        n2_pt = (K1 - n1_pt) / alpha
        if 0 <= n2_pt <= 1050:
            dn2 = r2 * n2_pt * (1 - (n2_pt + beta * n1_pt) / K2)
            arr_len = 80 * np.sign(dn2)
            if abs(arr_len) > 0:
                ax.annotate("", xy=(n1_pt, n2_pt + arr_len),
                            xytext=(n1_pt, n2_pt),
                            arrowprops=dict(arrowstyle="->", color="blue",
                                            lw=2, alpha=0.7))
    # On dn2/dt = 0 (red line, non-trivial): motion only in n1 (horizontal arrows)
    for n1_pt in [30, 80, 150, 220]:
        n2_pt = K2 - beta * n1_pt
        if 0 <= n2_pt <= 1050:
            dn1 = r1 * n1_pt * (1 - (n1_pt + alpha * n2_pt) / K1)
            arr_len = 60 * np.sign(dn1)
            if abs(arr_len) > 0:
                ax.annotate("", xy=(n1_pt + arr_len, n2_pt),
                            xytext=(n1_pt, n2_pt),
                            arrowprops=dict(arrowstyle="->", color="red",
                                            lw=2, alpha=0.7))

    # mark equilibria
    for label, (n1, n2) in equilibria.items():
        marker = "ro" if "n1*" in label else "ks"
        ax.plot(n1, n2, marker, ms=10, mfc="yellow" if "n1*" in label else "white")
        ax.annotate(label, (n1, n2), xytext=(8, 8),
                    textcoords="offset points", fontsize=10)

    ax.set_xlim(-30, 1100); ax.set_ylim(-30, 1100)
    ax.set_xlabel(r"$n_1$"); ax.set_ylabel(r"$n_2$")
    ax.set_title("Problem 3 — Gause Case III (K1=200, α=0.2, K2=800, β=3)\n"
                 "stable coexistence at (n1*, n2*) = (100, 500)")
    ax.legend(loc="upper right", fontsize=9); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig(FIG_DIR / "fig3_problem3_gause_caseIII.png", dpi=160)
    plt.close()


# ============================================================
# Problem 4 — Custom 2-D system
# ============================================================
def problem4():
    print("\n" + "=" * 60)
    print("Problem 4: 2-D system — nullclines, equilibria, stability")
    print("=" * 60)

    a1, a2, b, d, f = 1.0, 0.05, 5.0, 1.0, 10.0
    print(f"Parameters: a1={a1}, a2={a2}, b={b}, d={d}, f={f}")

    # Symbolic equilibrium (general form)
    x, y, A1, A2, B, D, F = sp.symbols("x y a1 a2 b d f", positive=True)
    f1 = A1 * x ** 2 - A2 * x ** 3 - B * x * y
    f2 = D * x * y - F * y ** 2
    eq_solutions = sp.solve([f1, f2], [x, y], dict=True)
    print("Symbolic equilibria (sympy):")
    for sol in eq_solutions:
        print("  ", sol)

    # Manually verified equilibria (numerical):
    equilibria = {
        "(0,0)":        (0.0, 0.0),
        "(a1/a2, 0)":  (a1 / a2, 0.0),
        "(x*, y*)":    ((a1*f - b*d) / (a2*f), d*(a1*f - b*d) / (a2*f**2)),
    }
    print("\nNumeric equilibria:")
    for k, v in equilibria.items():
        print(f"  {k} = {v}")

    # Jacobian
    J_sym = sp.Matrix([
        [sp.diff(f1, x), sp.diff(f1, y)],
        [sp.diff(f2, x), sp.diff(f2, y)],
    ])
    print("\nSymbolic Jacobian:")
    sp.pprint(J_sym)

    # Evaluate Jacobian at each equilibrium (numerical)
    def J_num(x_val, y_val):
        return np.array([
            [2 * a1 * x_val - 3 * a2 * x_val ** 2 - b * y_val, -b * x_val],
            [d * y_val,                                          d * x_val - 2 * f * y_val],
        ])

    for label, (x_val, y_val) in equilibria.items():
        J = J_num(x_val, y_val)
        eigs = np.linalg.eigvals(J)
        tr, det = J.trace(), np.linalg.det(J)
        disc = tr * tr - 4 * det
        if np.allclose(J, 0):
            kind = "degenerate (all zero Jacobian)"
        elif disc < 0:
            kind = "stable spiral" if tr < 0 else ("unstable spiral" if tr > 0 else "center")
        elif disc == 0:
            kind = "degenerate node"
        else:
            if det < 0:
                kind = "saddle"
            elif tr < 0:
                kind = "stable node"
            elif tr > 0:
                kind = "unstable node"
            else:
                kind = "degenerate"
        print(f"  {label}: J={J.tolist()}, tr={tr:.4f}, det={det:.4f}, "
              f"eigs={eigs}, kind={kind}")

    # ---- Figure: nullclines + flow with vector arrows on each nullcline ----
    fig, ax = plt.subplots(figsize=(10, 7.5))
    xg = np.linspace(0, 25, 30)
    yg = np.linspace(0, 4, 25)
    X, Y = np.meshgrid(xg, yg)
    DX = a1 * X ** 2 - a2 * X ** 3 - b * X * Y
    DY = d * X * Y - f * Y ** 2
    M = np.sqrt(DX ** 2 + DY ** 2) + 1e-12
    ax.streamplot(X, Y, DX, DY, density=1.4,
                  color=np.log10(M), cmap="viridis", linewidth=0.7)

    # Nullclines
    x_line = np.linspace(0.01, 25, 400)
    # dx/dt = 0:  x=0  OR  y = (a1*x - a2*x^2)/b
    y_parab = (a1 * x_line - a2 * x_line ** 2) / b
    mask = y_parab >= -0.05
    ax.plot(x_line[mask], y_parab[mask], "b-", lw=2.5,
            label=r"$\dot x=0$: $y=(a_1 x - a_2 x^2)/b$ (parabola)")
    ax.axvline(0, color="b", ls="--", alpha=0.7, lw=2,
               label=r"$\dot x=0$: $x=0$ (y-axis)")
    # dy/dt = 0:  y = 0  OR  y = d*x/f
    y_line2 = d * x_line / f
    ax.plot(x_line, y_line2, "r-", lw=2.5,
            label=r"$\dot y=0$: $y=dx/f$ (line)")
    ax.axhline(0, color="r", ls="--", alpha=0.7, lw=2,
               label=r"$\dot y=0$: $y=0$ (x-axis)")

    # ---- Arrows on each nullcline segment ----
    # On x=0 (N1a, y-axis): motion is vertical (dx=0); dy/dt = -fy² < 0 → DOWN
    for y_pt in [0.5, 1.5, 2.5, 3.5]:
        ax.annotate("", xy=(0, y_pt - 0.35), xytext=(0, y_pt),
                    arrowprops=dict(arrowstyle="->", color="blue", lw=2.2, alpha=0.85))

    # On parabola (N1b): motion vertical; sign by (x-10)
    for x_pt in [3, 6, 9, 12, 16, 19]:
        y_pt = (a1*x_pt - a2*x_pt**2)/b
        if y_pt > 0.05:
            dyv = d*x_pt*y_pt - f*y_pt**2
            sign = np.sign(dyv)
            ax.annotate("", xy=(x_pt, y_pt + 0.25*sign), xytext=(x_pt, y_pt),
                        arrowprops=dict(arrowstyle="->", color="blue", lw=2.2, alpha=0.85))

    # On y=0 (N2a, x-axis): motion horizontal; dx/dt = x²(a1 - a2 x)
    for x_pt in [3, 8, 14, 18, 22]:
        dxv = a1*x_pt**2 - a2*x_pt**3
        sign = np.sign(dxv)
        ax.annotate("", xy=(x_pt + 1.6*sign, 0), xytext=(x_pt, 0),
                    arrowprops=dict(arrowstyle="->", color="red", lw=2.2, alpha=0.85))

    # On y = dx/f (N2b): motion horizontal; sign by (10-x)
    for x_pt in [3, 6, 9, 12, 16, 20]:
        y_pt = d*x_pt/f
        dxv = a1*x_pt**2 - a2*x_pt**3 - b*x_pt*y_pt
        sign = np.sign(dxv)
        if abs(sign) > 0:
            ax.annotate("", xy=(x_pt + 1.5*sign, y_pt), xytext=(x_pt, y_pt),
                        arrowprops=dict(arrowstyle="->", color="red", lw=2.2, alpha=0.85))

    # equilibria
    for label, (x_val, y_val) in equilibria.items():
        is_stable = "(x*, y*)" in label
        ax.plot(x_val, y_val, "o", ms=14,
                mfc="yellow" if is_stable else "white",
                mec="black", mew=1.8, zorder=5)
        ax.annotate(label, (x_val, y_val), xytext=(10, 10),
                    textcoords="offset points", fontsize=11, fontweight="bold")
    ax.set_xlim(-1, 25); ax.set_ylim(-0.3, 4)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y", fontsize=12)
    ax.set_title("Problem 4 — Nullclines, vector directions & flow field\n"
                 r"$\dot{x}=a_1 x^2-a_2 x^3-bxy,\;\dot{y}=dxy-fy^2$"
                 f"  (a1={a1}, a2={a2}, b={b}, d={d}, f={f})\n"
                 "Blue arrows = vertical motion (on x-nullclines), "
                 "Red arrows = horizontal motion (on y-nullclines)",
                 fontsize=10)
    ax.legend(loc="upper right", fontsize=9); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig(FIG_DIR / "fig4_problem4_nullclines.png", dpi=160)
    plt.close()


# ============================================================
if __name__ == "__main__":
    problem1()
    problem2()
    problem3()
    problem4()
    print("\nAll figures written to:", FIG_DIR)
