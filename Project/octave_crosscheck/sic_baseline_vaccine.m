% sic_baseline_vaccine.m
% ============================================================================
% Independent GNU Octave cross-check of the Python sIC HIV/AIDS model + vaccine.
%
% Mirrors EXACTLY the Python core in
%   Project/part2_hiv/sic.py
% (Haefner 2005, Modeling Biological Systems 2nd ed., Ch. 15; sIC = simplified
%  Imperial College AIDS model, Eqs 15.5a-f females / 15.7a-f males; force of
%  infection 15.6/15.8; Table 15.2 parameters), extended with a vaccine-
%  Protected compartment P (S -> P -> S take-with-waning).
%
% Modeling choices reproduced verbatim from sic.py:
%   * gamma = 0.1 /yr           (working value -> ~8 yr infectious period,
%                                R0 ~ 2.3, reproduces Fig 15.5; the literal
%                                Table 15.2 gamma=1.16 is sub-threshold).
%   * CONSERVATIVE ageing term xi*A_{.,1} in the AIDS age-2 inflow (NOT the
%                                book's printed xi*I_{.,1}).
%   * FREQUENCY-dependent FOI with P INCLUDED in the partner-pool denominator
%                                (S + I + P, age-2). A (AIDS) excluded.
%   * Cost accumulator V = integral of nu*(S_f2 + S_m2); money = $10 * V.
%   * Seed with INFECTIOUS males I_m2 = 5. The textbook literal seed A_m2 = 5
%                                CANNOT ignite (A excluded from the FOI); this
%                                is documented and demonstrated below.
%
% Runs (i) baseline nu=0 to 120 yr and (ii) vaccination nu=0.65, l=0.1, plots
% overall HIV prevalence for both, prints baseline equilibrium prevalence, and
% confirms vaccination drives prevalence down. Compare against Python:
%     baseline equilibrium prevalence ~ 0.41  (Python: 0.4085, peak 0.4087 @ ~96 yr)
%     vaccine prevalence -> ~0           (Python: ~0.001 peak, 0 at equilibrium)
%     literal A_m2=5-only seed peak     ~ 0.0006 (cannot ignite)
%
% This is an INDEPENDENT re-implementation transcribed from sic.py; it does NOT
% load Python.  Run:   octave sic_baseline_vaccine.m
% ============================================================================
%
% STATE VECTOR LAYOUT (length 15; matches sic.py IDX):
%    1 S_f1   2 S_f2   3 S_m1   4 S_m2
%    5 I_f1   6 I_f2   7 I_m1   8 I_m2
%    9 A_f1  10 A_f2  11 A_m1  12 A_m2
%   13 P_f2  14 P_m2  15 V (cumulative vaccinations, cost accumulator)
% ============================================================================

1;  % script file marker

function main()
  t_end = 120.0;
  tspan = linspace(0, t_end, 1201)';
  lsode_options("relative tolerance", 1e-8);
  lsode_options("absolute tolerance", 1e-10);

  % ---- (i) baseline: nu = 0, seed infectious males I_m2 = 5 ----
  Pb = sic_params();
  Pb.nu = 0.0;
  y0 = sic_initial_conditions(0.0, 5.0);   % seed_A_m2=0, seed_I_m2=5
  Yb = lsode(@(y, t) sic_rhs(y, t, Pb), y0, tspan);
  prev_b = prevalence_overall(Yb);
  [pkb, ib] = max(prev_b);

  % ---- (ii) vaccination: nu = 0.65, l = 0.1, same seed ----
  Pv = sic_params();
  Pv.nu = 0.65;
  Pv.l  = 0.1;
  Yv = lsode(@(y, t) sic_rhs(y, t, Pv), y0, tspan);
  prev_v = prevalence_overall(Yv);
  cumV = Yv(:, 15);                 % cumulative vaccinations
  cost = 10.0 * cumV;              % $10 per vaccination

  % ---- (iii) demonstrate the literal A_m2=5 seed cannot ignite ----
  Pa = sic_params();
  Pa.nu = 0.0;
  y0a = sic_initial_conditions(5.0, 0.0);  % seed_A_m2=5, seed_I_m2=0
  Ya = lsode(@(y, t) sic_rhs(y, t, Pa), y0a, tspan);
  prev_a = prevalence_overall(Ya);

  % ---- Report ----
  printf("\n==== Octave cross-check: sIC HIV model (gamma=0.1) ====\n");
  printf("BASELINE (nu=0, seed I_m2=5):\n");
  printf("  prevalence peak        : %.4f at t = %.1f yr  (Python ~0.4087 @ ~96 yr)\n", pkb, tspan(ib));
  printf("  prevalence equilibrium : %.4f (t=%.0f yr)     (Python ~0.4085)\n", prev_b(end), t_end);
  printf("VACCINATION (nu=0.65, l=0.1):\n");
  printf("  prevalence peak        : %.4f                 (Python ~0.001)\n", max(prev_v));
  printf("  prevalence equilibrium : %.4f (t=%.0f yr)     (Python ~0)\n", prev_v(end), t_end);
  printf("  cumulative vaccinations: %.1f                 (Python ~44484)\n", cumV(end));
  printf("  total cost (USD)       : %.1f                 (Python ~444841)\n", cost(end));
  if prev_v(end) < prev_b(end)
    printf("  => vaccination DRIVES prevalence DOWN (%.4f -> %.4f). CONFIRMED.\n", prev_b(end), prev_v(end));
  else
    printf("  => WARNING: vaccination did not reduce prevalence.\n");
  end
  printf("LITERAL SEED CHECK (A_m2=5 only, no I seed):\n");
  printf("  prevalence peak        : %.6f  (cannot ignite; A excluded from FOI)\n", max(prev_a));
  printf("=======================================================\n\n");

  % ---- Plot overall prevalence, baseline vs vaccine ----
  figure("visible", "off");
  plot(tspan, prev_b, "r-", "linewidth", 2); hold on;
  plot(tspan, prev_v, "b-", "linewidth", 2);
  xlabel("time (years)"); ylabel("overall HIV prevalence (I+A)/N");
  title("sIC HIV model (Octave cross-check): baseline vs vaccination");
  legend("baseline (nu=0)", "vaccine (nu=0.65, l=0.1)", "location", "northwest");
  grid on; ylim([0 0.5]);
  print("sic_baseline_vaccine_octave.png", "-dpng");
  printf("Saved plot: sic_baseline_vaccine_octave.png\n\n");
end

% ===========================================================================
% Parameters -- Table 15.2 (sic.py Params defaults), with gamma overridden to
% the documented working value 0.1 (see sic.py KEY MODELING CHOICES #5 and the
% module docstring). count_p_in_denominator is TRUE (P included in FOI pool).
% ===========================================================================
function P = sic_params()
  P.alpha   = 1.0;       % AIDS extra death rate /yr
  P.beta_fm = 0.075;     % female -> male per-partnership transmission prob
  P.beta_mf = 0.2;       % male -> female per-partnership transmission prob
  P.c       = 2.35;      % new-partner acquisition rate /yr
  P.eta     = 0.5;       % proportion of newborns that are female
  P.gamma   = 0.1;       % progression I -> A /yr  (WORKING value, not 1.16)
  P.mu      = 0.0227;    % natural (non-AIDS) death rate /yr
  P.rho     = 1.0;       % social mixing probability
  P.theta   = 0.2088;    % female fecundity (birth rate) /yr
  P.vartheta= 0.35;      % perinatal (mother->child) transmission prob
  P.xi      = 0.0667;    % ageing rate age1 -> age2 /yr
  P.zeta    = 1.0;       % proportion in the sexual-activity class

  P.nu      = 0.0;       % per-capita vaccination rate of S_{.,2} -> P /yr
  P.l       = 0.1;       % waning rate P -> S /yr

  P.count_p_in_denominator = true;  % P included in FOI partner pool (DEFAULT)
end

% ===========================================================================
% Initial conditions (Table 15.2), matching sic.initial_conditions.
%   S_f1=3000, S_f2=1000, S_m1=3000, S_m2=1000
%   A_m2 = seed_A_m2 (literal book seed=5; cannot ignite)
%   I_m2 = seed_I_m2 (ignition seed)
% ===========================================================================
function y0 = sic_initial_conditions(seed_A_m2, seed_I_m2)
  y0 = zeros(15, 1);
  y0(1) = 3000.0;   % S_f1
  y0(2) = 1000.0;   % S_f2
  y0(3) = 3000.0;   % S_m1
  y0(4) = 1000.0;   % S_m2
  y0(12) = seed_A_m2;  % A_m2
  y0(8)  = seed_I_m2;  % I_m2
end

% ===========================================================================
% Force of infection (Eqs 15.6 / 15.8), frequency-dependent.
%   lambda_Sf2 = c*rho*beta_mf * I_m2 / (S_m2 + I_m2 [+ P_m2])
%   lambda_Sm2 = c*rho*beta_fm * I_f2 / (S_f2 + I_f2 [+ P_f2])
% A (AIDS) excluded; P included by default. Denominator-zero -> lambda = 0.
% ===========================================================================
function [lam_f, lam_m] = forces_of_infection(y, P)
  S_f2 = y(2); S_m2 = y(4);
  I_f2 = y(6); I_m2 = y(8);
  P_f2 = y(13); P_m2 = y(14);

  if P.count_p_in_denominator
    pool_m = S_m2 + I_m2 + P_m2;
    pool_f = S_f2 + I_f2 + P_f2;
  else
    pool_m = S_m2 + I_m2;
    pool_f = S_f2 + I_f2;
  end

  if pool_m > 0.0
    freq_m = I_m2 / pool_m;
  else
    freq_m = 0.0;
  end
  if pool_f > 0.0
    freq_f = I_f2 / pool_f;
  else
    freq_f = 0.0;
  end

  lam_f = P.c * P.rho * P.beta_mf * freq_m;   % hazard for S_f2
  lam_m = P.c * P.rho * P.beta_fm * freq_f;   % hazard for S_m2
end

% ===========================================================================
% Right-hand side: full 15-ODE sIC + vaccination system.
% Signature (y, t) for Octave lsode. Uses the CONSERVATIVE ageing term
% xi*A_{.,1} in the AIDS age-2 equations (not the book's printed xi*I_{.,1}).
% ===========================================================================
function dy = sic_rhs(y, t, P)
  S_f1 = y(1);  S_f2 = y(2);  S_m1 = y(3);  S_m2 = y(4);
  I_f1 = y(5);  I_f2 = y(6);  I_m1 = y(7);  I_m2 = y(8);
  A_f1 = y(9);  A_f2 = y(10); A_m1 = y(11); A_m2 = y(12);
  P_f2 = y(13); P_m2 = y(14);

  [lam_f, lam_m] = forces_of_infection(y, P);

  eta = P.eta; theta = P.theta; zeta = P.zeta; vartheta = P.vartheta;
  mu = P.mu; xi = P.xi; gamma = P.gamma; alpha = P.alpha; nu = P.nu; l = P.l;

  % Reproduction (births from age-2 females only).
  births_S = theta * zeta * (S_f2 + (1.0 - vartheta) * I_f2);
  births_I = theta * zeta * vartheta * I_f2;

  dy = zeros(15, 1);

  % ---------------- FEMALES (15.5a-f, conservative) ----------------
  dy(1)  = eta * births_S - mu * S_f1 - xi * S_f1;                     % S_f1
  dy(2)  = xi * S_f1 - (lam_f + mu + nu) * S_f2 + l * P_f2;            % S_f2
  dy(5)  = eta * births_I - (mu + xi) * I_f1 - gamma * I_f1;           % I_f1
  dy(6)  = lam_f * S_f2 - (mu + gamma) * I_f2 + xi * I_f1;             % I_f2
  dy(9)  = gamma * I_f1 - (mu + xi + alpha) * A_f1;                    % A_f1
  dy(10) = gamma * I_f2 + xi * A_f1 - (mu + alpha) * A_f2;             % A_f2 (xi*A_f1)
  dy(13) = nu * S_f2 - (l + mu) * P_f2;                               % P_f2

  % ---------------- MALES (15.7a-f, conservative) ----------------
  dy(3)  = (1.0 - eta) * births_S - (mu + xi) * S_m1;                  % S_m1
  dy(4)  = xi * S_m1 - (lam_m + mu + nu) * S_m2 + l * P_m2;            % S_m2
  dy(7)  = (1.0 - eta) * births_I - (mu + xi) * I_m1 - gamma * I_m1;   % I_m1
  dy(8)  = lam_m * S_m2 - (mu + gamma) * I_m2 + xi * I_m1;             % I_m2
  dy(11) = gamma * I_m1 - (mu + xi + alpha) * A_m1;                    % A_m1
  dy(12) = gamma * I_m2 + xi * A_m1 - (mu + alpha) * A_m2;             % A_m2 (xi*A_m1)
  dy(14) = nu * S_m2 - (l + mu) * P_m2;                               % P_m2

  % ---------------- COST ACCUMULATOR ----------------
  dy(15) = nu * (S_f2 + S_m2);     % V = integral of nu*(S_f2+S_m2)
end

% ===========================================================================
% Overall prevalence = (all I + all A) / (all living people), V excluded.
% Y is (15 x n) from lsode (each ROW is a state across time? no: lsode returns
% n x 15, time down rows). We accept Y as (n x 15) and operate column-wise.
% ===========================================================================
function prev = prevalence_overall(Y)
  % Y is (n_times x 15) as returned by Octave's lsode.
  living_idx = [1 2 3 4 5 6 7 8 9 10 11 12 13 14];  % all except V (15)
  infected_idx = [5 6 7 8 9 10 11 12];              % I_* and A_*
  N = sum(Y(:, living_idx), 2);
  withvirus = sum(Y(:, infected_idx), 2);
  prev = zeros(size(N));
  nz = N > 0;
  prev(nz) = withvirus(nz) ./ N(nz);
end

% ---- run ----
main();
