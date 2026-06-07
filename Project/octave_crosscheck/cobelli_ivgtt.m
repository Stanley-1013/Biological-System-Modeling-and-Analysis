% cobelli_ivgtt.m
% ============================================================================
% Independent GNU Octave cross-check of the Python Cobelli (1982) glucose model.
%
% Mirrors EXACTLY the calibrated Python core in
%   Project/part1_glucose/cobelli.py
% (Haefner 2005, Modeling Biological Systems 2nd ed., Ch. 12; Cobelli,
%  Federspil, Pacini, Salvan & Scandellari 1982, Math. Biosci. 58:27-60).
%
% Runs a NORMAL IVGTT (0.33 g/kg bolus over 1 min, 70 kg subject) and reports
% the plasma glucose peak, the recovery time, and the plasma insulin peak, so a
% student can compare these against the Python results:
%     glucose peak  ~ 253 mg/100 ml  (Python: 253.3 at t=1 min)
%     recovery      ~ 51 min         (Python: ~51 min back within 5% of basal)
%     insulin peak  ~ 40 uU/ml       (Python: 40.2 at t=4 min)
%
% This is an INDEPENDENT re-implementation: the equations, parameters, units
% and the documented calibration are transcribed directly from cobelli.py and
% CALIBRATION_FINDINGS.md. It does NOT load any Python code.
%
% Run in Octave:   octave cobelli_ivgtt.m
% ============================================================================
%
% STATE VECTOR ORDER (fixed; matches cobelli.py IDX_* constants):
%   y(1) = g  glucose                (mg)
%   y(2) = c  glucagon               (nU)
%   y(3) = i  interstitial insulin   (uU)
%   y(4) = l  liver insulin          (uU)
%   y(5) = p  plasma insulin         (uU)
%   y(6) = r  releasable pancreatic insulin (uU)
%   y(7) = s  stored pancreatic insulin     (uU)
% ============================================================================

1;  % mark this file as a script, not a function file

function main()
  % ---- Build the calibrated NORMAL patient (params, volumes, basal) ----
  P = cobelli_params();          % Table 12.2 + documented calibration
  V = cobelli_volumes(70.0);     % 70 kg compartment volumes
  BC = cobelli_basal_conc();     % deviation reference concentrations
  y0 = cobelli_basal_amounts();  % calibrated basal steady state (IC)

  % ---- IVGTT forcing: 0.33 g/kg over 1 min for a 70 kg subject ----
  % dose = 0.33 g/kg * 70 kg * 1000 mg/g = 23100 mg, delivered over [0,1) min.
  dose_mg = 0.33 * 70.0 * 1000.0;   % = 23100 mg  (matches Python ex1_ivgtt)
  pulse_dur = 1.0;                  % min
  rate = dose_mg / pulse_dur;       % mg/min inside the window

  % ---- Integrate 0..180 min ----
  % lsode is Octave's built-in stiff/non-stiff integrator (LSODE/LSODA family),
  % the direct analogue of SciPy's LSODA used in the Python core.
  tspan = linspace(0, 180, 1801)';         % 0.1 min output grid
  lsode_options("relative tolerance", 1e-8);
  lsode_options("absolute tolerance", 1e-10);
  % cap the step so the 1-min bolus window is never stepped over
  lsode_options("maximum step size", 0.25);

  rhs = @(y, t) cobelli_rhs(y, t, P, V, BC, rate, pulse_dur);
  Y = lsode(rhs, y0, tspan);

  % ---- Convert to concentrations for plotting/reporting ----
  gbar = Y(:, 1) / V.Vb;    % mg/100 ml
  pbar = Y(:, 5) / V.Vp;    % uU/ml  (plasma insulin)

  % ---- Peak glucose and recovery time ----
  [gpk, ig] = max(gbar);
  gpk_t = tspan(ig);
  basal_g = BC.gbar;        % 91.5 mg/100 ml
  % recovery = first time after the peak that glucose falls back within 5% of basal
  recov = NaN;
  for k = ig:length(tspan)
    if gbar(k) <= basal_g * 1.05
      recov = tspan(k);
      break;
    end
  end

  [ppk, ip] = max(pbar);
  ppk_t = tspan(ip);

  % ---- Report ----
  printf("\n==== Octave cross-check: NORMAL IVGTT (0.33 g/kg, 70 kg) ====\n");
  printf("glucose peak       : %.2f mg/100 ml at t = %.2f min  (Python ~253.3 @ 1 min)\n", gpk, gpk_t);
  printf("recovery (<=5%% basal): %.1f min                       (Python ~51 min)\n", recov);
  printf("plasma insulin peak: %.2f uU/ml    at t = %.2f min  (Python ~40.2 @ 4 min)\n", ppk, ppk_t);
  printf("basal glucose / insulin: %.1f mg/100 ml / %.1f uU/ml\n", gbar(1), pbar(1));
  printf("============================================================\n\n");

  % ---- Plot ----
  figure("visible", "off");
  subplot(2, 1, 1);
  plot(tspan, gbar, "b-", "linewidth", 2); hold on;
  plot([0 180], [basal_g basal_g], "k--");
  xlabel("time (min)"); ylabel("plasma glucose (mg/100 ml)");
  title("Cobelli IVGTT (Octave cross-check) -- glucose");
  grid on;

  subplot(2, 1, 2);
  plot(tspan, pbar, "r-", "linewidth", 2); hold on;
  plot([0 180], [pbar(1) pbar(1)], "k--");
  xlabel("time (min)"); ylabel("plasma insulin (uU/ml)");
  title("Cobelli IVGTT (Octave cross-check) -- plasma insulin");
  grid on;

  print("cobelli_ivgtt_octave.png", "-dpng");
  printf("Saved plot: cobelli_ivgtt_octave.png\n\n");
end

% ===========================================================================
% Parameters -- Table 12.2 (NORMAL) plus the documented calibration.
% Values transcribed verbatim from cobelli.py NORMAL_PARAMS, with aw/a71/b52
% replaced by the runtime-calibrated values produced by cobelli.calibrate_basal
% (see CALIBRATION_FINDINGS.md). Those three numbers are computed in Python so
% the published clinical basal (91.5/11/75) is an EXACT steady state; they are
% hard-coded here (with the source) because Octave does not re-run the Python
% calibration. They were extracted by running cobelli.make_patient('normal').
% ===========================================================================
function P = cobelli_params()
  % --- GLUCOSE submodel ---
  P.a11 = 1.51;   P.b11 = 2.14;   P.b12 = 7.84e-2; P.b13 = 2.75e-2;
  P.c11 = -0.85;  P.c12 = 7.0;    P.c13 = 20.0;
  P.a221 = 1.95e-3; P.a222 = 5.21e-3; P.b21 = 1.11e-2; P.b22 = 1.45e-2;
  P.c21 = 51.3;   P.c22 = -108.5;
  P.a321 = 1.43e-5; P.a322 = -1.31e-5;
  P.b31 = 20.0;   P.c31 = -180.0;            % renal threshold ~180 mg/100 ml
  P.a41 = 2.87e-2; P.b41 = 3.1e-2; P.b42 = 1.44e-2; P.c41 = -50.9; P.c42 = -20.2;
  P.a51 = 1.01e-3; P.a52 = 4.6e-6; P.b51 = 2.78e-3;
  % P.b52 below is the CALIBRATED value (see note above), NOT the raw 4.13e-4.
  P.c51 = 1.002;
  % --- INSULIN submodel ---
  P.k12 = 0.01;   P.k21 = 4.34e-3;
  P.m01 = 0.125;  P.m02 = 0.185;  P.m12 = 0.209;  P.m13 = 0.02;
  P.m21 = 0.268;  P.m31 = 0.042;
  P.a6 = 1.3;     P.bw = 1.51e-2; P.b6 = 9.23e-2; P.cw = -92.3; P.c6 = -19.68;
  % --- GLUCAGON submodel ---
  P.b71 = 6.86e-3; P.b72 = 3.00e-2; P.c71 = 99.2; P.c72 = 40.0; P.h02 = 0.086;

  % --- Uniform glucose-flux turnover scale (CALIBRATION_FINDINGS.md item 1) ---
  P.glucose_flux_scale = 1.0e5;

  % --- CALIBRATED basal-balance scales (CALIBRATION_FINDINGS.md items 2 & 3) ---
  % Extracted from Python cobelli.make_patient('normal').params:
  %   aw  : insulin synthesis scale  (so basal W == required F6)
  %   a71 : glucagon secretion scale (so basal F7 == h02*c)
  %   b52 : F5 baseline offset       (so dg/dt == 0 at the clinical basal)
  % These replace the raw Table-12.2 aw=0.287, a71=2.35, b52=4.13e-4.
  P.aw  = 282472.33372232807;   % CALIBRATED (Python runtime value)
  P.a71 = 53200.957575179564;   % CALIBRATED (Python runtime value)
  P.b52 = 0.001469898073603483; % CALIBRATED (Python runtime value)
end

% ===========================================================================
% Compartment volumes (Haefner sec 12.3.1, body-weight based), matching
% cobelli.compute_volumes for a 70 kg subject. Vb is in (100 ml) units so
% g/Vb comes out in mg/100 ml; Vp,Vl,Vi are in ml so insulin is uU/ml.
% For 70 kg: Vb=140, Vp=3150, Vl=2100, Vi=7000.
% ===========================================================================
function V = cobelli_volumes(bw_kg)
  bw_g = bw_kg * 1000.0;
  V.Vb = (0.20  * bw_g) / 100.0;   % (100 ml) units
  V.Vp =  0.045 * bw_g;            % ml
  V.Vl =  0.030 * bw_g;            % ml
  V.Vi =  0.10  * bw_g;            % ml
end

% ===========================================================================
% Basal (deviation-reference) concentrations. gbar/pbar/cbar are the published
% clinical values; lbar/ibar are DERIVED from the insulin steady state in the
% Python calibrate_basal and hard-coded here (extracted from the Python run).
%   gbar=91.5, pbar=11, cbar=75 ; lbar=31.0263..., ibar=10.395
% ===========================================================================
function BC = cobelli_basal_conc()
  BC.gbar = 91.5;                 % mg/100 ml
  BC.pbar = 11.0;                 % uU/ml
  BC.cbar = 75.0;                 % nU/ml (working unit)
  BC.lbar = 31.02631578947368;    % uU/ml (DERIVED; Python value)
  BC.ibar = 10.395000000000001;   % uU/ml (DERIVED; Python value)
end

% ===========================================================================
% Calibrated basal amounts = the steady-state IC (Python basal_amounts).
% Extracted from cobelli.make_patient('normal').basal_amounts; gives a basal
% residual max|dy/dt| ~ 3.6e-12 (verified in Python).
%   g=12810, c=10500, i=72765, l=65155.263..., p=34650,
%   r=489323.394..., s=4902812.817...
% ===========================================================================
function y0 = cobelli_basal_amounts()
  y0 = [ 12810.0; ...
         10500.0; ...
         72765.00000000001; ...
         65155.26315789473; ...
         34650.0; ...
         489323.39455245447; ...
         4902812.817911306 ];
end

% ===========================================================================
% Right-hand side of the Cobelli 7-ODE system (Eqs 12.1-12.7).
% Signature is (y, t) to match Octave's lsode convention.
% Ig (glucose input, mg/min) is a rectangular pulse: rate on [0, pulse_dur).
% Ip (insulin input) = 0 for the IVGTT.
% ===========================================================================
function dy = cobelli_rhs(y, t, P, V, BC, rate, pulse_dur)
  g = y(1); c = y(2); i = y(3); l = y(4); pl = y(5); r = y(6); s = y(7);

  % --- concentrations ---
  gbar = g / V.Vb;
  cbar = c / V.Vb;
  ibar = i / V.Vi;
  lbar = l / V.Vl;

  % --- standardized deviations from basal reference ---
  dg = gbar - BC.gbar;
  dc = cbar - BC.cbar;
  di = ibar - BC.ibar;
  dl = lbar - BC.lbar;

  % --- gate helpers (sigmoidal limiting factors) ---
  sig_plus  = @(b, arg) 0.5 * (1.0 + tanh(b * arg));   % 0.5[1+tanh]
  sig_minus = @(b, arg) 0.5 * (1.0 - tanh(b * arg));   % 0.5[1-tanh]

  % --- F1: hepatic glucose production ---
  G1 = sig_plus(P.b11,  dc + P.c11);   % glucagon stimulates (+)
  H1 = sig_minus(P.b12, dl + P.c12);   % liver insulin suppresses (-)
  M1 = sig_minus(P.b13, dg + P.c13);   % glucose suppresses (-)
  F1 = P.a11 * G1 * H1 * M1;

  % --- F2: hepatic glucose uptake (normal mode: H2*M2) ---
  H2 = sig_minus(P.b21, dl + P.c21);
  M2 = P.a221 + P.a222 * sig_plus(P.b22, dg + P.c22);
  F2 = H2 * M2;

  NHGB = F1 - F2;

  % --- F3: renal excretion. M31 uses RAW gbar with b31,c31 (renal ~180). ---
  M31 = sig_plus(P.b31, gbar + P.c31);
  M32 = P.a321 * gbar + P.a322;
  F3 = M31 * M32;

  % --- F4: peripheral (muscle + adipose) use (normal mode) ---
  H4 = sig_plus(P.b41, di + P.c41);    % interstitial insulin drives (+)
  M4 = sig_plus(P.b42, dg + P.c42);    % glucose drives (+)
  F4 = P.a41 * H4 * M4;

  % --- F5: CNS + RBC uptake (insulin-independent) ---
  M51 = P.a51 * tanh(P.b51 * (dg + P.c51));
  M52 = P.a52 * dg + P.b52;
  F5 = M51 + M52;

  % --- F7: glucagon secretion (suppressed by insulin and glucose) ---
  H7 = sig_minus(P.b71, di + P.c71);
  M7 = sig_minus(P.b72, dg + P.c72);
  F7 = P.a71 * H7 * M7;

  % --- insulin source terms ---
  W  = 0.5 * P.aw * (1.0 + tanh(P.bw * (dg + P.cw)));
  F6 = 0.5 * P.a6 * (1.0 + tanh(P.b6 * (dg + P.c6))) * r;

  % --- exogenous glucose input (rectangular IVGTT bolus) ---
  if (t >= 0.0) && (t < pulse_dur)
    ig = rate;
  else
    ig = 0.0;
  end
  ip = 0.0;   % no insulin infusion in the IVGTT

  % --- uniform glucose-turnover scale on the four endogenous glucose fluxes ---
  S = P.glucose_flux_scale;

  % --- derivatives (Eqs 12.1-12.7) ---
  dg_dt = S * (NHGB - F3 - F4 - F5) + ig;                                % 12.1
  dc_dt = -P.h02 * c + F7;                                               % 12.2
  di_dt = -P.m13 * i + P.m31 * pl;                                       % 12.3
  dl_dt = -(P.m02 + P.m12) * l + P.m21 * pl + F6;                        % 12.4
  dp_dt = -(P.m01 + P.m21 + P.m31) * pl + P.m12 * l + P.m13 * i + ip;    % 12.5
  dr_dt =  P.k21 * s - P.k12 * r - F6;                                   % 12.6
  ds_dt = -P.k21 * s + P.k12 * r + W;                                    % 12.7

  dy = [dg_dt; dc_dt; di_dt; dl_dt; dp_dt; dr_dt; ds_dt];
end

% ---- run ----
main();
