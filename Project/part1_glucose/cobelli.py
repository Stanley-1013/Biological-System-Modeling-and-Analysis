"""Cobelli et al. (1982) intermediate-complexity glucose-insulin-glucagon model.

Reference: Haefner, J. W. (2005). *Modeling Biological Systems*, 2nd ed., Ch. 12
(restating Cobelli, Federspil, Pacini, Salvan & Scandellari (1982),
*Math. Biosci.* 58:27-60). Equations 12.1-12.7, Tables 12.1/12.2/12.3.

This module is the shared simulation core for Part 1 (exercises 1-7). It is
written as pure functions with immutable parameter handling -- callers override
parameters by passing dict overrides, which are copied, never mutated in place.

============================================================================
UNITS  (kept consistent everywhere; see research_notes/part1_glucose_expertise)
============================================================================
  Time            : minutes (Table 12.2 rate constants are per-minute;
                    a normal IVGTT recovers in ~90 min).
  Glucose amount g: mg            -> concentration gbar = g/Vb in mg/100 ml
  Insulin amounts p,l,i,r,s: uU   -> concentrations in uU/ml
  Glucagon amount c: nU           -> concentration cbar = c/Vb in nU/ml
  Volumes Vb,Vp,Vl,Vi: 100 ml units for glucose/glucagon; ml for insulin.
                    (see note in compute_volumes on the 100-ml convention)

NOTE on the mg/100 ml convention: the clinically reported glucose
concentration gbar is in mg/100 ml. To make gbar = g/Vb come out in mg/100 ml
when g is in mg, Vb must be expressed in units of (100 ml), i.e. Vb_in_ml/100.
Insulin concentrations are reported in uU/ml, so the insulin volumes are kept
in plain ml. This split is handled explicitly in compute_volumes and is the
only subtlety in the unit bookkeeping.

============================================================================
STATE VECTOR ORDER  (fixed, documented -- do not reorder)
============================================================================
  index 0 : g  glucose            (mg)
  index 1 : c  glucagon           (nU)
  index 2 : i  interstitial insulin (uU)
  index 3 : l  liver insulin      (uU)
  index 4 : p  plasma insulin     (uU)
  index 5 : r  releasable pancreatic insulin (uU)
  index 6 : s  stored pancreatic insulin     (uU)

============================================================================
TRANSCRIPTION FLAG (F3 renal flux)
============================================================================
The textbook prints M31 = 0.5[1 + tanh(b13(...))], but Table 12.2 lists
b31 = 20, c31 = -180. The renal-threshold reading (excretion turns on near
gbar = 180 mg/100 ml, the physiological renal threshold ~180 mg/dl,
StatPearls Physiology/Glycosuria) only works with b31, c31. We therefore use
b31 = 20, c31 = -180 and M31 operates on RAW gbar (not the deviation).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, Optional

import numpy as np
from scipy.integrate import solve_ivp

# ---------------------------------------------------------------------------
# State-vector index constants (fixed order; never reorder)
# ---------------------------------------------------------------------------
IDX_G = 0  # glucose            (mg)
IDX_C = 1  # glucagon           (nU)
IDX_I = 2  # interstitial insulin (uU)
IDX_L = 3  # liver insulin      (uU)
IDX_P = 4  # plasma insulin     (uU)
IDX_R = 5  # releasable insulin (uU)
IDX_S = 6  # stored insulin     (uU)

STATE_NAMES = ("g", "c", "i", "l", "p", "r", "s")
N_STATES = 7

# ---------------------------------------------------------------------------
# Basal (normal) plasma concentrations for a 70-kg adult (Haefner sec 12.2)
# ---------------------------------------------------------------------------
GLUCOSE_BASAL_CONC = 91.5   # mg/100 ml  (plasma glucose)
INSULIN_BASAL_CONC = 11.0   # uU/ml      (plasma insulin)
GLUCAGON_BASAL_CONC = 75.0  # pg/ml      (plasma glucagon)

# Glucagon basal in nU/ml. The state c is in nU and cbar = c/Vb is used in the
# tanh arguments. Cobelli's glucagon concentration unit is nU/ml; the 75 pg/ml
# figure is the clinical value. We treat the *standardized* glucagon deviation
# Dcbar = cbar - cbar_basal, so the absolute pg<->nU calibration cancels in
# every tanh argument that uses Dcbar (G1 uses Dcbar). We therefore define the
# basal glucagon concentration directly in the model's nU/ml working unit using
# the numeric value 75 (i.e. we adopt cbar_basal = 75 nU/ml). This is the
# convention used by the textbook's own simulations; documented here so the
# choice is explicit rather than hidden.
GLUCAGON_BASAL_CONC_WORK = 75.0  # nU/ml (working unit; see note above)

DEFAULT_BODY_WEIGHT_KG = 70.0

# Densities (g/ml). Notes say ~1.0 g/ml unless specified otherwise; no more
# precise value is given in Ch. 12, so we adopt 1.0 for all compartments and
# document the assumption.
DENSITY_BLOOD = 1.0
DENSITY_PLASMA = 1.0
DENSITY_LIVER = 1.0
DENSITY_INTERSTITIAL = 1.0


# ===========================================================================
# Parameters
# ===========================================================================
@dataclass(frozen=True)
class Volumes:
    """Compartment volumes for concentration scaling.

    Vb, Vc are in units of (100 ml) so that g/Vb and c/Vb come out in
    mg/100 ml and nU/100ml*... -- see compute_volumes. Vp, Vl, Vi are in ml
    so insulin concentrations come out in uU/ml.
    """

    Vb: float   # blood + extracellular fluid, in (100 ml) units (for glucose/glucagon)
    Vp: float   # plasma, in ml (for plasma insulin)
    Vl: float   # liver, in ml (for liver insulin)
    Vi: float   # interstitial fluid, in ml (for interstitial insulin)


def compute_volumes(
    body_weight_kg: float = DEFAULT_BODY_WEIGHT_KG,
    density_blood: float = DENSITY_BLOOD,
    density_plasma: float = DENSITY_PLASMA,
    density_liver: float = DENSITY_LIVER,
    density_interstitial: float = DENSITY_INTERSTITIAL,
) -> Volumes:
    """Body-weight-based compartment volumes (Haefner sec 12.3.1).

    Fractions of body weight (kg -> g via *1000), divided by density (g/ml):
      Vb = 0.20  * BW / blood_density           (blood + extracellular fluid)
      Vp = 0.045 * BW / plasma_density          (plasma)
      Vl = 0.030 * BW / liver_density           (liver)
      Vi = 0.10  * BW / interstitial_density    (interstitial fluid)

    BW in kg -> tissue mass in g (x1000); dividing by density (g/ml) gives ml.

    For glucose/glucagon we report concentration in mg/100 ml, so Vb is
    converted to (100 ml) units (ml / 100). For insulin we report uU/ml, so
    Vp, Vl, Vi stay in ml.
    """
    bw_g = body_weight_kg * 1000.0  # kg -> g
    vb_ml = 0.20 * bw_g / density_blood
    vp_ml = 0.045 * bw_g / density_plasma
    vl_ml = 0.030 * bw_g / density_liver
    vi_ml = 0.10 * bw_g / density_interstitial
    return Volumes(
        Vb=vb_ml / 100.0,  # (100 ml) units -> gbar in mg/100 ml
        Vp=vp_ml,          # ml -> pbar in uU/ml
        Vl=vl_ml,          # ml -> lbar in uU/ml
        Vi=vi_ml,          # ml -> ibar in uU/ml
    )


@dataclass(frozen=True)
class BasalConcentrations:
    """Basal (normal operating point) concentrations used to form deviations."""

    gbar: float   # mg/100 ml
    pbar: float   # uU/ml  (plasma insulin)
    lbar: float   # uU/ml  (liver insulin)
    ibar: float   # uU/ml  (interstitial insulin)
    cbar: float   # nU/ml  (glucagon, working unit)


@dataclass(frozen=True)
class BasalAmounts:
    """Basal amounts (the state-vector values at the basal operating point)."""

    g: float
    c: float
    i: float
    l: float
    p: float
    r: float
    s: float

    def to_array(self) -> np.ndarray:
        return np.array(
            [self.g, self.c, self.i, self.l, self.p, self.r, self.s], dtype=float
        )


# ---------------------------------------------------------------------------
# Table 12.2 nominal parameters (NORMAL patient).
# Keys mirror the textbook symbol names exactly.
# ---------------------------------------------------------------------------
NORMAL_PARAMS: Dict[str, float] = {
    # --- GLUCOSE submodel ---
    "a11": 1.51,
    "b11": 2.14,
    "b12": 7.84e-2,
    "b13": 2.75e-2,
    "c11": -0.85,
    "c12": 7.0,
    "c13": 20.0,
    "a221": 1.95e-3,
    "a222": 5.21e-3,
    "b21": 1.11e-2,
    "b22": 1.45e-2,
    "c21": 51.3,
    "c22": -108.5,
    "a321": 1.43e-5,
    "a322": -1.31e-5,
    "b31": 20.0,    # renal-threshold steepness (used for M31; see flag in module docstring)
    "c31": -180.0,  # renal threshold ~180 mg/100 ml
    "a41": 2.87e-2,
    "b41": 3.1e-2,
    "b42": 1.44e-2,
    "c41": -50.9,
    "c42": -20.2,
    "a51": 1.01e-3,
    "a52": 4.6e-6,
    "b51": 2.78e-3,
    "b52": 4.13e-4,
    "c51": 1.002,   # estimated (value missing from Cobelli et al. 1982)
    # --- INSULIN submodel ---
    "k12": 0.01,
    "k21": 4.34e-3,
    "m01": 0.125,
    "m02": 0.185,
    "m12": 0.209,
    "m13": 0.02,
    "m21": 0.268,
    "m31": 0.042,
    "aw": 0.287,
    "a6": 1.3,
    "bw": 1.51e-2,
    "b6": 9.23e-2,
    "cw": -92.3,
    "c6": -19.68,
    # --- GLUCAGON submodel ---
    "a71": 2.35,
    "b71": 6.86e-3,
    "b72": 3.00e-2,
    "c71": 99.2,
    "c72": 40.0,
    "h02": 0.086,
    # --- Diabetic-mode constants (only used when mode == 'diabetic') ---
    # Table 12.3 says "F2 and H2 are replaced by constants" for the diabetic:
    # the insulin-driven hepatic glucose-uptake pathway stops responding to
    # insulin and is pinned to a constant. The *literal* table value F2 = 0.037
    # is in the textbook's native (un-scaled) flux units; our core multiplies the
    # four glucose fluxes by glucose_flux_scale = 1e5, so 0.037 would become a
    # ~3700 mg/min constant hepatic "vacuum" (~70x the normal basal F2 of
    # ~52 mg/min) that clamps glucose flat -- physiologically backwards. The
    # scale-consistent reading of "F2 frozen to a constant" is to pin it at (or
    # just below) the NORMAL basal hepatic-uptake flux, i.e. the liver can no
    # longer RAMP uptake with insulin but is not turned into a sink. We therefore
    # freeze F2 to the normal basal F2 gate product (~5.25e-4 unscaled =>
    # ~52 mg/min scaled). See calibrate_diabetic_basal and DIABETIC_BASAL below.
    "F2_const": 5.25e-4,  # diabetic: F2 frozen near the NORMAL basal hepatic uptake
    "H4_const": 0.0012,   # diabetic & obese: H4 frozen to this constant (Table 12.3)
    # --- Glucose-flux turnover scale (see GLUCOSE_FLUX_SCALE note below) ---
    "glucose_flux_scale": 1.0e5,
}

# ---------------------------------------------------------------------------
# GLUCOSE-FLUX TURNOVER SCALE  (documented model-scaling decision)
# ---------------------------------------------------------------------------
# Haefner's Ch. 12 transcription of the glucose-flux scale coefficients
# (a11, a221/a222, a41, a51, a52, b52) yields hepatic/peripheral/CNS/renal
# fluxes of order ~1e-3 (mg/100ml)/min. Against the glucose pool (~1.3e4 mg,
# ~91.5 mg/100ml) this gives a glucose relaxation time of ~1e6 min -- the
# literal table CANNOT reproduce the Fig 12.4 ~90-min IVGTT recovery; the
# overall glucose-turnover scale is under-specified by the textbook table.
#
# We correct this with ONE uniform, physiologically-motivated turnover scale
# applied to the four glucose fluxes (NHGB, F3, F4, F5). It changes NO tanh
# shape parameter, NO feedback structure, NO transfer/secretion rate -- only
# the single overall glucose-flux magnitude the table leaves ill-determined,
# exactly analogous to the aw/a71 basal calibration. Because at basal the
# fluxes already balance (NHGB ~= F3+F4+F5), multiplying all four by the same
# scale leaves the basal steady state EXACTLY unchanged; it only sets the
# clearance timescale. The default 1.0e5 was chosen so a standard IVGTT
# (0.33 g/kg) recovers in ~70-90 min, matching Fig 12.4. It is exposed as a
# parameter so it can be re-tuned or disabled (set to 1.0) for sensitivity
# studies.
GLUCOSE_FLUX_SCALE = 1.0e5

# ---------------------------------------------------------------------------
# Table 12.3 overrides (on top of Table 12.2).
# ---------------------------------------------------------------------------
DIABETIC_OVERRIDES: Dict[str, float] = {
    # F2 and H2 are "replaced by constants" -> handled via the mode flag +
    # F2_const (scale-consistent value documented in NORMAL_PARAMS above) and
    # H4_const. The Table 12.3 secretion/uptake-shape changes are listed here.
    "H4_const": 0.0012,
    "b42": 7e-3,
    "c42": -40.47,
    "bw": 4.5e-3,
    "b6": 5e-3,
    "c6": -363.55,
    "cw": -306.25,
}

# ---------------------------------------------------------------------------
# DIABETIC OPERATING POINT  (documented model-scaling decision; see §12.3.6)
# ---------------------------------------------------------------------------
# Haefner §12.3.6 / Fig 12.6: the diabetic subject has a DIFFERENT basal
# operating point -- fasting glucose is much HIGHER than the normal 91.5, plasma
# insulin is LOWER (blunted secretion), and IVGTT recovery is ~2x slower.
#
# The normal subject is anchored to the published clinical basal (91.5/11/75) by
# choosing the under-determined source/clearance scales (aw, a71, b52) so that
# point is an exact steady state (calibrate_basal). The strong glucose
# self-suppression (M1) and glucagon feedback (G1) make 91.5 a robust attractor,
# so merely freezing the insulin-driven uptake gates does NOT relocate the basal
# -- the only faithful way to obtain the elevated diabetic basal is to calibrate
# the diabetic to its OWN operating point, exactly analogous to how the normal
# subject is calibrated to its operating point (and exactly the "scale the model
# to a particular patient" use the model is designed for; Cobelli et al. 1982).
#
# We therefore target a documented diabetic fasting state and recalibrate the
# SAME three under-determined scales (aw, a71, b52) -- no tanh shape parameter,
# no transfer rate, no feedback structure is changed:
#   * gbar = 140 mg/100 ml  : a representative diabetic fasting hyperglycaemia
#     (elevated vs 91.5; sits below the ~180 renal threshold so the elevation is
#     not just renal spill). This is the operating-point target.
#   * pbar = 7  uU/ml        : blunted plasma insulin (below the normal 11),
#     i.e. reduced beta-cell secretion (Type-I/II), so insulin is honestly low.
#   * cbar = 75 nU/ml        : glucagon kept at the normal reference; pushing it
#     higher makes the (hypersensitive) glucagon gate G1 inflate hepatic
#     production into an unphysical regime, so we keep it at reference.
# At this operating point the liver-insulin level is low, so the (UNFROZEN,
# published) H1 gate naturally sits HIGH (~0.66 vs 0.25 normal): hepatic glucose
# production is no longer suppressed by insulin -- the textbook diabetic
# mechanism -- and it emerges from the model rather than being hand-forced.
DIABETIC_BASAL = {
    "gbar": 140.0,  # elevated fasting glucose (mg/100 ml)
    "pbar": 7.0,    # blunted plasma insulin (uU/ml)
    "cbar": 75.0,   # glucagon at the normal reference (nU/ml)
}

OBESE_OVERRIDES: Dict[str, float] = {
    "H4_const": 0.0012,
    "b42": 7e-3,
    "c42": 40.47,   # sign flip vs diabetic (Table 12.3)
    "b6": 0.5,
    "c6": -3.64,
    "m02": 0.13,
}


@dataclass(frozen=True)
class Patient:
    """A complete, immutable patient specification.

    mode is one of 'normal', 'diabetic', 'obese' and controls the F2/H2/H4
    constant-replacement switches required by Table 12.3.
    """

    params: Dict[str, float]
    volumes: Volumes
    basal_conc: BasalConcentrations
    basal_amounts: BasalAmounts
    mode: str = "normal"
    body_weight_kg: float = DEFAULT_BODY_WEIGHT_KG


def _merge_params(overrides: Optional[Dict[str, float]]) -> Dict[str, float]:
    """Return a fresh params dict = NORMAL with overrides applied (immutable)."""
    merged = dict(NORMAL_PARAMS)  # copy; never mutate the module-level default
    if overrides:
        merged.update(overrides)
    return merged


def make_basal_concentrations(
    glucagon_basal: float = GLUCAGON_BASAL_CONC_WORK,
) -> BasalConcentrations:
    """Clinically measured basal plasma concentrations (deviation references).

    The plasma quantities are pinned to the published clinical values:
      gbar = 91.5 mg/100 ml, pbar = 11 uU/ml, cbar = 75 nU/ml.
    The liver- and interstitial-insulin basal concentrations are NOT measured
    clinically; they are *derived* from the steady-state of the insulin
    transfer equations (Eqs 12.3-12.5) in calibrate_basal, which overwrites the
    placeholder values set here. We initialize them to pbar as a placeholder.
    """
    return BasalConcentrations(
        gbar=GLUCOSE_BASAL_CONC,
        pbar=INSULIN_BASAL_CONC,
        lbar=INSULIN_BASAL_CONC,   # placeholder; replaced by calibrate_basal
        ibar=INSULIN_BASAL_CONC,   # placeholder; replaced by calibrate_basal
        cbar=glucagon_basal,
    )


def calibrate_basal(params: Dict[str, float], vols: Volumes,
                    basal_conc: BasalConcentrations):
    """Make the published clinical basal an EXACT steady state.

    WHY THIS IS NEEDED (documented design decision):
    Haefner's Ch. 12 transcription of Table 12.2 does NOT yield a self-
    consistent basal steady state at the published clinical concentrations
    (gbar=91.5, pbar=11, cbar=75). Concretely, the published insulin-synthesis
    scale (aw) and glucagon-secretion scale (a71) sustain only ~1e-5 uU/ml
    plasma insulin and ~0.004 nU/ml glucagon -- i.e. the insulin and glucagon
    axes collapse to ~0 if you integrate forward from the clinical basal. That
    makes any IVGTT impossible (no insulin to respond). A blind 7-D root solve
    diverges to an unphysical (negative-glucose) state.

    The rigorous, physiologically honest fix -- and exactly what "scaling the
    model to a particular patient's normal operating point" means in Cobelli's
    framework -- is to choose the under-determined basal-balance RATE SCALES so
    the published clinical basal is the steady state, while leaving every tanh
    SHAPE parameter (all b's and c's, the gate structure, every transfer rate
    mij/kij) exactly as printed in Table 12.2. We recalibrate THREE
    under-determined basal-balance scale/offset constants (all disclosed and
    motivated below and in the report):
      * aw  : insulin synthesis scale, so basal synthesis W == required basal
              secretion F6 (forced by d(r+s)/dt = W - F6 = 0 at equilibrium).
      * a71 : glucagon secretion scale, so F7 == h02*c at basal.
      * b52 : the insulin-independent CNS/RBC baseline glucose sink (F5 offset),
              shifted by the tiny published NHGB-(F3+F4+F5) imbalance so that
              dg/dt == 0 at the clinical basal exactly (see block below). This is
              a constant offset, not a tanh slope/centre, so it preserves shapes.
    Separately, a single uniform `glucose_flux_scale` multiplies the four glucose
    fluxes to set the (otherwise ~1e6 min, non-physical) clearance timescale to
    the ~90 min of Fig 12.4; because NHGB==F3+F4+F5 at basal, a common scale
    cancels and leaves the steady state and every feedback shape exactly intact.
    We DERIVE the internal basal quantities (lbar, ibar, r, s) from the
    steady-state relations of Eqs 12.3-12.7.

    NOTE (honesty): the literal Haefner Table 12.2 does NOT reproduce Figs
    12.4a/b -- its glucose-flux coefficients are ~5 orders too small (amount
    form) and basal insulin synthesis is ~6 orders too small to sustain the
    plasma pool. These calibrations are the documented minimal fix and MUST be
    reported as such; they are not claimed to be the original Cobelli values.

    Returns (params_calibrated, basal_conc_calibrated, basal_amounts).
    All returned objects are fresh; inputs are not mutated.
    """
    p = dict(params)  # copy; never mutate caller's dict

    # --- Pin plasma quantities from clinical basal concentrations ---
    g_amt = basal_conc.gbar * vols.Vb           # mg
    p_amt = basal_conc.pbar * vols.Vp           # uU
    c_amt = basal_conc.cbar * vols.Vb           # nU

    # --- Glucose basal balance: make NHGB == F3+F4+F5 at basal exactly, by
    #     absorbing the tiny published imbalance into the insulin-independent
    #     CNS+RBC baseline sink b52 (the natural balancing constant). This makes
    #     dg/dt = 0 at the clinical basal regardless of the glucose_flux_scale.
    #     b52 is the F5 baseline (M52 = a52*Dgbar + b52); at basal Dgbar=0 so
    #     F5_baseline contains b52. Evaluate the unscaled glucose imbalance at
    #     the basal amounts and add it to b52. ---
    y_basal_tmp = np.array(
        [g_amt, c_amt,
         p["m31"] * p_amt / p["m13"],                                # i (eq 12.3)
         ((p["m01"] + p["m21"] + p["m31"]) * p_amt
          - p["m13"] * (p["m31"] * p_amt / p["m13"])) / p["m12"],    # l (eq 12.5)
         p_amt, p_amt, 10.0 * p_amt],                                # p, r(seed), s(seed)
        dtype=float,
    )
    bc_tmp = BasalConcentrations(
        gbar=basal_conc.gbar, pbar=basal_conc.pbar,
        lbar=y_basal_tmp[3] / vols.Vl, ibar=y_basal_tmp[2] / vols.Vi,
        cbar=basal_conc.cbar,
    )
    f0 = compute_fluxes(y_basal_tmp, p, bc_tmp, vols, mode="normal")
    dg_unscaled = f0.NHGB - f0.F3 - f0.F4 - f0.F5
    p["b52"] = p["b52"] + dg_unscaled

    # --- Insulin compartments from steady state of Eqs 12.3-12.5 ---
    # (12.3) 0 = -m13*i + m31*p  ->  i = m31/m13 * p
    i_amt = p["m31"] * p_amt / p["m13"]
    # (12.5) 0 = -(m01+m21+m31)*p + m12*l + m13*i  ->  l = ((..)*p - m13*i)/m12
    l_amt = ((p["m01"] + p["m21"] + p["m31"]) * p_amt - p["m13"] * i_amt) / p["m12"]
    l_bar = l_amt / vols.Vl
    i_bar = i_amt / vols.Vi

    # --- Required basal secretion F6 from liver-insulin balance (12.4) ---
    # 0 = -(m02+m12)*l + m21*p + F6  ->  F6 = (m02+m12)*l - m21*p
    F6_req = (p["m02"] + p["m12"]) * l_amt - p["m21"] * p_amt

    # --- Calibrate aw so synthesis W(basal) == F6_req (since W==F6 at eq) ---
    # W = 0.5*aw*(1+tanh(bw*(Dgbar+cw))); at basal Dgbar=0.
    gate_w = 0.5 * (1.0 + np.tanh(p["bw"] * p["cw"]))
    if gate_w <= 0:
        raise ValueError("degenerate W gate at basal; cannot calibrate aw")
    p["aw"] = F6_req / gate_w

    # --- Derive releasable/stored pools from secretion/synthesis balance ---
    # F6 = 0.5*a6*(1+tanh(b6*(Dgbar+c6)))*r ; at basal Dgbar=0  ->  r = F6_req/gate6
    gate6 = 0.5 * p["a6"] * (1.0 + np.tanh(p["b6"] * p["c6"]))
    if gate6 <= 0:
        raise ValueError("degenerate F6 gate at basal; cannot derive r")
    r_amt = F6_req / gate6
    # (12.7) 0 = -k21*s + k12*r + W  ->  s = (k12*r + W)/k21 , with W=F6_req
    s_amt = (p["k12"] * r_amt + F6_req) / p["k21"]

    # --- Calibrate a71 so glucagon balance (12.2) holds: F7 == h02*c ---
    # F7 = a71*H7*M7 ; at basal Dibar=Dgbar=0.
    gate_f7 = (0.5 * (1.0 - np.tanh(p["b71"] * p["c71"]))
               * 0.5 * (1.0 - np.tanh(p["b72"] * p["c72"])))
    if gate_f7 <= 0:
        raise ValueError("degenerate F7 gate at basal; cannot calibrate a71")
    p["a71"] = p["h02"] * c_amt / gate_f7

    basal_conc_cal = BasalConcentrations(
        gbar=basal_conc.gbar,
        pbar=basal_conc.pbar,
        lbar=l_bar,
        ibar=i_bar,
        cbar=basal_conc.cbar,
    )
    basal_amounts = BasalAmounts(
        g=g_amt, c=c_amt, i=i_amt, l=l_amt, p=p_amt, r=r_amt, s=s_amt
    )
    return p, basal_conc_cal, basal_amounts


def calibrate_diabetic_basal(
    params: Dict[str, float],
    vols: Volumes,
    ref_conc: BasalConcentrations,
    target: Dict[str, float] = DIABETIC_BASAL,
):
    """Calibrate the diabetic subject to its OWN elevated operating point.

    WHY A SEPARATE CALIBRATION (documented, honest):
    The normal calibration anchors the published clinical basal (91.5/11/75) as
    an exact steady state. Because the glucose self-suppression gate M1 and the
    glucagon gate G1 make 91.5 a strong attractor, simply freezing the diabetic's
    insulin-driven uptake gates does NOT move the basal -- the system relaxes
    straight back to ~91.5 (verified). Reproducing Fig 12.6's ELEVATED diabetic
    fasting glucose therefore requires calibrating the diabetic to its own
    operating point, exactly as the normal subject is calibrated to its own --
    this is the intended "scale the model to a particular patient" use of the
    Cobelli model (Haefner §12.3; Cobelli et al. 1982).

    WHAT IS (AND IS NOT) CHANGED:
    Deviations are still formed against the NORMAL clinical reference
    (gbar=91.5, ibar, lbar, cbar=75) -- this is what makes the diabetic state
    GENUINELY elevated/blunted rather than re-zeroed. We recalibrate ONLY the
    same three under-determined source/clearance scales the normal calibration
    uses (aw, a71, b52), so that the documented diabetic fasting state
    (DIABETIC_BASAL: gbar=140, pbar=7, cbar=75) is an exact steady state. Every
    tanh SHAPE parameter (all b's and c's), every transfer rate (mij/kij), the
    glucose_flux_scale, and all the Table 12.3 overrides are left exactly as set.
    The frozen F2_const / H4_const enter through compute_fluxes(mode='diabetic').
    H1 (insulin suppression of hepatic production) is NOT frozen: at the low
    liver-insulin diabetic state it naturally sits high (~0.66 vs 0.25 normal),
    so the liver keeps producing -- the textbook mechanism, emergent not forced.

    Returns (params_calibrated, ref_conc_unchanged, diabetic_basal_amounts).
    All returned objects are fresh; inputs are not mutated.
    """
    p = dict(params)  # copy; never mutate caller's dict
    S = p.get("glucose_flux_scale", 1.0)

    g_d, p_d, c_d = target["gbar"], target["pbar"], target["cbar"]
    g_amt = g_d * vols.Vb
    p_amt = p_d * vols.Vp
    c_amt = c_d * vols.Vb

    # Deviations of the diabetic operating point from the NORMAL reference.
    dg = g_d - ref_conc.gbar
    dc = c_d - ref_conc.cbar

    # --- Insulin compartments from steady state of Eqs 12.3-12.5 (at p_amt) ---
    i_amt = p["m31"] * p_amt / p["m13"]                                  # (12.3)
    l_amt = ((p["m01"] + p["m21"] + p["m31"]) * p_amt
             - p["m13"] * i_amt) / p["m12"]                             # (12.5)
    l_bar = l_amt / vols.Vl
    i_bar = i_amt / vols.Vi
    di = i_bar - ref_conc.ibar
    dl = l_bar - ref_conc.lbar

    # --- Required basal secretion F6 from liver-insulin balance (12.4) ---
    F6_req = (p["m02"] + p["m12"]) * l_amt - p["m21"] * p_amt
    if F6_req <= 0:
        raise ValueError("diabetic F6_req <= 0; pick a higher pbar target")

    # --- Calibrate aw so synthesis W == F6_req at the DIABETIC glucose level ---
    gate_w = 0.5 * (1.0 + np.tanh(p["bw"] * (dg + p["cw"])))
    if gate_w <= 0:
        raise ValueError("degenerate W gate at diabetic basal; cannot set aw")
    p["aw"] = F6_req / gate_w

    # --- Releasable/stored pools from secretion/synthesis balance (at dg) ---
    gate6 = 0.5 * p["a6"] * (1.0 + np.tanh(p["b6"] * (dg + p["c6"])))
    if gate6 <= 0:
        raise ValueError("degenerate F6 gate at diabetic basal; cannot derive r")
    r_amt = F6_req / gate6
    s_amt = (p["k12"] * r_amt + F6_req) / p["k21"]                       # (12.7)

    # --- Calibrate a71 so glucagon balance (12.2) holds at the diabetic state ---
    gate_f7 = (0.5 * (1.0 - np.tanh(p["b71"] * (di + p["c71"])))
               * 0.5 * (1.0 - np.tanh(p["b72"] * (dg + p["c72"]))))
    if gate_f7 <= 0:
        raise ValueError("degenerate F7 gate at diabetic basal; cannot set a71")
    p["a71"] = p["h02"] * c_amt / gate_f7

    # --- Calibrate b52 (F5 baseline offset) so dg/dt == 0 at the diabetic basal.
    #     Mirror the diabetic-mode fluxes EXACTLY (F2 frozen, H4 frozen, H1 not
    #     frozen) and solve NHGB - F3 - F4 - F5 == 0 for b52. b52 is a constant
    #     offset, not a tanh slope/centre, so all feedback shapes are preserved.
    G1 = 0.5 * (1.0 + np.tanh(p["b11"] * (dc + p["c11"])))
    H1 = 0.5 * (1.0 - np.tanh(p["b12"] * (dl + p["c12"])))   # UNFROZEN, naturally high
    M1 = 0.5 * (1.0 - np.tanh(p["b13"] * (dg + p["c13"])))
    F1 = p["a11"] * G1 * H1 * M1
    F2 = p["F2_const"]                                       # frozen (diabetic)
    NHGB = F1 - F2
    M31 = 0.5 * (1.0 + np.tanh(p["b31"] * (g_d + p["c31"])))
    M32 = p["a321"] * g_d + p["a322"]
    F3 = M31 * M32
    M4 = 0.5 * (1.0 + np.tanh(p["b42"] * (dg + p["c42"])))
    F4 = p["a41"] * p["H4_const"] * M4                       # H4 frozen (diabetic)
    M51 = p["a51"] * np.tanh(p["b51"] * (dg + p["c51"]))
    # Require F5 = M51 + a52*dg + b52 == NHGB - F3 - F4  ->  solve b52.
    p["b52"] = (NHGB - F3 - F4) - M51 - p["a52"] * dg

    # ref_conc is UNCHANGED: deviations stay framed against the normal reference,
    # which is what keeps the diabetic state genuinely elevated/blunted.
    diabetic_amounts = BasalAmounts(
        g=g_amt, c=c_amt, i=i_amt, l=l_amt, p=p_amt, r=r_amt, s=s_amt
    )
    return p, ref_conc, diabetic_amounts


def make_patient(
    mode: str = "normal",
    body_weight_kg: float = DEFAULT_BODY_WEIGHT_KG,
    extra_overrides: Optional[Dict[str, float]] = None,
    calibrate: bool = True,
) -> Patient:
    """Construct an immutable Patient for the given mode.

    mode: 'normal' | 'diabetic' | 'obese'
    extra_overrides: optional dict of additional parameter overrides applied
        LAST (used e.g. by exercise 5 hyperinsulinism to bump a6). Copied;
        the caller's dict is never mutated.
    calibrate: if True (default), recalibrate the under-determined basal-balance
        scales (aw, a71) and derive the internal basal amounts so the published
        clinical basal is an exact steady state (see calibrate_basal). All tanh
        shape parameters and transfer rates stay exactly as in Table 12.2.

    NOTE on diabetic/obese basal: those subjects have a DIFFERENT basal
    operating point (higher glucose, lower insulin for diabetes). The clinical
    91.5/11/75 references are the NORMAL operating point.

    * DIABETIC: calibrated to its OWN elevated operating point
      (calibrate_diabetic_basal -> DIABETIC_BASAL = 140/7/75). Deviations are
      still framed against the normal clinical reference, so the diabetic basal
      is genuinely elevated (glucose) and blunted (insulin). The returned
      basal_amounts ARE the diabetic steady state, so basal_amounts.to_array()
      is a ready IC (settle_to_basal is a no-op refinement on it).
    * OBESE: still calibrated to the normal clinical basal (aw/a71 anchored
      there); its pathological steady state emerges from the altered parameters
      when integrated. Downstream exercises pre-equilibrate via settle_to_basal.
    """
    mode = mode.lower()
    if mode == "normal":
        overrides: Dict[str, float] = {}
    elif mode == "diabetic":
        overrides = dict(DIABETIC_OVERRIDES)
    elif mode == "obese":
        overrides = dict(OBESE_OVERRIDES)
    else:
        raise ValueError(f"unknown mode {mode!r}; expected normal/diabetic/obese")

    if extra_overrides:
        overrides = {**overrides, **extra_overrides}

    params = _merge_params(overrides)
    vols = compute_volumes(body_weight_kg)
    basal_conc = make_basal_concentrations()

    if calibrate:
        # First anchor the NORMAL clinical reference (gives calibrated lbar/ibar
        # used to frame deviations, plus the normal aw/a71/b52).
        params, basal_conc, basal_amounts = calibrate_basal(params, vols, basal_conc)
        if mode == "diabetic":
            # Then recalibrate aw/a71/b52 to the diabetic OWN operating point
            # (elevated glucose, blunted insulin). basal_conc (the deviation
            # reference) is intentionally left at the normal clinical reference.
            params, basal_conc, basal_amounts = calibrate_diabetic_basal(
                params, vols, basal_conc
            )
    else:
        # Uncalibrated path: seed amounts directly (used only for diagnostics).
        basal_amounts = BasalAmounts(
            g=basal_conc.gbar * vols.Vb,
            c=basal_conc.cbar * vols.Vb,
            i=basal_conc.ibar * vols.Vi,
            l=basal_conc.lbar * vols.Vl,
            p=basal_conc.pbar * vols.Vp,
            r=basal_conc.pbar * vols.Vp,
            s=10.0 * basal_conc.pbar * vols.Vp,
        )

    return Patient(
        params=params,
        volumes=vols,
        basal_conc=basal_conc,
        basal_amounts=basal_amounts,
        mode=mode,
        body_weight_kg=body_weight_kg,
    )


# ===========================================================================
# Concentration helpers
# ===========================================================================
@dataclass(frozen=True)
class Concentrations:
    gbar: float  # mg/100 ml
    cbar: float  # nU/ml
    ibar: float  # uU/ml
    lbar: float  # uU/ml
    pbar: float  # uU/ml


def amounts_to_concentrations(y: np.ndarray, vols: Volumes) -> Concentrations:
    """Convert a state-amount vector to concentrations for plotting/analysis."""
    return Concentrations(
        gbar=y[IDX_G] / vols.Vb,
        cbar=y[IDX_C] / vols.Vb,
        ibar=y[IDX_I] / vols.Vi,
        lbar=y[IDX_L] / vols.Vl,
        pbar=y[IDX_P] / vols.Vp,
    )


# ===========================================================================
# Auxiliary fluxes (Eqs 12.1-12.7)
# ===========================================================================
def _sig_plus(b: float, arg: float) -> float:
    """0.5[1 + tanh(b*arg)] -- stimulatory gate, 0->1 as driver rises."""
    return 0.5 * (1.0 + np.tanh(b * arg))


def _sig_minus(b: float, arg: float) -> float:
    """0.5[1 - tanh(b*arg)] -- inhibitory gate, 1->0 as driver rises."""
    return 0.5 * (1.0 - np.tanh(b * arg))


@dataclass(frozen=True)
class Fluxes:
    """All auxiliary fluxes and the gates, for inspection / plotting."""

    NHGB: float
    F1: float
    F2: float
    F3: float
    F4: float
    F5: float
    F6: float
    F7: float
    G1: float
    H1: float
    M1: float
    H2: float
    M2: float
    M31: float
    M32: float
    H4: float
    M4: float
    M51: float
    M52: float
    H7: float
    M7: float
    W: float


def compute_fluxes(
    y: np.ndarray,
    params: Dict[str, float],
    basal_conc: BasalConcentrations,
    vols: Volumes,
    mode: str = "normal",
) -> Fluxes:
    """Compute every auxiliary flux exactly as in Haefner Ch. 12.

    Standardized deviations are formed against basal_conc:
        Dgbar = gbar - gbar_basal, etc.
    For the renal flux M31 the RAW gbar is used (absolute 180 threshold).
    """
    p = params
    # Concentrations
    gbar = y[IDX_G] / vols.Vb
    cbar = y[IDX_C] / vols.Vb
    ibar = y[IDX_I] / vols.Vi
    lbar = y[IDX_L] / vols.Vl
    r = y[IDX_R]

    # Standardized deviations
    dg = gbar - basal_conc.gbar
    dc = cbar - basal_conc.cbar
    di = ibar - basal_conc.ibar
    dl = lbar - basal_conc.lbar

    # --- F1: hepatic glucose production (multiplicative limiting factors) ---
    G1 = _sig_plus(p["b11"], dc + p["c11"])   # glucagon stimulates (+)
    H1 = _sig_minus(p["b12"], dl + p["c12"])  # liver insulin suppresses (-)
    M1 = _sig_minus(p["b13"], dg + p["c13"])  # glucose suppresses (-)
    F1 = p["a11"] * G1 * H1 * M1

    # --- F2: hepatic glucose uptake. Diabetic mode replaces F2 (and H2) by a
    #     constant (Table 12.3, F2_const = 0.037). ---
    H2 = _sig_minus(p["b21"], dl + p["c21"])  # liver insulin (published form)
    M2 = p["a221"] + p["a222"] * _sig_plus(p["b22"], dg + p["c22"])
    if mode == "diabetic":
        F2 = p["F2_const"]
    else:
        F2 = H2 * M2

    NHGB = F1 - F2

    # --- F3: renal excretion. M31 uses RAW gbar with b31, c31 (renal
    #     threshold ~180 mg/100 ml). See module docstring transcription flag. ---
    M31 = _sig_plus(p["b31"], gbar + p["c31"])
    M32 = p["a321"] * gbar + p["a322"]
    F3 = M31 * M32

    # --- F4: peripheral (muscle + adipose) use. Diabetic & obese freeze H4. ---
    if mode in ("diabetic", "obese"):
        H4 = p["H4_const"]
    else:
        H4 = _sig_plus(p["b41"], di + p["c41"])  # interstitial insulin drives (+)
    M4 = _sig_plus(p["b42"], dg + p["c42"])      # glucose drives (+)
    F4 = p["a41"] * H4 * M4

    # --- F5: CNS + RBC uptake (insulin-independent) ---
    M51 = p["a51"] * np.tanh(p["b51"] * (dg + p["c51"]))
    M52 = p["a52"] * dg + p["b52"]
    F5 = M51 + M52

    # --- F7: glucagon secretion (suppressed by insulin and glucose) ---
    H7 = _sig_minus(p["b71"], di + p["c71"])
    M7 = _sig_minus(p["b72"], dg + p["c72"])
    F7 = p["a71"] * H7 * M7

    # --- Insulin source terms ---
    W = 0.5 * p["aw"] * (1.0 + np.tanh(p["bw"] * (dg + p["cw"])))
    F6 = 0.5 * p["a6"] * (1.0 + np.tanh(p["b6"] * (dg + p["c6"]))) * r

    return Fluxes(
        NHGB=NHGB, F1=F1, F2=F2, F3=F3, F4=F4, F5=F5, F6=F6, F7=F7,
        G1=G1, H1=H1, M1=M1, H2=H2, M2=M2, M31=M31, M32=M32,
        H4=H4, M4=M4, M51=M51, M52=M52, H7=H7, M7=M7, W=W,
    )


# ===========================================================================
# Right-hand side (Eqs 12.1-12.7)
# ===========================================================================
ZERO_FORCING = lambda t: 0.0  # noqa: E731


def dydt(
    t: float,
    y: np.ndarray,
    patient: Patient,
    Ig: Callable[[float], float] = ZERO_FORCING,
    Ip: Callable[[float], float] = ZERO_FORCING,
) -> np.ndarray:
    """RHS of the Cobelli ODE system.

    Parameters
    ----------
    t : float        time (min)
    y : ndarray(7)   state amounts in fixed order [g, c, i, l, p, r, s]
    patient : Patient    immutable patient spec (params, volumes, basal, mode)
    Ig : callable    glucose ingestion rate Ig(t)  (mg/min); default 0
    Ip : callable    insulin ingestion rate Ip(t)  (uU/min); default 0

    Returns
    -------
    ndarray(7) : time derivatives in the same fixed order.
    """
    p = patient.params
    f = compute_fluxes(y, p, patient.basal_conc, patient.volumes, patient.mode)

    g, c, i, l, pl, r, s = y  # unpack (pl = plasma insulin to avoid name clash)

    ig = Ig(t)
    ip = Ip(t)

    # Uniform glucose-turnover scale (see GLUCOSE_FLUX_SCALE note). Applied to
    # the four endogenous glucose fluxes only; the exogenous input Ig is added
    # afterwards in true mg/min. Scaling all four equally preserves the basal
    # steady state and only sets the clearance timescale.
    S = p.get("glucose_flux_scale", 1.0)

    dg = S * (f.NHGB - f.F3 - f.F4 - f.F5) + ig                    # (12.1)
    dc = -p["h02"] * c + f.F7                                       # (12.2)
    di = -p["m13"] * i + p["m31"] * pl                             # (12.3)
    dl = -(p["m02"] + p["m12"]) * l + p["m21"] * pl + f.F6         # (12.4)
    dp = -(p["m01"] + p["m21"] + p["m31"]) * pl + p["m12"] * l \
        + p["m13"] * i + ip                                        # (12.5)
    dr = p["k21"] * s - p["k12"] * r - f.F6                        # (12.6)
    ds = -p["k21"] * s + p["k12"] * r + f.W                        # (12.7)

    return np.array([dg, dc, di, dl, dp, dr, ds], dtype=float)


# ===========================================================================
# Forcing-function builders (injectable callables)
# ===========================================================================
def make_rectangular_pulse(
    total_dose: float, t_start: float, duration: float
) -> Callable[[float], float]:
    """Rectangular input: total_dose delivered uniformly over [t_start, t_start+duration].

    Returns a callable rate(t) = total_dose/duration inside the window, else 0.
    Units of total_dose set the rate units (mg for glucose -> mg/min;
    uU for insulin -> uU/min).
    """
    rate = total_dose / duration
    t_end = t_start + duration

    def forcing(t: float) -> float:
        return rate if (t_start <= t < t_end) else 0.0

    return forcing


def make_pulse_train(
    dose_per_pulse: float,
    duration: float,
    interval: float,
    n_pulses: int,
    t_start: float = 0.0,
) -> Callable[[float], float]:
    """Sum of n equally-spaced rectangular pulses (for Fig 12.5 protocols)."""
    rate = dose_per_pulse / duration
    starts = [t_start + k * interval for k in range(n_pulses)]

    def forcing(t: float) -> float:
        total = 0.0
        for st in starts:
            if st <= t < st + duration:
                total += rate
        return total

    return forcing


# ===========================================================================
# Simulation wrapper
# ===========================================================================
@dataclass(frozen=True)
class SimResult:
    """Time series of states, concentrations, and auxiliary fluxes."""

    t: np.ndarray              # (n,)        time points (min)
    y: np.ndarray              # (7, n)      state amounts
    concentrations: Dict[str, np.ndarray]  # gbar, cbar, ibar, lbar, pbar
    fluxes: Dict[str, np.ndarray]          # NHGB, F1..F7, gates
    success: bool
    message: str
    t_events: Optional[list] = None
    y_events: Optional[list] = None


def simulate(
    patient: Patient,
    y0: np.ndarray,
    t_span: tuple,
    Ig: Callable[[float], float] = ZERO_FORCING,
    Ip: Callable[[float], float] = ZERO_FORCING,
    t_eval: Optional[np.ndarray] = None,
    method: str = "LSODA",
    rtol: float = 1e-6,
    atol: Optional[np.ndarray] = None,
    max_step: Optional[float] = None,
    events=None,
    pulse_times: Optional[list] = None,
) -> SimResult:
    """Integrate the model with solve_ivp and return states + key fluxes.

    Parameters
    ----------
    patient : Patient
    y0 : ndarray(7)   initial state amounts (fixed order)
    t_span : (t0, tf) in minutes
    Ig, Ip : forcing callables (default 0)
    t_eval : optional array of output times
    method : 'LSODA' (default; auto-stiffness) or 'Radau' (fully implicit)
    rtol, atol : tolerances. If atol is None a per-state vector is built from
        the basal amount scales so the orders-of-magnitude spread (g large,
        insulin small, glucagon small) is handled correctly.
    max_step : cap on step size. If pulse_times given and max_step is None, it
        is set small enough to resolve the forcing windows so the solver does
        not step over a pulse.
    events : optional solve_ivp events (e.g. death-at-gbar<20 for exercise 5).
    pulse_times : optional list of times the solver must not step over; used to
        set a default max_step.

    Returns
    -------
    SimResult
    """
    if y0.shape != (N_STATES,):
        raise ValueError(f"y0 must have shape ({N_STATES},), got {y0.shape}")

    vols = patient.volumes

    # Per-state absolute tolerance from basal scales (avoids one scalar atol
    # being wrong for both mg-scale glucose and uU-scale insulin pools).
    if atol is None:
        ba = patient.basal_amounts.to_array()
        scale = np.maximum(np.abs(ba), 1.0)
        atol = 1e-8 * scale

    # Resolve forcing pulses: keep solver from stepping over short windows.
    if max_step is None and pulse_times:
        gaps = [abs(b - a) for a, b in zip(pulse_times[:-1], pulse_times[1:])]
        gaps = [g for g in gaps if g > 0]
        if gaps:
            max_step = min(gaps) / 4.0

    kwargs = dict(
        fun=lambda t, y: dydt(t, y, patient, Ig=Ig, Ip=Ip),
        t_span=t_span,
        y0=np.asarray(y0, dtype=float),
        method=method,
        rtol=rtol,
        atol=atol,
        dense_output=False,
    )
    if t_eval is not None:
        kwargs["t_eval"] = t_eval
    if max_step is not None:
        kwargs["max_step"] = max_step
    if events is not None:
        kwargs["events"] = events

    sol = solve_ivp(**kwargs)

    # Build concentration and flux time series from the solution.
    conc = {"gbar": [], "cbar": [], "ibar": [], "lbar": [], "pbar": []}
    flux_keys = [
        "NHGB", "F1", "F2", "F3", "F4", "F5", "F6", "F7",
        "G1", "H1", "M1", "H2", "M2", "M31", "M32",
        "H4", "M4", "M51", "M52", "H7", "M7", "W",
    ]
    flux = {k: [] for k in flux_keys}

    for j in range(sol.y.shape[1]):
        yj = sol.y[:, j]
        cj = amounts_to_concentrations(yj, vols)
        conc["gbar"].append(cj.gbar)
        conc["cbar"].append(cj.cbar)
        conc["ibar"].append(cj.ibar)
        conc["lbar"].append(cj.lbar)
        conc["pbar"].append(cj.pbar)
        fj = compute_fluxes(yj, patient.params, patient.basal_conc, vols, patient.mode)
        for k in flux_keys:
            flux[k].append(getattr(fj, k))

    conc = {k: np.asarray(v) for k, v in conc.items()}
    flux = {k: np.asarray(v) for k, v in flux.items()}

    # Provide scaled glucose fluxes in true mg/min for mass-balance analysis
    # (e.g. exercise 1 "where does the majority of glucose go?"). The raw
    # NHGB/F3/F4/F5 above are the unscaled gate products; *_mgmin = S * raw.
    S = patient.params.get("glucose_flux_scale", 1.0)
    for k in ("NHGB", "F1", "F2", "F3", "F4", "F5"):
        flux[k + "_mgmin"] = S * flux[k]

    return SimResult(
        t=sol.t,
        y=sol.y,
        concentrations=conc,
        fluxes=flux,
        success=sol.success,
        message=sol.message,
        t_events=getattr(sol, "t_events", None),
        y_events=getattr(sol, "y_events", None),
    )


# ===========================================================================
# Equilibrium helpers (used by verify_core.py)
# ===========================================================================
def basal_residual(patient: Patient, y0: np.ndarray) -> float:
    """Return max |dy/dt| at y0 with no forcing (steady-state residual)."""
    d = dydt(0.0, y0, patient)
    return float(np.max(np.abs(d)))


def find_equilibrium(patient: Patient, y0: np.ndarray, log_scale: bool = True):
    """Find the steady state nearest y0 using scipy.optimize.root (no forcing).

    The state magnitudes span ~8 orders, so by default the solve is done in a
    log-magnitude-scaled space (positivity-preserving) to keep the Newton step
    well-conditioned and stop it wandering to unphysical negative-glucose roots.

    Returns (y_eq, residual, success). y_eq is a fresh array; the input y0 is
    not mutated.
    """
    from scipy.optimize import root

    y0 = np.asarray(y0, dtype=float)

    if log_scale and np.all(y0 > 0):
        # Solve for u = log(y); enforces y = exp(u) > 0 automatically.
        u0 = np.log(y0)

        def f(u):
            return dydt(0.0, np.exp(u), patient)

        sol = root(f, u0, method="hybr", tol=1e-12)
        y_eq = np.exp(np.asarray(sol.x, dtype=float))
    else:
        def f(y):
            return dydt(0.0, y, patient)

        sol = root(f, y0, method="hybr", tol=1e-12)
        y_eq = np.asarray(sol.x, dtype=float)

    res = float(np.max(np.abs(dydt(0.0, y_eq, patient))))
    return y_eq, res, bool(sol.success)


def settle_to_basal(
    patient: Patient,
    y0: Optional[np.ndarray] = None,
    t_settle: float = 3000.0,
    method: str = "LSODA",
) -> np.ndarray:
    """Integrate with no forcing until the system reaches its natural steady
    state, returning the settled amount vector.

    Useful for obtaining the pathological (diabetic/obese) basal IC, whose
    steady state differs from the normal clinical reference. Pure: returns a
    fresh array; does not mutate inputs.
    """
    if y0 is None:
        y0 = patient.basal_amounts.to_array()
    res = simulate(patient, np.asarray(y0, dtype=float), (0.0, t_settle),
                   method=method, rtol=1e-9)
    return res.y[:, -1].copy()
