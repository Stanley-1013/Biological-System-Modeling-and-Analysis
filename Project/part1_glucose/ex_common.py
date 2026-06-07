"""Shared helpers for Part 1 exercise scripts (ex1/ex2/ex3).

Thin convenience layer over the verified ``cobelli`` core. It adds NO model
physics -- it only wraps the public API for repeated plotting / pulse-train /
trapezoid-integration chores so each exercise script stays short and standalone.

Units (from cobelli.py): time min; glucose conc mg/100ml; insulin uU/ml;
glucagon nU/ml; glucose dose grams -> mg via *1000.
"""

from __future__ import annotations

import os
from typing import Callable, Optional

import numpy as np

import cobelli as cb

# ---------------------------------------------------------------------------
# Paths (absolute, relative to this file)
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")
RESULTS_DIR = os.path.join(HERE, "results")

# ---------------------------------------------------------------------------
# Unit constants
# ---------------------------------------------------------------------------
MG_PER_GRAM = 1000.0
DEFAULT_BOLUS_DURATION_MIN = 2.0  # IV bolus delivered over ~2 min (clinical IVGTT)


def ensure_dirs() -> None:
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)


def grams_to_mg(grams: float) -> float:
    """Convert a glucose dose in grams to mg (model amount unit)."""
    return grams * MG_PER_GRAM


def single_ivgtt_forcing(
    dose_grams: float,
    t_start: float = 0.0,
    duration: float = DEFAULT_BOLUS_DURATION_MIN,
) -> Callable[[float], float]:
    """Rectangular IV glucose bolus of ``dose_grams`` g over ``duration`` min."""
    return cb.make_rectangular_pulse(grams_to_mg(dose_grams), t_start, duration)


def variable_pulse_train_forcing(
    doses_grams,
    times_min,
    duration: float = DEFAULT_BOLUS_DURATION_MIN,
) -> Callable[[float], float]:
    """Sum of rectangular boluses with PER-PULSE doses at PER-PULSE start times.

    cobelli.make_pulse_train assumes a fixed dose/interval; the Fig 12.5 protocol
    uses an escalating dose ladder at irregular times, so we build the explicit
    superposition of rectangular pulses here (no new physics; just forcing I/O).
    """
    doses_mg = [grams_to_mg(d) for d in doses_grams]
    starts = list(times_min)
    if len(doses_mg) != len(starts):
        raise ValueError("doses_grams and times_min must have equal length")
    rates = [d / duration for d in doses_mg]

    def forcing(t: float) -> float:
        total = 0.0
        for st, rate in zip(starts, rates):
            if st <= t < st + duration:
                total += rate
        return total

    return forcing


def run(
    patient: cb.Patient,
    y0: np.ndarray,
    t_end: float,
    Ig: Callable[[float], float] = cb.ZERO_FORCING,
    Ip: Callable[[float], float] = cb.ZERO_FORCING,
    n_eval: int = 1200,
    pulse_times: Optional[list] = None,
    max_step: Optional[float] = 0.5,
    method: str = "LSODA",
) -> cb.SimResult:
    """Convenience wrapper around cb.simulate with a dense uniform output grid."""
    t_eval = np.linspace(0.0, t_end, n_eval)
    return cb.simulate(
        patient,
        np.asarray(y0, dtype=float),
        (0.0, t_end),
        Ig=Ig,
        Ip=Ip,
        t_eval=t_eval,
        method=method,
        pulse_times=pulse_times,
        max_step=max_step,
    )


def cumulative_trapz(y: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Cumulative trapezoidal integral of y over t (same length as t, starts 0)."""
    y = np.asarray(y, dtype=float)
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(y)
    dt = np.diff(t)
    incr = 0.5 * (y[1:] + y[:-1]) * dt
    out[1:] = np.cumsum(incr)
    return out


def total_integral(y: np.ndarray, t: np.ndarray) -> float:
    """Total trapezoidal integral of y over the whole t span."""
    return float(np.trapezoid(np.asarray(y, dtype=float), np.asarray(t, dtype=float)))


def setup_matplotlib():
    """Return a configured pyplot (Agg backend, consistent fonts)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 130,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "font.size": 10,
        }
    )
    return plt
