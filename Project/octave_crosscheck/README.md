# Octave cross-check scripts (independent re-implementations)

These two GNU Octave (`.m`) scripts **independently reproduce** the key results of
the two Python models in this term project, so the results can be cross-validated
in a second, unrelated toolchain. The textbook's MBS-CD ships Octave/Matlab code,
so Octave is a natural second implementation.

| Script | Mirrors | Reproduces |
|---|---|---|
| `cobelli_ivgtt.m` | `Project/part1_glucose/cobelli.py` | Normal IVGTT (Part 1) |
| `sic_baseline_vaccine.m` | `Project/part2_hiv/sic.py` | sIC HIV baseline + vaccine (Part 2) |

Each script is **self-contained** (all parameters, the calibration, the initial
conditions, and the ODE right-hand side are defined inline). They do **not** load
or call any Python code — they are an independent transcription of the same
equations, parameters, and units, written to match the verified Python models.

> **Note on validation.** The user requested a Python + Octave cross-validation.
> Octave was **not installed** in the development environment, so these scripts
> could not be executed there. They were authored to match the Python models
> exactly: each ODE right-hand side was re-transcribed and checked numerically
> against the Python core (an independent SciPy re-run of the transcribed RHS
> reproduced every headline number below to the printed precision). They are
> provided for the user to execute in their own Octave install.

---

## How to run

Octave with its built-in `lsode` integrator is all that is needed (no extra
packages). From this directory:

```bash
octave cobelli_ivgtt.m
octave sic_baseline_vaccine.m
```

Each script prints its headline numbers to the terminal and saves a PNG plot
(`cobelli_ivgtt_octave.png`, `sic_baseline_vaccine_octave.png`). If you run an
older Octave where `lsode_options("maximum step size", ...)` is unavailable, the
solver still works; the option only protects the 1-minute IVGTT bolus window —
the prints clearly show whether the glucose peak (~253) and timing (t≈1 min) were
captured.

---

## Part 1 — `cobelli_ivgtt.m`

Calibrated Cobelli (1982) 7-ODE glucose/insulin/glucagon model (Haefner Ch. 12,
Eqs 12.1–12.7), NORMAL subject, standard IVGTT (0.33 g/kg over 1 min, 70 kg).

**Expected printout (compare against Python `ex1_ivgtt`):**

| Quantity | Octave should print | Python value |
|---|---|---|
| Plasma glucose peak | ~253 mg/100 ml at t ≈ 1 min | 253.27 @ 1.0 min |
| Recovery (≤ 5% of basal) | ~51 min | 51.4 min |
| Plasma insulin peak | ~40 uU/ml at t ≈ 4 min | 40.21 @ 4.0 min |
| Basal glucose / insulin | 91.5 mg/100 ml / 11.0 uU/ml | 91.5 / 11.0 |

The plot shows plasma glucose spiking to ~250 and recovering toward 91.5 within
~50 min, and plasma insulin rising 11 → ~40 uU/ml then decaying.

### Hard-coded Python-computed calibration values

The Python core computes three under-determined basal-balance scales **at
runtime** in `cobelli.calibrate_basal` so the published clinical basal
(91.5 / 11 / 75) is an exact steady state. Octave does not re-run that
calibration, so these values were extracted from
`cobelli.make_patient('normal')` and hard-coded (each labelled in the script):

| Symbol | Hard-coded value | Meaning |
|---|---|---|
| `aw`  | `282472.33372232807`   | insulin-synthesis scale (replaces Table 12.2 `aw=0.287`) |
| `a71` | `53200.957575179564`   | glucagon-secretion scale (replaces `a71=2.35`) |
| `b52` | `0.001469898073603483` | F5 baseline offset, dg/dt = 0 at basal (replaces `b52=4.13e-4`) |
| `glucose_flux_scale` | `1.0e5` | uniform turnover scale on the 4 glucose fluxes |

The derived basal concentrations (`lbar=31.0263…`, `ibar=10.395`) and the basal
amount IC vector (`g=12810, c=10500, i=72765, l=65155.263…, p=34650,
r=489323.39…, s=4902812.82`) are likewise extracted from the Python steady state
(basal residual `max|dy/dt| ≈ 3.6e-12`). Everything else (every `tanh` shape
parameter `b*`/`c*`, every transfer rate `mij`/`kij`) is the literal Table 12.2
value. See `Project/part1_glucose/CALIBRATION_FINDINGS.md` for the full rationale.

Other faithfully reproduced choices: the renal flux `F3` uses `b31=20`,
`c31=-180` on **raw** `gbar` (renal threshold ~180 mg/100 ml); the four glucose
fluxes (NHGB, F3, F4, F5) carry the `glucose_flux_scale` while the exogenous
bolus `Ig` is added afterward in true mg/min.

---

## Part 2 — `sic_baseline_vaccine.m`

sIC (simplified Imperial College) HIV/AIDS model (Haefner Ch. 15, Eqs 15.5a–f /
15.7a–f, FOI 15.6/15.8, Table 15.2), 15 ODEs = 12 baseline compartments +
`P_f2`, `P_m2` (vaccine-protected) + `V` (cost accumulator).

**Reproduced modeling choices (from `sic.py`):**

- `gamma = 0.1 /yr` — the documented **working value** (≈8 yr infectious period,
  R0 ≈ 2.3) that reproduces Fig 15.5. The literal Table 15.2 `gamma=1.16` is
  sub-threshold (R0 ≈ 0.24, epidemic cannot ignite) and is **not** used here.
- **Conservative ageing term** `xi*A_{.,1}` in the AIDS age-2 inflow (not the
  book's printed `xi*I_{.,1}`, which double-counts and breaks conservation).
- **Frequency-dependent FOI** with the vaccine-protected `P` **included** in the
  partner-pool denominator: `pool = S + I + P` (age-2); AIDS `A` excluded.
- **Cost accumulator** `V = ∫ nu·(S_f2 + S_m2) dt`; money cost `= $10 · V`.
- Seeded with **infectious males `I_m2 = 5`**. The textbook **literal seed
  `A_m2 = 5` cannot ignite** the epidemic because AIDS individuals are excluded
  from the force of infection — the script demonstrates this explicitly.

**Expected printout (compare against Python `q_a`/`q_b`/`verify_sic`):**

| Quantity | Octave should print | Python value |
|---|---|---|
| Baseline (nu=0) prevalence peak | ~0.41 at t ≈ 96 yr | 0.4087 @ 95.9 yr |
| Baseline equilibrium prevalence | ~0.41 (t=120 yr) | 0.4086 (≈0.4085 long-run) |
| Vaccine (nu=0.65, l=0.1) prevalence peak | ~0.001 | 0.0010 |
| Vaccine equilibrium prevalence | ~0 | 0.0 |
| Cumulative vaccinations V(120) | ~44484 | 44484.1 |
| Total cost (USD) | ~444841 | 444841.2 |
| Literal `A_m2=5`-only seed peak | ~0.0006 (cannot ignite) | 0.000625 |

The plot overlays **overall HIV prevalence** for baseline (rising to ~0.41 plateau)
versus vaccination (collapsing toward 0): vaccination at nu=0.65 with l=0.1 drives
prevalence down, confirming a genuine herd-immunity effect (the script prints
`CONFIRMED` when `prev_vaccine(end) < prev_baseline(end)`).

No Python-computed runtime calibration is hard-coded for Part 2 — all parameters
are the literal Table 15.2 values plus the documented `gamma=0.1` working value
(and the vaccination `nu`, `l`), so the Octave parameter block is a direct
transcription of `sic.Params`.

---

## What these are (and are not)

These are **independent cross-checks**, not the primary deliverable. The primary
models are the Python implementations under `Project/part1_glucose/` and
`Project/part2_hiv/`. The Octave scripts re-derive the same headline numbers from
the same equations in a separate toolchain, giving Python + Octave cross-validation
of the Part 1 IVGTT and Part 2 baseline/vaccine results.
