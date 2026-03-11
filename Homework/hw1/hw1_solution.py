"""
BME5113 Biological Systems Modeling and Analysis
Homework 1: Island Biogeography - MacArthur-Wilson Theory

Author: [Student Name]
Date: 2026-03-12

HW1 Problems 1 and 2.
Problem 1: linear regression on Rakata data, equilibrium/pool estimation,
           finite-difference simulation from empty island and from R=500.
Problem 2: curvilinear model (exponential I, quadratic E), equilibrium
           derivation, biological rationale, island-size extension.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for file saving
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------------
# 0. Setup output directory
# ---------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hw1_figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Observed data for Rakata island (vascular plants)
# ---------------------------------------------------------------------------
R_data = np.array([0,   36,   80,  155,  210,  240],  dtype=float)
I_data = np.array([8.0,  3.0,  5.0,  6.5,  4.0,  2.5], dtype=float)
E_data = np.array([0.0,  0.05, 0.10, 0.50, 1.75, 1.75], dtype=float)

# ---------------------------------------------------------------------------
# 2. Problem 1(a): Linear regression for I(R) and E(R)
# ---------------------------------------------------------------------------

def linear_regression(x, y):
    """
    Perform linear regression y = a + b*x using numpy.polyfit.
    Returns coefficients (b, a) in the form [slope, intercept],
    and the coefficient of determination R².
    """
    coeffs = np.polyfit(x, y, 1)   # coeffs = [slope, intercept]
    slope, intercept = coeffs

    # Compute R²
    y_pred = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot != 0 else 1.0

    return slope, intercept, r_squared


slope_I, intercept_I, r2_I = linear_regression(R_data, I_data)
slope_E, intercept_E, r2_E = linear_regression(R_data, E_data)

# Notation aligned with theory:
#   I(R) = a_I + b_I * R   (b_I expected < 0: immigration decreases with R)
#   E(R) = a_E + b_E * R   (b_E expected > 0: extinction increases with R)
a_I, b_I = intercept_I, slope_I   # I(R) = a_I + b_I*R
a_E, b_E = intercept_E, slope_E   # E(R) = a_E + b_E*R

print("=" * 60)
print("PROBLEM 1 - LINEAR MODEL")
print("=" * 60)
print(f"\n(a) Linear Regression Results")
print(f"    Immigration: I(R) = {a_I:.4f} + ({b_I:.6f}) * R")
print(f"    R² (I) = {r2_I:.4f}")
print(f"    Extinction:  E(R) = {a_E:.4f} + ({b_E:.6f}) * R")
print(f"    R² (E) = {r2_E:.4f}")

# ---------------------------------------------------------------------------
# 3. Problem 1(b): Differential equation with fitted parameters
# ---------------------------------------------------------------------------
print(f"\n(b) Species dynamics equation:")
print(f"    dR/dt = I(R) - E(R)")
print(f"         = ({a_I:.4f} + {b_I:.6f}*R) - ({a_E:.4f} + {b_E:.6f}*R)")
net_a = a_I - a_E
net_b = b_I - b_E
print(f"         = {net_a:.4f} + ({net_b:.6f})*R")

# ---------------------------------------------------------------------------
# 4. Problem 1(c): Equilibrium species richness R*
# ---------------------------------------------------------------------------
# At equilibrium: dR/dt = 0  =>  I(R*) = E(R*)
# a_I + b_I * R* = a_E + b_E * R*
# (a_I - a_E) = (b_E - b_I) * R*
# R* = (a_I - a_E) / (b_E - b_I)

R_star = (a_I - a_E) / (b_E - b_I)

print(f"\n(c) Equilibrium species richness:")
print(f"    I(R*) = E(R*) => R* = (a_I - a_E) / (b_E - b_I)")
print(f"    R* = ({a_I:.4f} - {a_E:.4f}) / ({b_E:.6f} - {b_I:.6f})")
print(f"    R* = {R_star:.2f} species")

# ---------------------------------------------------------------------------
# 5. Problem 1(d): Mainland species pool P
# ---------------------------------------------------------------------------
# Immigration goes to zero when the island is fully saturated:
#   I(P) = 0  =>  a_I + b_I * P = 0  =>  P = -a_I / b_I
P = -a_I / b_I

print(f"\n(d) Mainland species pool (x-intercept of I):")
print(f"    I(P) = 0 => P = -a_I / b_I = {P:.1f} species")

# ---------------------------------------------------------------------------
# 6. Problem 1(e): Finite difference simulation
# ---------------------------------------------------------------------------

def dRdt_linear(R, a_I, b_I, a_E, b_E):
    """Rate of change of species richness under the linear model."""
    immigration = a_I + b_I * R
    extinction  = a_E + b_E * R
    # Clamp immigration and extinction to be non-negative
    immigration = max(immigration, 0.0)
    extinction  = max(extinction,  0.0)
    return immigration - extinction


def simulate_finite_difference(R0, t_max, dt, a_I, b_I, a_E, b_E):
    """
    Simulate species richness over time using the forward Euler method.

    R(t + dt) = R(t) + dt * dR/dt

    Parameters
    ----------
    R0    : initial species richness
    t_max : simulation end time (years)
    dt    : time step (years)
    """
    n_steps = int(t_max / dt) + 1
    t = np.linspace(0, t_max, n_steps)
    R = np.zeros(n_steps)
    R[0] = R0

    for i in range(n_steps - 1):
        rate = dRdt_linear(R[i], a_I, b_I, a_E, b_E)
        R[i + 1] = R[i] + dt * rate
        # Species richness must remain non-negative
        R[i + 1] = max(R[i + 1], 0.0)

    return t, R


# Simulation parameters
T_MAX = 500    # years
DT    = 0.5   # time step

t_from0,   R_from0   = simulate_finite_difference(0,   T_MAX, DT, a_I, b_I, a_E, b_E)
t_from500, R_from500 = simulate_finite_difference(500, T_MAX, DT, a_I, b_I, a_E, b_E)

print(f"\n(e) Finite difference simulation (dt = {DT} yr, T_max = {T_MAX} yr)")
print(f"    Starting R=0:   final R = {R_from0[-1]:.2f}")
print(f"    Starting R=500: final R = {R_from500[-1]:.2f}")
print(f"    Theoretical R* = {R_star:.2f}")

# Time to reach within 5% of R* from below and above
tolerance = 0.05 * R_star
idx0 = np.where(np.abs(R_from0   - R_star) < tolerance)[0]
idx5 = np.where(np.abs(R_from500 - R_star) < tolerance)[0]
t_conv0   = t_from0[idx0[0]]   if len(idx0) > 0 else T_MAX
t_conv500 = t_from500[idx5[0]] if len(idx5) > 0 else T_MAX
print(f"    Convergence time from R=0:   ~{t_conv0:.0f} yr  (within 5% of R*)")
print(f"    Convergence time from R=500: ~{t_conv500:.0f} yr (within 5% of R*)")

# ---------------------------------------------------------------------------
# 7. Problem 2(a): Alternative curvilinear model
# ---------------------------------------------------------------------------
#   I(R) = lambda * exp(-alpha * R)    (negative exponential)
#   E(R) = beta * R^2                  (quadratic)
#
# Parameters chosen so that:
#   - I(0) = lambda ≈ 8 (same as linear model intercept)
#   - Equilibrium near R* of the linear model

lam   = 8.0       # lambda: immigration rate at R=0
alpha = 0.008     # decay constant for immigration
beta  = 0.00003   # quadratic coefficient for extinction


def I_curvilinear(R, lam, alpha):
    return lam * np.exp(-alpha * R)


def E_curvilinear(R, beta):
    return beta * R ** 2


# Find curvilinear equilibrium numerically (I(R) = E(R))
# lam * exp(-alpha * R) = beta * R^2
# Scan over R to find crossing point
R_scan = np.linspace(1, 800, 50000)
diff = I_curvilinear(R_scan, lam, alpha) - E_curvilinear(R_scan, beta)
sign_changes = np.where(np.diff(np.sign(diff)))[0]

R_star_curv = None
if len(sign_changes) > 0:
    # Refine with bisection between the two bracketing points
    r_lo = R_scan[sign_changes[0]]
    r_hi = R_scan[sign_changes[0] + 1]
    for _ in range(50):
        r_mid = 0.5 * (r_lo + r_hi)
        if (I_curvilinear(r_mid, lam, alpha) - E_curvilinear(r_mid, beta)) > 0:
            r_lo = r_mid
        else:
            r_hi = r_mid
    R_star_curv = 0.5 * (r_lo + r_hi)

print("\n" + "=" * 60)
print("PROBLEM 2 - CURVILINEAR MODEL")
print("=" * 60)
print(f"\nParameters: lambda={lam}, alpha={alpha}, beta={beta}")
if R_star_curv is not None:
    print(f"Equilibrium R* (curvilinear) = {R_star_curv:.2f} species")
    print(f"  Verification: I(R*)={I_curvilinear(R_star_curv, lam, alpha):.4f}, "
          f"E(R*)={E_curvilinear(R_star_curv, beta):.4f}")

# ---------------------------------------------------------------------------
# 8. Problem 2(d): Island size effect
# ---------------------------------------------------------------------------
#   I(R, A) = lambda * A^0.3 * exp(-alpha * R)
#   E(R, A) = beta / A^0.5 * R^2
#
# Larger islands (higher A):
#   - Higher immigration capacity (more habitats attract more species)
#   - Lower per-species extinction (more resources reduce competition pressure)

ISLAND_AREAS = [1, 5, 20]  # relative area units

def I_size(R, lam, alpha, A):
    return lam * (A ** 0.3) * np.exp(-alpha * R)


def E_size(R, beta, A):
    return (beta / (A ** 0.5)) * R ** 2


def find_equilibrium_size(lam, alpha, beta, A):
    """Find equilibrium R* for a given island area A."""
    R_scan = np.linspace(1, 1200, 100000)
    diff = I_size(R_scan, lam, alpha, A) - E_size(R_scan, beta, A)
    sign_ch = np.where(np.diff(np.sign(diff)))[0]
    if len(sign_ch) == 0:
        return None
    r_lo = R_scan[sign_ch[0]]
    r_hi = R_scan[sign_ch[0] + 1]
    for _ in range(60):
        r_mid = 0.5 * (r_lo + r_hi)
        if (I_size(r_mid, lam, alpha, A) - E_size(r_mid, beta, A)) > 0:
            r_lo = r_mid
        else:
            r_hi = r_mid
    return 0.5 * (r_lo + r_hi)


print(f"\n(d) Island size effect on equilibrium species richness:")
size_equilibria = {}
for A in ISLAND_AREAS:
    R_eq = find_equilibrium_size(lam, alpha, beta, A)
    size_equilibria[A] = R_eq
    if R_eq is not None:
        print(f"    A = {A:2d}: R* = {R_eq:.2f} species")
    else:
        print(f"    A = {A:2d}: No equilibrium found")

# ---------------------------------------------------------------------------
# 9. Plotting
# ---------------------------------------------------------------------------

R_plot = np.linspace(0, 300, 500)

# -- Figure 1: Linear regression (Problem 1a) --------------------------------
fig1, ax1 = plt.subplots(figsize=(8, 5))

I_fit = a_I + b_I * R_plot
E_fit = a_E + b_E * R_plot

ax1.plot(R_plot, I_fit, 'b-', linewidth=2,
         label=f'I(R) = {a_I:.2f} + ({b_I:.4f})R  (R²={r2_I:.3f})')
ax1.plot(R_plot, E_fit, 'r-', linewidth=2,
         label=f'E(R) = {a_E:.4f} + ({b_E:.5f})R  (R²={r2_E:.3f})')
ax1.scatter(R_data, I_data, color='blue', s=60, zorder=5, label='I data')
ax1.scatter(R_data, E_data, color='red',  s=60, zorder=5, label='E data')
ax1.axvline(R_star, color='green', linestyle='--', linewidth=1.5,
            label=f'R* = {R_star:.1f}')
ax1.set_xlabel('Species Richness R', fontsize=12)
ax1.set_ylabel('Rate (species / year)', fontsize=12)
ax1.set_title('Problem 1(a): Linear Regression for I(R) and E(R)\n'
              'Rakata Island Vascular Plants', fontsize=12)
ax1.legend(fontsize=9)
ax1.set_xlim(0, 280)
ax1.set_ylim(-0.5, 9.5)
ax1.grid(True, alpha=0.3)
fig1.tight_layout()
fig1.savefig(os.path.join(OUTPUT_DIR, 'fig1_linear_regression.png'), dpi=150)
plt.close(fig1)
print(f"\nSaved: fig1_linear_regression.png")

# -- Figure 2: Finite difference simulation (Problem 1e) --------------------
fig2, ax2 = plt.subplots(figsize=(8, 5))

ax2.plot(t_from0,   R_from0,   'b-',  linewidth=2, label='Start R = 0')
ax2.plot(t_from500, R_from500, 'r--', linewidth=2, label='Start R = 500')
ax2.axhline(R_star, color='green', linestyle=':', linewidth=1.5,
            label=f'Equilibrium R* = {R_star:.1f}')
ax2.set_xlabel('Time (years)', fontsize=12)
ax2.set_ylabel('Species Richness R', fontsize=12)
ax2.set_title('Problem 1(e): Species Dynamics Simulation\n'
              'Finite Difference Method (Linear Model)', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
fig2.tight_layout()
fig2.savefig(os.path.join(OUTPUT_DIR, 'fig2_simulation_linear.png'), dpi=150)
plt.close(fig2)
print(f"Saved: fig2_simulation_linear.png")

# -- Figure 3: Curvilinear model (Problem 2a) --------------------------------
R_plot2 = np.linspace(0, 700, 1000)
I_curv  = I_curvilinear(R_plot2, lam, alpha)
E_curv  = E_curvilinear(R_plot2, beta)
I_lin2  = np.maximum(a_I + b_I * R_plot2, 0)
E_lin2  = np.maximum(a_E + b_E * R_plot2, 0)

fig3, axes3 = plt.subplots(1, 2, figsize=(13, 5))

# Left: side-by-side comparison
ax3a = axes3[0]
ax3a.plot(R_plot2, I_lin2,  'b--', linewidth=1.8, label='I linear')
ax3a.plot(R_plot2, E_lin2,  'r--', linewidth=1.8, label='E linear')
ax3a.plot(R_plot2, I_curv,  'b-',  linewidth=2.2, label='I(R) = λe^{-αR}')
ax3a.plot(R_plot2, E_curv,  'r-',  linewidth=2.2, label='E(R) = βR²')
if R_star_curv is not None:
    ax3a.axvline(R_star_curv, color='purple', linestyle=':', linewidth=1.5,
                 label=f'R* (curv.) = {R_star_curv:.1f}')
ax3a.axvline(R_star, color='green', linestyle=':', linewidth=1.5,
             label=f'R* (linear) = {R_star:.1f}')
ax3a.scatter(R_data, I_data, color='blue', s=50, zorder=5)
ax3a.scatter(R_data, E_data, color='red',  s=50, zorder=5)
ax3a.set_xlabel('Species Richness R', fontsize=11)
ax3a.set_ylabel('Rate (species / year)', fontsize=11)
ax3a.set_title('Problem 2(a): Curvilinear vs Linear Model', fontsize=11)
ax3a.set_xlim(0, 500)
ax3a.set_ylim(-0.2, 9)
ax3a.legend(fontsize=8)
ax3a.grid(True, alpha=0.3)

# Right: zoom near equilibrium
ax3b = axes3[1]
R_zoom = np.linspace(50, 450, 800)
ax3b.plot(R_zoom, I_curvilinear(R_zoom, lam, alpha), 'b-', linewidth=2,
          label='I(R) = λe^{-αR}')
ax3b.plot(R_zoom, E_curvilinear(R_zoom, beta),       'r-', linewidth=2,
          label='E(R) = βR²')
ax3b.fill_between(R_zoom,
                  I_curvilinear(R_zoom, lam, alpha),
                  E_curvilinear(R_zoom, beta),
                  where=(I_curvilinear(R_zoom, lam, alpha) >
                         E_curvilinear(R_zoom, beta)),
                  alpha=0.15, color='blue', label='R increasing (I > E)')
ax3b.fill_between(R_zoom,
                  I_curvilinear(R_zoom, lam, alpha),
                  E_curvilinear(R_zoom, beta),
                  where=(I_curvilinear(R_zoom, lam, alpha) <
                         E_curvilinear(R_zoom, beta)),
                  alpha=0.15, color='red', label='R decreasing (E > I)')
if R_star_curv is not None:
    ax3b.axvline(R_star_curv, color='purple', linestyle='--', linewidth=2,
                 label=f'R* = {R_star_curv:.1f}')
ax3b.set_xlabel('Species Richness R', fontsize=11)
ax3b.set_ylabel('Rate (species / year)', fontsize=11)
ax3b.set_title('Stability Analysis (Curvilinear Model)', fontsize=11)
ax3b.legend(fontsize=8)
ax3b.grid(True, alpha=0.3)
ax3b.set_ylim(-0.1, 3)

fig3.tight_layout()
fig3.savefig(os.path.join(OUTPUT_DIR, 'fig3_curvilinear_model.png'), dpi=150)
plt.close(fig3)
print(f"Saved: fig3_curvilinear_model.png")

# -- Figure 4: Island size effect (Problem 2d) --------------------------------
fig4, axes4 = plt.subplots(1, 2, figsize=(13, 5))

colors = ['#e07b39', '#3a86ff', '#06d6a0']
R_sz = np.linspace(0, 1000, 2000)

ax4a = axes4[0]
for i, A in enumerate(ISLAND_AREAS):
    I_sz = I_size(R_sz, lam, alpha, A)
    E_sz = E_size(R_sz, beta, A)
    ax4a.plot(R_sz, I_sz, '-',  color=colors[i], linewidth=2,
              label=f'I(R), A={A}')
    ax4a.plot(R_sz, E_sz, '--', color=colors[i], linewidth=2,
              label=f'E(R), A={A}')
    if size_equilibria[A] is not None:
        ax4a.axvline(size_equilibria[A], color=colors[i], linestyle=':',
                     linewidth=1.2, alpha=0.8)

ax4a.set_xlabel('Species Richness R', fontsize=11)
ax4a.set_ylabel('Rate (species / year)', fontsize=11)
ax4a.set_title('Problem 2(d): Island Size Effect on I(R) and E(R)', fontsize=11)
ax4a.legend(fontsize=8, ncol=2)
ax4a.set_xlim(0, 900)
ax4a.set_ylim(-0.2, 12)
ax4a.grid(True, alpha=0.3)

# Right: equilibrium R* vs island area (species-area relationship)
A_range = np.logspace(-1, 2, 200)
R_star_A = [find_equilibrium_size(lam, alpha, beta, A) for A in A_range]
R_star_A = np.array([r if r is not None else np.nan for r in R_star_A])

ax4b = axes4[1]
ax4b.plot(A_range, R_star_A, 'k-', linewidth=2.5)
for i, A in enumerate(ISLAND_AREAS):
    if size_equilibria[A] is not None:
        ax4b.scatter([A], [size_equilibria[A]], color=colors[i], s=100,
                     zorder=5, label=f'A={A}: R*={size_equilibria[A]:.0f}')
ax4b.set_xscale('log')
ax4b.set_xlabel('Island Area A (relative units, log scale)', fontsize=11)
ax4b.set_ylabel('Equilibrium Species Richness R*', fontsize=11)
ax4b.set_title('Species-Area Relationship (Curvilinear Model)', fontsize=11)
ax4b.legend(fontsize=9)
ax4b.grid(True, alpha=0.3, which='both')

fig4.tight_layout()
fig4.savefig(os.path.join(OUTPUT_DIR, 'fig4_island_size_effect.png'), dpi=150)
plt.close(fig4)
print(f"Saved: fig4_island_size_effect.png")

# ---------------------------------------------------------------------------
# 10. Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Linear model:")
print(f"    I(R) = {a_I:.4f} + ({b_I:.6f})*R  (R²={r2_I:.4f})")
print(f"    E(R) = {a_E:.6f} + ({b_E:.6f})*R  (R²={r2_E:.4f})")
print(f"    Equilibrium R* = {R_star:.2f}")
print(f"    Mainland pool  P = {P:.1f}")
print(f"  Curvilinear model (lambda={lam}, alpha={alpha}, beta={beta}):")
if R_star_curv is not None:
    print(f"    Equilibrium R* = {R_star_curv:.2f}")
print(f"  Island size equilibria (curvilinear):")
for A in ISLAND_AREAS:
    r = size_equilibria[A]
    print(f"    A={A}: R* = {r:.1f}" if r else f"    A={A}: not found")
print(f"\nAll figures saved to: {OUTPUT_DIR}/")
