"""
BME5113 HW3 — Numerical Simulation of Biological Dynamics
==========================================================
Problem 1: Beer fermentation with temperature-dependent yeast growth (curve A)
Problem 2: Non-dimensionalization of Lotka-Volterra (phase portrait illustration)
Problem 3: RK-4 time step sensitivity on a Lotka-Volterra ODE (Eq. 6.4)
Problem 4: Liquid tank level — Euler vs Runge-Kutta comparison

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


# =====================================================================
# Problem 1: Beer fermentation with Temperature Optimum (Fig 5.4 curve A)
# =====================================================================
#
# State variables (per litre of wort):
#   S : sugar            [g/L]
#   Y : yeast biomass    [g/L]
#   E : ethanol          [g/L]
#   C : CO2 released     [g/L]
#
# Stoichiometric constraint (given):
#   2.0665 g sugar -> 1 g ethanol + 0.9565 g CO2 + 0.11 g yeast
# => yield coefficients (mass/mass sugar consumed):
#   Y_ES = 1/2.0665     (ethanol)
#   Y_CS = 0.9565/2.0665 (CO2)
#   Y_YS = 0.11/2.0665  (yeast)
#
# Kinetics: Monod substrate uptake, multiplied by temperature optimum curve A
#   mu(T,S) = mu_max * f_T(T) * S/(K_s + S)
#   dY/dt = mu(T,S) * Y - k_d * Y
#   dS/dt = -(1/Y_YS) * mu(T,S) * Y
#   dE/dt =  Y_ES/Y_YS * mu(T,S) * Y
#   dC/dt =  Y_CS/Y_YS * mu(T,S) * Y
#
# Temperature Optimum, curve A (Gaussian form for fig 5.4 curve A):
#   f_T(T) = exp( -((T - T_opt)**2) / (2 * sigma**2) )
#
# Diurnal temperature forcing:
#   T(t) = 20 + 8 * cos(2 * pi * (t - 12) / 24)     [t in hours, peak at 12:00]


# Stoichiometric yield coefficients
Y_ES = 1.0 / 2.0665       # ~0.4839
Y_CS = 0.9565 / 2.0665    # ~0.4629
Y_YS = 0.11 / 2.0665      # ~0.0532

# Kinetic parameters (chosen so ~90% sugar consumed within one week)
MU_MAX = 0.12              # [1/hr]  maximum specific growth rate at optimum
K_S = 5.0                  # [g/L]   half-saturation for sugar
K_D = 0.0                  # [1/hr]  yeast decay (set to 0 for strict stoichiometric closure)
T_OPT = 25.0               # [C]     yeast temperature optimum
T_SIGMA = 5.0              # [C]     width of optimum curve


def temperature_profile(t_hr):
    """Diurnal temperature: 20C mean, 8C amplitude, peak at noon."""
    return 20.0 + 8.0 * np.cos(2.0 * np.pi * (t_hr - 12.0) / 24.0)


def f_T_curveA(T, T_opt=None):
    """Fig 5.4 curve A — Gaussian temperature optimum."""
    if T_opt is None:
        T_opt = T_OPT
    return np.exp(-((T - T_opt) ** 2) / (2.0 * T_SIGMA ** 2))


def make_beer_rhs(T_opt=None):
    def rhs(t, state):
        S, Y, E, C = state
        S = max(S, 0.0)
        Y = max(Y, 0.0)
        T = temperature_profile(t)
        mu = MU_MAX * f_T_curveA(T, T_opt) * S / (K_S + S)
        dY = mu * Y - K_D * Y
        dS = -(1.0 / Y_YS) * mu * Y
        dE = (Y_ES / Y_YS) * mu * Y
        dC = (Y_CS / Y_YS) * mu * Y
        return np.array([dS, dY, dE, dC])
    return rhs


def beer_rhs(t, state):
    S, Y, E, C = state
    S = max(S, 0.0)
    Y = max(Y, 0.0)
    T = temperature_profile(t)
    mu = MU_MAX * f_T_curveA(T) * S / (K_S + S)
    dY = mu * Y - K_D * Y
    dS = -(1.0 / Y_YS) * mu * Y
    dE = (Y_ES / Y_YS) * mu * Y
    dC = (Y_CS / Y_YS) * mu * Y
    return np.array([dS, dY, dE, dC])


def rk4_step(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + dt / 2, y + dt / 2 * k1)
    k3 = f(t + dt / 2, y + dt / 2 * k2)
    k4 = f(t + dt, y + dt * k3)
    return y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def euler_step(f, t, y, dt):
    return y + dt * f(t, y)


def integrate(stepper, f, y0, t0, t_end, dt):
    n = int(np.ceil((t_end - t0) / dt))
    t = t0 + dt * np.arange(n + 1)
    y = np.zeros((n + 1, len(y0)))
    y[0] = y0
    for i in range(n):
        y[i + 1] = stepper(f, t[i], y[i], dt)
    return t, y


def problem1_beer():
    # Initial conditions (typical homebrew wort)
    S0 = 120.0   # [g/L] initial fermentable sugar
    Y0 = 0.5     # [g/L] pitched yeast
    E0 = 0.0
    C0 = 0.0

    t0 = 0.0
    t_end = 7.0 * 24.0     # 1 week in hours
    dt = 0.1               # 6-minute step, adequate for RK4

    t, y = integrate(rk4_step, beer_rhs,
                     np.array([S0, Y0, E0, C0]), t0, t_end, dt)
    S, Y, E, C = y[:, 0], y[:, 1], y[:, 2], y[:, 3]
    T = temperature_profile(t)

    # Mass-balance check at final time
    dS_consumed = S0 - S[-1]
    E_predicted = Y_ES * dS_consumed
    C_predicted = Y_CS * dS_consumed
    Y_predicted = Y0 + Y_YS * dS_consumed

    print("=" * 64)
    print("Problem 1 — Beer fermentation (RK4, dt=0.1 hr, 168 hr)")
    print("=" * 64)
    print(f"  Sugar consumed       : {dS_consumed:.2f} g/L  "
          f"({100*dS_consumed/S0:.1f}% of initial)")
    print(f"  Ethanol  produced    : {E[-1]:.2f} g/L   (stoich: {E_predicted:.2f})")
    print(f"  CO2      released    : {C[-1]:.2f} g/L   (stoich: {C_predicted:.2f})")
    print(f"  Yeast    final       : {Y[-1]:.2f} g/L   (stoich: {Y_predicted:.2f})")
    print(f"  Mass-balance residual (ethanol): "
          f"{abs(E[-1] - E_predicted):.2e}")

    # --- Figure 1: state variables over time ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    t_day = t / 24.0
    axes[0, 0].plot(t_day, S, 'b-', lw=1.8); axes[0, 0].set_ylabel('Sugar S (g/L)')
    axes[0, 0].set_title('Sugar consumption'); axes[0, 0].grid(alpha=0.3)
    axes[0, 1].plot(t_day, Y, 'g-', lw=1.8); axes[0, 1].set_ylabel('Yeast Y (g/L)')
    axes[0, 1].set_title('Yeast growth'); axes[0, 1].grid(alpha=0.3)
    axes[1, 0].plot(t_day, E, 'r-', lw=1.8); axes[1, 0].set_ylabel('Ethanol E (g/L)')
    axes[1, 0].set_xlabel('Time (day)')
    axes[1, 0].set_title('Ethanol production'); axes[1, 0].grid(alpha=0.3)
    axes[1, 1].plot(t_day, C, 'm-', lw=1.8); axes[1, 1].set_ylabel('CO₂ (g/L)')
    axes[1, 1].set_xlabel('Time (day)')
    axes[1, 1].set_title('CO₂ release'); axes[1, 1].grid(alpha=0.3)
    fig.suptitle('Problem 1: Beer primary fermentation (1 week, diurnal 20±8°C)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_beer_fermentation.png'), dpi=140)
    plt.close(fig)

    # --- Figure 1b: temperature forcing & f_T(T) curve A ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(t_day, T, 'orange', lw=1.5)
    axes[0].axhline(T_OPT, color='gray', ls='--', lw=1, label=f'T_opt = {T_OPT}°C')
    axes[0].set_xlabel('Time (day)'); axes[0].set_ylabel('Temperature (°C)')
    axes[0].set_title('Diurnal temperature  T(t) = 20 + 8·cos(2π(t−12)/24)')
    axes[0].legend(); axes[0].grid(alpha=0.3)

    T_range = np.linspace(0, 45, 200)
    axes[1].plot(T_range, f_T_curveA(T_range), 'b-', lw=2, label='curve A (Gaussian)')
    axes[1].axvspan(12, 28, color='orange', alpha=0.2, label='operating range')
    axes[1].set_xlabel('Temperature (°C)'); axes[1].set_ylabel('f_T  (dimensionless)')
    axes[1].set_title('Fig 5.4 curve A — yeast temperature optimum')
    axes[1].legend(); axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1b_temperature_curve.png'), dpi=140)
    plt.close(fig)

    # --- Parameter sensitivity (Problem 1 discussion) ---
    # Sensitivity at 72 hr (partway through fermentation — differences visible)
    print("\n  Parameter sensitivity (sugar consumed % at t=72 hr):")
    for T_opt_try in [15.0, 20.0, 25.0, 30.0, 35.0]:
        _, yy = integrate(rk4_step, make_beer_rhs(T_opt_try),
                          np.array([S0, Y0, E0, C0]), t0, 72.0, dt)
        pct = 100 * (S0 - yy[-1, 0]) / S0
        print(f"    T_opt = {T_opt_try:4.1f}°C  -> {pct:5.1f}% sugar consumed in 72 hr")

    print("  fig1_beer_fermentation.png, fig1b_temperature_curve.png")


# =====================================================================
# Problem 2: Non-dimensionalize Lotka-Volterra (Eq. 4.23)
# =====================================================================
#
# dV/dt = r V - a V P
# dP/dt = a b V P - d P
#
# Rescale:
#   tau = r t                    (time in units of prey growth rate)
#   x   = (a b / d) V            (prey in units of predator half-cycle)
#   y   = (a / r) P              (predator in units of prey decay rate)
#
# Substitute:
#   dx/d(tau) = x (1 - y)
#   dy/d(tau) = alpha * y (x - 1)    with   alpha = d / r
#
# => single dimensionless parameter alpha controls dynamics.


def lv_nondim_rhs(tau, state, alpha):
    x, y = state
    return np.array([x * (1.0 - y), alpha * y * (x - 1.0)])


def problem2_lv_nondim():
    print("\n" + "=" * 64)
    print("Problem 2 — LV non-dimensional system")
    print("=" * 64)
    print("  dx/dτ = x(1 − y)")
    print("  dy/dτ = α y(x − 1),   α = d/r")

    # Phase portrait for a few α values
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

    # Time series for alpha = 1
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
    print("  fig2_lv_nondim.png")


# =====================================================================
# Problem 3: RK-4 time step on Eq. 6.4
# =====================================================================
#
# The textbook's Eq. 6.4 is the coupled Lotka-Volterra predator-prey
# system used for numerical demonstration in Haefner Chapter 6:
#
#   dV/dt = r V − a V P
#   dP/dt = b a V P − d P
#
# Parameters (Haefner's demo values):
#   r = 1.0, a = 0.1, b = 0.5, d = 0.5
#   V(0) = 10,  P(0) = 5
#
# We integrate to t=50 with RK-4 at dt ∈ {1.0, 0.5, 0.1, 0.01} and
# compare to a fine reference (dt = 0.001).


def eq64_rhs(t, s):
    r, a, b, d = 1.0, 0.1, 0.5, 0.5
    V, P = s
    return np.array([r * V - a * V * P, b * a * V * P - d * P])


def problem3_rk4_timestep():
    print("\n" + "=" * 64)
    print("Problem 3 — RK-4 time step sensitivity (Eq. 6.4 Lotka-Volterra)")
    print("=" * 64)

    y0 = np.array([10.0, 5.0])
    t_end = 50.0
    dts = [1.0, 0.5, 0.1, 0.01]

    # reference
    t_ref, y_ref = integrate(rk4_step, eq64_rhs, y0, 0.0, t_end, 0.001)
    V_ref_end = y_ref[-1, 0]

    results = []
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, dt in zip(axes.ravel(), dts):
        t, y = integrate(rk4_step, eq64_rhs, y0, 0.0, t_end, dt)
        err = abs(y[-1, 0] - V_ref_end)
        results.append((dt, y[-1, 0], err))
        ax.plot(t_ref, y_ref[:, 0], 'k-', lw=1.0, alpha=0.6, label='reference')
        ax.plot(t, y[:, 0], 'b.-', lw=1.3, ms=3, label=f'RK4 dt={dt}')
        ax.plot(t, y[:, 1], 'r.-', lw=1.3, ms=3, alpha=0.7, label='P')
        ax.set_xlabel('t'); ax.set_ylabel('V, P')
        ax.set_title(f'Δt = {dt}   |V(T)−V_ref| = {err:.3e}')
        ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.suptitle('Problem 3: RK-4 convergence as Δt decreases',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_rk4_timestep.png'), dpi=140)
    plt.close(fig)

    print(f"  {'dt':>8} | {'V(T)':>10} | {'|err|':>12}")
    for dt, VT, err in results:
        print(f"  {dt:8.3f} | {VT:10.4f} | {err:12.4e}")
    print(f"  reference V(T) = {V_ref_end:.6f}  (dt=0.001)")
    print("  -> Dynamics converge by dt ≈ 0.1; dt=0.01 essentially exact.")
    print("  fig3_rk4_timestep.png")


# =====================================================================
# Problem 4: Liquid tank level — Euler vs RK-4
# =====================================================================
#
#   16 * sqrt(5h − h^2) * dh/dt = − sin(π t / 60),   h(0)=2,   0 ≤ t ≤ 120
#
# =>  dh/dt = − sin(π t / 60) / (16 * sqrt(5h − h^2))
#
# Note: 5h − h^2 = h(5 − h), positive only for 0 < h < 5.
#       The denominator vanishes at h=0 and h=5, so large time steps
#       may overshoot the domain and the method blows up.
#
# Analytical implicit solution:
#   G(h) = 8(h − 5/2) sqrt(h(5−h)) + 50 arcsin((2h−5)/5)
#   G(h(t)) − G(h₀) = (60/π)[cos(π t / 60) − 1]


def tank_rhs(t, s):
    h = s[0]
    # clamp to keep sqrt well-defined against tiny numerical overshoot
    arg = max(5.0 * h - h * h, 1e-12)
    return np.array([-np.sin(np.pi * t / 60.0) / (16.0 * np.sqrt(arg))])


def tank_analytical_h(t_grid, h0=2.0):
    """Solve G(h) = G(h0) + (60/π)(cos(πt/60) - 1) for h at each t."""
    def G(h):
        return (8.0 * (h - 2.5) * np.sqrt(h * (5.0 - h))
                + 50.0 * np.arcsin((2.0 * h - 5.0) / 5.0))

    G0 = G(h0)
    h_sol = np.zeros_like(t_grid)
    for i, tt in enumerate(t_grid):
        target = G0 + (60.0 / np.pi) * (np.cos(np.pi * tt / 60.0) - 1.0)
        # bisection over h ∈ (0.001, 4.999)
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
    """Return (t, h) or (None, None) if diverged."""
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

    # Scan dt for Euler and RK-4 — find largest dt that stays stable
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

        # Track largest dt with acceptable accuracy (<0.05 absolute)
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

    # Representative plot: dt=1.0 (big) and dt=0.1 (fine) for both methods
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, dt in zip(axes, [1.0, 0.1]):
        ax.plot(t_ref, h_ref, 'k-', lw=2.0, label='analytical')
        te, he = _try_integrate(euler_step, dt)
        tr, hr = _try_integrate(rk4_step, dt)
        if te is not None:
            ax.plot(te, he, 'b.--', lw=1.2, ms=3, label=f'Euler Δt={dt}')
        else:
            ax.text(60, 2.5, f'Euler Δt={dt}\nDIVERGED',
                    ha='center', color='blue', fontsize=10, fontweight='bold')
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
    print("  fig4_tank_euler_vs_rk.png")


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
