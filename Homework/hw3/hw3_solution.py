"""
BME5113 HW3 — Numerical Simulation of Biological Dynamics
==========================================================
Problem 1: Beer fermentation (Fig 5.8) with yeast growth modulated by
           Temperature Optimum curve A of Fig 5.4 (k1,k2,k3,k4 = 1.25,1.5,29.3,40)
Problem 2: Non-dimensionalization of Lotka-Volterra (Eq. 4.23 / 4.24)
Problem 3: RK-4 time step on the stiff linear system (Eq. 6.4)
              du/dt =  998 u + 1998 v
              dv/dt = -999 u - 1999 v
Problem 4: Liquid-tank level — Euler vs Runge-Kutta

Outputs:
    hw3_figures/fig1_beer_fermentation.png
    hw3_figures/fig1b_temperature_curve.png
    hw3_figures/fig2_lv_nondim.png
    hw3_figures/fig3_rk4_timestep.png
    hw3_figures/fig4_tank_euler_vs_rk.png
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

for font in ['Noto Sans CJK TC', 'Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']:
    try:
        plt.rcParams['font.family'] = font
        break
    except Exception:
        continue
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hw3_figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------------------------------------------------------
# Generic integrators
# ------------------------------------------------------------------
def rk4_step(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + dt / 2, y + dt / 2 * k1)
    k3 = f(t + dt / 2, y + dt / 2 * k2)
    k4 = f(t + dt, y + dt * k3)
    return y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def euler_step(f, t, y, dt):
    return y + dt * f(t, y)


def integrate(stepper, f, y0, t0, t_end, dt):
    """Fixed-step integrator. The final step is clamped so t[-1] == t_end
    exactly (never overshoots) — important when dt > (t_end - t0)."""
    n = int(np.ceil((t_end - t0) / dt))
    y = np.zeros((n + 1, len(y0)))
    t = np.zeros(n + 1)
    y[0] = y0
    t[0] = t0
    for i in range(n):
        dt_step = min(dt, t_end - t[i])
        y[i + 1] = stepper(f, t[i], y[i], dt_step)
        t[i + 1] = t[i] + dt_step
    return t, y


# =====================================================================
# Problem 1: Beer fermentation (Fig 5.8) × Temperature Optimum curve A
# =====================================================================
#
# Original Fig 5.8 equations (S = sugar, Y = yeast, A = alcohol, in g/L):
#     dS/dt = -a b S Y - a f S Y
#     dY/dt =  a c S Y - d Y A
#     dA/dt =  a b S Y
#
# Problem 1 modification — multiply the yeast growth term by the
# Temperature Optimum response of Fig 5.4 curve A:
#     dY/dt = fT(T) * a c S Y - d Y A
#
# Temperature Optimum curve A (Spain's asymmetric form; parameters from
# Fig 5.4 panel K row A):  k1 = 1.25, k2 = 1.5, k3 = 29.3, k4 = 40.
#     fT(T) = k1 * ((k4 - T)/(k4 - k3))**k2 * exp(k2 * (T - k3)/(k4 - k3))
#     fT(k3) = k1  (peak),   fT(k4) = 0,   fT(T>k4) = 0.
#
# Diurnal forcing (problem spec): mean 20°C, amplitude 8°C, period 24 hr,
# peak at 12:00 noon:
#     T(t) = 20 + 8 * cos(2π (t - 12) / 24)        [t in hours]
#
# Stoichiometry (2.0665 g sugar -> 1 g EtOH + 0.9565 g CO2 + 0.11 g yeast)
# is respected only approximately: CO2 is treated as the "loss" term
# (a f S Y) as in Fig 5.8; parameters are chosen so yield ratios match.

# Temperature Optimum, curve A (panel K)
K1_A, K2_A, K3_A, K4_A = 1.25, 1.5, 29.3, 40.0

# Fig 5.8 rate parameters (chosen so: (i) ~fully fermented in ~1 week;
# (ii) EtOH / CO2 / yeast ratios near stoichiometric; (iii) Y_final a few g/L)
PAR_a = 0.0050   # [L/(g·hr)]  overall sugar uptake rate constant
PAR_b = 0.484    # []          fraction of uptaken sugar -> EtOH   (= 1/2.0665·(b+f)/0.947)
PAR_f = 0.466    # []          fraction -> CO2                      (b/(b+f) = 0.484/0.950 ≈ 0.509 matching 1/1.9565)
PAR_c = 0.055    # []          yeast yield per sugar uptaken
PAR_d = 0.00020  # [L/(g·hr)]  alcohol-induced yeast death


def temperature_profile(t_hr):
    """Diurnal temperature: 20C mean, 8C amplitude, peak at noon."""
    return 20.0 + 8.0 * np.cos(2.0 * np.pi * (t_hr - 12.0) / 24.0)


def fT_curveA(T, k1=K1_A, k2=K2_A, k3=K3_A, k4=K4_A):
    """Fig 5.4 curve A — Spain-style asymmetric temperature optimum.

    fT(T) = k1 * ((k4 - T)/(k4 - k3))**k2 * exp(k2 * (T - k3)/(k4 - k3))
    Defined for T < k4; peak fT(k3) = k1; zero at T = k4.
    """
    T = np.asarray(T, dtype=float)
    frac = (k4 - T) / (k4 - k3)
    # avoid negative base raised to non-integer power when T > k4
    safe = np.where(frac > 0, frac, 0.0)
    with np.errstate(invalid='ignore'):
        val = k1 * np.where(frac > 0, safe ** k2, 0.0) \
                  * np.exp(k2 * (T - k3) / (k4 - k3))
    return val


def beer_rhs_factory(k1=K1_A, k2=K2_A, k3=K3_A, k4=K4_A,
                     a=PAR_a, b=PAR_b, c=PAR_c, d=PAR_d, f=PAR_f):
    def rhs(t, state):
        S, Y, A = state
        S = max(S, 0.0)
        Y = max(Y, 0.0)
        A = max(A, 0.0)
        T = temperature_profile(t)
        fT = float(fT_curveA(T, k1, k2, k3, k4))
        dS = -a * b * S * Y - a * f * S * Y
        dY = fT * a * c * S * Y - d * Y * A
        dA = a * b * S * Y
        return np.array([dS, dY, dA])
    return rhs


def problem1_beer():
    print("=" * 64)
    print("Problem 1 — Beer fermentation (Fig 5.8 × Fig 5.4 curve A)")
    print("=" * 64)
    print("  fT(T) = k1·((k4-T)/(k4-k3))^k2 · exp(k2·(T-k3)/(k4-k3))")
    print(f"         k1={K1_A}, k2={K2_A}, k3={K3_A} (T_opt), k4={K4_A}")
    print(f"  params: a={PAR_a}, b={PAR_b}, c={PAR_c}, d={PAR_d}, f={PAR_f}")

    S0, Y0, A0 = 120.0, 0.5, 0.0
    t_end = 7.0 * 24.0    # 168 hr = 1 week
    dt = 0.1

    rhs = beer_rhs_factory()
    t, y = integrate(rk4_step, rhs, np.array([S0, Y0, A0]), 0.0, t_end, dt)
    S, Y, A = y[:, 0], y[:, 1], y[:, 2]
    T = temperature_profile(t)

    dS = S0 - S[-1]
    frac_b = PAR_b / (PAR_b + PAR_f)    # expected EtOH / sugar_consumed
    CO2_approx = dS * (PAR_f / (PAR_b + PAR_f))
    print(f"\n  Sugar consumed    : {dS:6.2f} g/L   ({100*dS/S0:5.1f}% of initial)")
    print(f"  Ethanol produced  : {A[-1]:6.2f} g/L   "
          f"(theoretical b/(b+f)·ΔS = {dS*frac_b:6.2f})")
    print(f"  CO2 (implicit)    : {CO2_approx:6.2f} g/L   (via f-branch)")
    print(f"  Yeast final       : {Y[-1]:6.2f} g/L")
    print(f"  ABV ≈ {A[-1]/7.9:4.1f} %   (ethanol density 0.79 g/mL)")

    # --- Figure 1: time series ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    tday = t / 24.0
    axes[0, 0].plot(tday, S, 'b-', lw=1.8); axes[0, 0].set_ylabel('Sugar S (g/L)')
    axes[0, 0].set_title('Sugar consumption'); axes[0, 0].grid(alpha=0.3)
    axes[0, 1].plot(tday, Y, 'g-', lw=1.8); axes[0, 1].set_ylabel('Yeast Y (g/L)')
    axes[0, 1].set_title('Yeast growth (with fT·acSY)'); axes[0, 1].grid(alpha=0.3)
    axes[1, 0].plot(tday, A, 'r-', lw=1.8); axes[1, 0].set_ylabel('Alcohol A (g/L)')
    axes[1, 0].set_xlabel('Time (day)')
    axes[1, 0].set_title('Alcohol production'); axes[1, 0].grid(alpha=0.3)
    axes[1, 1].plot(tday, T, 'orange', lw=1.2)
    axes[1, 1].axhline(K3_A, color='gray', ls='--', lw=0.8, label=f'T_opt=k3={K3_A}°C')
    axes[1, 1].set_ylabel('Temperature (°C)')
    axes[1, 1].set_xlabel('Time (day)')
    axes[1, 1].set_title('Diurnal T(t) = 20 + 8·cos(2π(t−12)/24)')
    axes[1, 1].legend(); axes[1, 1].grid(alpha=0.3)
    fig.suptitle('Problem 1: Fig 5.8 beer equations with Fig 5.4 curve A',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_beer_fermentation.png'), dpi=140)
    plt.close(fig)

    # --- Figure 1b: Temperature Optimum curves (reproduce Fig 5.4 panel K) ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    T_range = np.linspace(0, 45, 400)
    axes[0].plot(T_range, fT_curveA(T_range), 'b-', lw=2.2,
                 label=f'curve A  (k={K1_A},{K2_A},{K3_A},{K4_A})')
    # A few comparison curves to echo panel K qualitatively
    for (k1, k2, k3, k4, lab, ls) in [
            (1.0,  1.0,  25.0, 45.0, 'wider (illustr.)',  '--'),
            (1.1,  2.5,  32.0, 38.0, 'sharper (illustr.)', ':'),
    ]:
        axes[0].plot(T_range, fT_curveA(T_range, k1, k2, k3, k4),
                     ls, lw=1.2, alpha=0.7, label=lab)
    axes[0].axvspan(12, 28, color='orange', alpha=0.15, label='operating range')
    axes[0].axvline(K3_A, color='gray', ls='--', lw=0.7)
    axes[0].set_xlabel('Temperature (°C)')
    axes[0].set_ylabel('fT  (dimensionless)')
    axes[0].set_title('Fig 5.4 panel K — Temperature Optimum (curve A)')
    axes[0].legend(fontsize=9); axes[0].grid(alpha=0.3)

    # Show fT evaluated along the operating diurnal trajectory
    t_sample = np.linspace(0, 48, 500)
    axes[1].plot(t_sample, temperature_profile(t_sample), 'orange', lw=1.6, label='T(t) [°C]')
    axes[1].plot(t_sample, 20 * fT_curveA(temperature_profile(t_sample)),
                 'b-', lw=1.6, label='20·fT(T)  (scaled)')
    axes[1].set_xlabel('t (hr)'); axes[1].set_ylabel('value')
    axes[1].set_title('Diurnal T(t) and temperature modulation fT(T(t))')
    axes[1].legend(); axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1b_temperature_curve.png'), dpi=140)
    plt.close(fig)

    # --- Parameter sensitivity scan ---
    print("\n  Parameter sensitivity (final alcohol A at t=168 hr):")
    base = dict(k1=K1_A, k2=K2_A, k3=K3_A, k4=K4_A,
                a=PAR_a, b=PAR_b, c=PAR_c, d=PAR_d, f=PAR_f)

    def run(**overrides):
        p = {**base, **overrides}
        rhs = beer_rhs_factory(**p)
        _, y = integrate(rk4_step, rhs, np.array([S0, Y0, A0]), 0.0, t_end, dt)
        return y[-1, 0], y[-1, 1], y[-1, 2]

    scans = [
        ('k3 (T_opt)', [20.0, 25.0, 29.3, 33.0, 37.0], 'k3'),
        ('a (uptake)', [0.0020, 0.0030, 0.0040, 0.0060, 0.0080], 'a'),
        ('d (EtOH tox)', [0.0, 0.0001, 0.00020, 0.0005, 0.001], 'd'),
    ]
    for label, vals, key in scans:
        print(f"    -- scan {label} --")
        for v in vals:
            Sf, Yf, Af = run(**{key: v})
            print(f"      {key} = {v:<8}  S_f={Sf:6.2f}  Y_f={Yf:5.2f}  A_f={Af:6.2f}")

    print("  -> fig1_beer_fermentation.png, fig1b_temperature_curve.png")


# =====================================================================
# Problem 2: Non-dimensionalize Lotka-Volterra (Eq. 4.23 / 4.24)
# =====================================================================
#
#   dV/dt = r V - a V P            (Eq. 4.23)
#   dP/dt = a b V P - d P          (Eq. 4.24)
#
# Rescaling:
#   tau = r t
#   x   = (a b / d) V                  (prey scaled by predator-equilibrium)
#   y   = (a / r) P                    (predator scaled by prey-equilibrium)
#
# Non-dim system:
#   dx/dtau = x (1 - y)
#   dy/dtau = alpha * y (x - 1),       alpha = d / r
#
# => one dimensionless group alpha; fixed point moves to (1,1).


def lv_nondim_rhs(tau, state, alpha):
    x, y = state
    return np.array([x * (1.0 - y), alpha * y * (x - 1.0)])


def problem2_lv_nondim():
    print("\n" + "=" * 64)
    print("Problem 2 — LV non-dimensional system (from Eq. 4.23/4.24)")
    print("=" * 64)
    print("  dx/dτ = x(1 − y)")
    print("  dy/dτ = α y(x − 1),   α = d/r")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    alphas = [0.5, 1.0, 2.0]
    colors = ['#1565C0', '#2E7D32', '#C62828']
    for alpha, col in zip(alphas, colors):
        for (x0, y0) in [(0.5, 0.5), (2.0, 0.5), (0.5, 2.0)]:
            f = lambda t, s: lv_nondim_rhs(t, s, alpha)
            _, sol = integrate(rk4_step, f, np.array([x0, y0]),
                               0.0, 20.0, 0.01)
            axes[0].plot(sol[:, 0], sol[:, 1], '-', color=col, lw=1.2, alpha=0.7)
        axes[0].plot([], [], '-', color=col, label=f'α = {alpha}')
    axes[0].plot(1, 1, 'k*', markersize=14, label='fixed point (1,1)')
    axes[0].set_xlabel('x (prey)'); axes[0].set_ylabel('y (predator)')
    axes[0].set_title('Phase portrait — non-dim LV')
    axes[0].legend(); axes[0].grid(alpha=0.3)
    axes[0].set_xlim(0, 3.5); axes[0].set_ylim(0, 3.5)

    f = lambda t, s: lv_nondim_rhs(t, s, 1.0)
    tau, sol = integrate(rk4_step, f, np.array([0.5, 0.5]),
                         0.0, 30.0, 0.01)
    axes[1].plot(tau, sol[:, 0], 'b-', lw=1.6, label='x (prey)')
    axes[1].plot(tau, sol[:, 1], 'r-', lw=1.6, label='y (predator)')
    axes[1].set_xlabel('τ (dimensionless time)')
    axes[1].set_ylabel('x, y')
    axes[1].set_title('Oscillatory time series (α=1, x₀=y₀=0.5)')
    axes[1].legend(); axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_lv_nondim.png'), dpi=140)
    plt.close(fig)
    print("  -> fig2_lv_nondim.png")


# =====================================================================
# Problem 3: RK-4 time steps on the stiff system Eq. 6.4
# =====================================================================
#
#   du/dt =  998 u + 1998 v
#   dv/dt = -999 u - 1999 v
#
# Matrix A = [[998, 1998], [-999, -1999]] has eigenvalues λ = -1 and -1000
#   (trace = -1001, det = 1000 → (λ+1)(λ+1000) = 0).
# This is a classic stiff ODE: stiff mode decays 1000× faster than slow mode.
#
# With u(0)=1, v(0)=0 the exact solution is
#   u(t) =  2 e^{-t}  -  e^{-1000 t}
#   v(t) = -  e^{-t}  +  e^{-1000 t}
# — so BOTH modes are excited, the stiff mode cannot be ignored by the scheme.
#
# RK-4 is only conditionally stable: for a real negative eigenvalue λ, the
# step z = λ Δt must satisfy |R(z)| ≤ 1 with
#   R(z) = 1 + z + z²/2 + z³/6 + z⁴/24.
# The real-axis stability boundary is z ≈ -2.7853, so the STIFF mode demands
#   Δt ≤ 2.7853 / 1000 ≈ 2.79e-3 .
#
# Therefore all four prescribed Δt = (1.0, 0.5, 0.1, 0.01) are UNSTABLE, and
# we must "continue" to smaller Δt to see RK-4 converge.


def eq64_rhs(t, s):
    u, v = s
    return np.array([ 998.0 * u + 1998.0 * v,
                     -999.0 * u - 1999.0 * v])


def eq64_exact(t, u0=1.0, v0=0.0):
    # solve C1, C2 from eigen-decomposition (eigvecs: λ=-1 -> (2,-1); λ=-1000 -> (1,-1))
    # u = 2 C1 e^{-t} + C2 e^{-1000 t};  v = -C1 e^{-t} - C2 e^{-1000 t}
    # u0 = 2 C1 + C2; v0 = -C1 - C2  =>  C1 = u0 + v0,  C2 = -(u0 + 2 v0)
    C1 = u0 + v0
    C2 = -(u0 + 2.0 * v0)
    e1 = np.exp(-t)
    e2 = np.exp(-1000.0 * t)
    u = 2.0 * C1 * e1 + C2 * e2
    v = -C1 * e1 - C2 * e2
    return u, v


def problem3_rk4_timestep():
    print("\n" + "=" * 64)
    print("Problem 3 — RK-4 on stiff Eq. 6.4")
    print("=" * 64)
    print("  du/dt =  998 u + 1998 v,   dv/dt = -999 u - 1999 v")
    print("  eigenvalues λ = -1, -1000  (stiffness ratio 1000)")
    print("  RK-4 real-axis stability: Δt ≤ 2.7853/|λ_max| ≈ 2.79e-3")
    print()

    # --- Initial condition (assumption — homework does not specify) ---
    # u(0)=1, v(0)=0 is chosen so BOTH eigenmodes are excited:
    #   C1 = u0 + v0 = 1      (coefficient of slow mode e^{-t})
    #   C2 = -(u0 + 2 v0) = -1 (coefficient of stiff mode e^{-1000 t})
    # This is the conservative test for stiffness. An IC aligned with the
    # slow eigenvector (e.g. (u,v)=(2,-1)) would set C2=0 and any Δt works.
    y0 = np.array([1.0, 0.0])
    t_end = 1.0   # integrate over many slow time-constants (1/|λ_slow|=1)
                  # with Δt = 1.0 this still gives 1 step; Δt=0.01 gives 100 steps.

    # Prescribed time steps + progressively smaller ones to find convergence.
    dts = [1.0, 0.5, 0.1, 0.01, 5e-3, 3e-3, 2.79e-3, 2.5e-3, 2e-3, 1e-3, 5e-4]

    print(f"  IC: u(0)={y0[0]}, v(0)={y0[1]} (both eigenmodes excited)")
    print(f"  integrate to t = {t_end}")
    print()
    print(f"  {'Δt':>10} | {'n_steps':>7} | {'u(T)':>14} | {'|u_err|':>11} | status")
    u_exact, _ = eq64_exact(t_end, *y0)
    results = []
    for dt in dts:
        n_steps = max(1, int(np.ceil(t_end / dt)))
        y = y0.copy()
        t = 0.0
        blew_up = False
        for _ in range(n_steps):
            dt_step = min(dt, t_end - t)
            y = rk4_step(eq64_rhs, t, y, dt_step)
            t += dt_step
            if (not np.all(np.isfinite(y))) or np.max(np.abs(y)) > 1e20:
                blew_up = True
                break
        err = abs(y[0] - u_exact) if not blew_up else np.inf
        status = 'UNSTABLE' if blew_up else (
                 'converged' if err < 1e-4 else
                 'stable, not yet accurate')
        results.append((dt, y[0] if not blew_up else float('nan'), err, status))
        err_str = f"{err:.3e}" if np.isfinite(err) else '    —    '
        u_str = f"{y[0]:14.4e}" if not blew_up else '       BLOWUP'
        print(f"  {dt:10.4g} | {n_steps:>7} | {u_str} | {err_str:>11} | {status}")
    print(f"  reference u({t_end}) = {u_exact:.10e}")

    # ----- Figure: show solutions at a few representative Δt -----
    t_fine = np.linspace(0, t_end, 2000)
    u_true, v_true = eq64_exact(t_fine)
    plot_dts = [0.01, 3e-3, 2.5e-3, 1e-3]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, dt in zip(axes.ravel(), plot_dts):
        n = max(1, int(np.ceil(t_end / dt)))
        ys = np.zeros((n + 1, 2))
        ts = np.zeros(n + 1)
        ys[0] = y0
        ok = True
        for i in range(n):
            dt_step = min(dt, t_end - ts[i])
            ys[i + 1] = rk4_step(eq64_rhs, ts[i], ys[i], dt_step)
            ts[i + 1] = ts[i] + dt_step
            if (not np.all(np.isfinite(ys[i + 1]))
                    or np.max(np.abs(ys[i + 1])) > 1e20):
                ok = False
                ys = ys[:i + 2]
                ts = ts[:i + 2]
                break
        ax.plot(t_fine, u_true, 'k-', lw=2.0, alpha=0.6, label='exact u')
        ax.plot(t_fine, v_true, 'k--', lw=1.2, alpha=0.5, label='exact v')
        if ok:
            ax.plot(ts, ys[:, 0], 'b.-', lw=1.2, ms=4, label=f'RK4 u, Δt={dt}')
            ax.plot(ts, ys[:, 1], 'r.-', lw=1.2, ms=4, label=f'RK4 v, Δt={dt}')
        else:
            ax.plot(ts, np.clip(ys[:, 0], -5, 5), 'b.-', lw=1.2, ms=4,
                    label='RK4 u (diverged)')
            ax.text(t_end * 0.5, 0.0, 'BLEW UP', ha='center', color='red',
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('t'); ax.set_ylabel('u, v')
        ax.set_title(f'Δt = {dt}' + ('  (unstable)' if not ok else ''))
        ax.grid(alpha=0.3); ax.legend(fontsize=8, loc='best')
        ax.set_ylim(-2, 2)
    fig.suptitle('Problem 3: RK-4 on stiff Eq. 6.4   (λ = −1, −1000)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_rk4_timestep.png'), dpi=140)
    plt.close(fig)

    print("\n  Conclusion: none of Δt=(1.0, 0.5, 0.1, 0.01) is stable; the stiff")
    print("  eigenvalue λ=-1000 requires Δt ≲ 2.79e-3 for RK-4 absolute stability.")
    print("  Δt ≈ 1e-3 gives fully converged dynamics. This is textbook stiffness:")
    print("  explicit RK-4 is forced to track the fast transient even long after")
    print("  it has decayed; an implicit or A-stable method (BDF, TR) would remove")
    print("  the restriction.")
    print("  -> fig3_rk4_timestep.png")


# =====================================================================
# Problem 4: Tank level — Euler vs Runge-Kutta
# =====================================================================
#
#   16 sqrt(5h − h²) dh/dt = − sin(π t / 60),  h(0) = 2,   0 ≤ t ≤ 120
#
#   => dh/dt = − sin(π t / 60) / (16 · sqrt(h(5 − h)))
#
# Analytical implicit form:
#   G(h) = 8 (h − 5/2) sqrt(h(5 − h)) + 50 arcsin((2h − 5)/5)
#   G(h(t)) − G(h₀) = (60/π) [cos(π t / 60) − 1]


def tank_rhs(t, s):
    h = s[0]
    arg = max(5.0 * h - h * h, 1e-12)
    return np.array([-np.sin(np.pi * t / 60.0) / (16.0 * np.sqrt(arg))])


def tank_analytical_h(t_grid, h0=2.0):
    def G(h):
        return (8.0 * (h - 2.5) * np.sqrt(h * (5.0 - h))
                + 50.0 * np.arcsin((2.0 * h - 5.0) / 5.0))

    G0 = G(h0)
    h_sol = np.zeros_like(t_grid)
    for i, tt in enumerate(t_grid):
        target = G0 + (60.0 / np.pi) * (np.cos(np.pi * tt / 60.0) - 1.0)
        lo, hi = 0.001, 4.999
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if G(mid) < target:
                lo = mid
            else:
                hi = mid
        h_sol[i] = 0.5 * (lo + hi)
    return h_sol


def _try_integrate(stepper, dt, h0=2.0, t_end=120.0):
    try:
        t, y = integrate(stepper, tank_rhs, np.array([h0]), 0.0, t_end, dt)
        h = y[:, 0]
        if (not np.all(np.isfinite(h))) or np.any(h < -0.01) or np.any(h > 5.01):
            return None, None
        return t, h
    except Exception:
        return None, None


def problem4_tank():
    print("\n" + "=" * 64)
    print("Problem 4 — Tank level: Euler vs Runge-Kutta")
    print("=" * 64)

    t_ref = np.linspace(0, 120, 601)
    h_ref = tank_analytical_h(t_ref)

    dts_scan = [10.0, 5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.01]
    print("  dt      | Euler  | RK-4   (max |err| vs analytic; 'x' = diverged)")
    max_dt_ok = {'euler': None, 'rk4': None}
    for dt in dts_scan:
        te, he = _try_integrate(euler_step, dt)
        tr, hr = _try_integrate(rk4_step, dt)

        def err(tn, hn):
            if tn is None:
                return 'x'
            h_interp = np.interp(tn, t_ref, h_ref)
            return f"{np.max(np.abs(hn - h_interp)):.3e}"

        if he is not None:
            h_interp = np.interp(te, t_ref, h_ref)
            if np.max(np.abs(he - h_interp)) < 0.05 and max_dt_ok['euler'] is None:
                max_dt_ok['euler'] = dt
        if hr is not None:
            h_interp = np.interp(tr, t_ref, h_ref)
            if np.max(np.abs(hr - h_interp)) < 0.05 and max_dt_ok['rk4'] is None:
                max_dt_ok['rk4'] = dt
        print(f"  {dt:6.3f}  | {err(te, he):>8} | {err(tr, hr):>8}")

    print(f"\n  Largest dt with |err|<0.05 — Euler: {max_dt_ok['euler']},"
          f"   RK-4: {max_dt_ok['rk4']}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, dt in zip(axes, [1.0, 0.1]):
        ax.plot(t_ref, h_ref, 'k-', lw=2.0, label='analytical')
        te, he = _try_integrate(euler_step, dt)
        tr, hr = _try_integrate(rk4_step, dt)
        if te is not None:
            ax.plot(te, he, 'b.--', lw=1.2, ms=3, label=f'Euler Δt={dt}')
        else:
            ax.text(60, 2.5, f'Euler Δt={dt}\nDIVERGED', ha='center',
                    color='blue', fontsize=10, fontweight='bold')
        if tr is not None:
            ax.plot(tr, hr, 'r.-', lw=1.2, ms=3, label=f'RK-4 Δt={dt}')
        ax.set_xlabel('t'); ax.set_ylabel('h (tank level)')
        ax.set_title(f'Δt = {dt}')
        ax.grid(alpha=0.3); ax.legend(fontsize=9)
    fig.suptitle('Problem 4: Tank-level ODE — Euler vs RK-4',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4_tank_euler_vs_rk.png'), dpi=140)
    plt.close(fig)
    print("  -> fig4_tank_euler_vs_rk.png")


# =====================================================================
# Main
# =====================================================================

if __name__ == '__main__':
    print(f"Output directory: {OUTPUT_DIR}\n")
    problem1_beer()
    problem2_lv_nondim()
    problem3_rk4_timestep()
    problem4_tank()
    print(f"\nDone. Figures in {OUTPUT_DIR}/")
