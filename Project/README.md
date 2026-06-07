# BME5113 Term Project — Submission Map

**Student:** 李傳漢 (Chuan-Han Li), B11611027 · **Course:** BME5113 Biological Systems Modeling and Analysis (NTU BiME) · **Due:** 2026-06-15

Two parts: **Part 1** — the Cobelli *et al.* (1982) glucose–insulin–glucagon model (Haefner Ch. 12),
exercises 1–7. **Part 2** — HIV vaccination on the simplified Imperial College ("sIC") AIDS model
(Haefner Ch. 15), the four project questions. All simulations in Python (NumPy/SciPy/Matplotlib),
with GNU Octave cross-check scripts.

## The four required submissions
| # | Required item | Where |
|---|---------------|-------|
| 1 | **Project report** (figures + tables) | [`report/main.pdf`](report/main.pdf) (LaTeX source `report/main.tex`, `part1.tex`, `part2.tex`) |
| 2 | **Simulation programs** | Part 1: [`part1_glucose/`](part1_glucose/) · Part 2: [`part2_hiv/`](part2_hiv/) · Octave cross-checks: [`octave_crosscheck/`](octave_crosscheck/) |
| 3 | **Papers read** | [`references/`](references/) (see `references/README.md`) |
| 4 | **Presentation (Part 2 talk)** | [`presentation/part2_HIV_vaccination.pptx`](presentation/part2_HIV_vaccination.pptx) |

## Additional Chinese study aids (requested)
- **簡報講稿** (speaker script for the 15-min talk): [`presentation/簡報講稿_zh.md`](presentation/簡報講稿_zh.md)
- **報告註解稿** (companion explainer for the report + anticipated Q&A): [`report/報告註解稿_zh.md`](report/報告註解稿_zh.md)

## How to run
```bash
# Part 1 (glucose): core verification + each exercise
cd part1_glucose && python3 verify_core.py && python3 ex1_ivgtt.py   # ... ex2..ex7
# Part 2 (HIV): core verification + each question
cd part2_hiv && python3 verify_sic.py && python3 q_a_peak_decline.py # ... q_b, q_c, q_d
# Report (PDF)
cd report && latexmk -lualatex main.tex
# Octave cross-checks (needs GNU Octave installed)
cd octave_crosscheck && octave cobelli_ivgtt.m && octave sic_baseline_vaccine.m
```
Each core ships a `verify_*.py` harness (basal steady state / conservation of individuals + LSODA-vs-Radau agreement).

## Notes on modeling integrity (documented in the report, not hidden)
- **Part 1:** Haefner's literal Table 12.2 does not reproduce Fig. 12.4; a small, explicitly documented
  calibration (`glucose_flux_scale`, recalibrated `aw`, `a71`, `b52`) is applied — see
  `part1_glucose/CALIBRATION_FINDINGS.md`. We do not claim these are the original Cobelli coefficients.
- **Part 2:** the literal progression rate γ=1.16/yr gives R₀<1 (no epidemic); we use the biologically
  grounded γ=0.1/yr (mean ~10 yr) → R₀≈2.35. Protected individuals are kept in the frequency-dependent
  partner pool (the correct convention) so the vaccine expresses herd immunity. Both choices are
  justified in the report.

## Textbook notes & research
- `textbook_notes/` — extracted Haefner Ch. 12 & 15 (equations, parameter tables, exercises).
- `research_notes/` — domain expertise briefs grounding each Part.
