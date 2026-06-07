# Reference 1 — Cobelli et al. (1982): Integrated Glucose–Insulin–Glucagon Model

## Full citation

Cobelli, C., G. Federspil, G. Pacini, A. Salvan, and C. Scandellari. 1982.
"An integrated mathematical model of the dynamics of blood glucose and its
hormonal control." *Mathematical Biosciences* **58**(1): 27–60.

- DOI: `10.1016/0025-5564(82)90050-5` (verified via Semantic Scholar API and Unpaywall)
- Publication date: 1982-02-01
- Publisher: Elsevier BV
- Citation count: ~186 (Semantic Scholar, as of June 2026)
- Semantic Scholar CorpusID: 85357962; MAG: 2052381132

This is the foundational paper for the glucose–insulin "intermediate complexity"
model presented in Haefner, *Modeling Biological Systems* (Ch. 12).

## Access status

**Paywalled / closed access.** The original full text is behind the Elsevier /
ScienceDirect paywall (article page returns HTTP 403 to automated fetches).

- Unpaywall (`api.unpaywall.org`) reports `is_oa: false` with **no** open-access
  locations.
- Semantic Scholar reports `openAccessPdf.status: CLOSED`; the abstract field is
  explicitly **elided by the publisher** in the API response.
- No legitimate open-access PDF was found on ResearchGate, institutional
  repositories, or PMC/Europe PMC. (sci-hub was not used; out of scope.)

**Bottom line:** I could NOT access the original full text. The model details
below are reconstructed from a detailed, properly-attributed secondary source
(see Sources), cross-checked against Haefner Ch. 12. They are NOT transcribed
from the Cobelli 1982 original.

## Abstract

> **The verbatim abstract could not be retrieved from a free, authoritative
> source** (publisher elides it; Europe PMC has no record with abstract text).

Paraphrased gist (synthesized from publisher/indexing blurbs and citing papers —
treat as secondary, NOT verbatim): The paper presents an integrated
whole-organism model of short-term blood-glucose regulation. The model is of the
comprehensive (intermediate-complexity) type and is nonlinear, representing the
major processes of glucose, insulin, and glucagon dynamics and their
interrelationships. Validation was performed by simultaneously matching several
kinds of test inputs across a variety of normal and pathological states,
examining both plasma-accessible variables and the behavior of internal unit
processes. Practical uses in the study of carbohydrate-metabolism regulation are
outlined.

## Model summary (what's known — from secondary sources + Haefner Ch. 12)

The model couples three subsystems — **glucose, insulin, glucagon** — as a system
of 7 coupled ODEs in 7 state variables, with nonlinear physiological responses
built from hyperbolic-tangent (`tanh`) saturation functions.

### State variables (7)
| Symbol | Meaning | Units |
|--------|---------|-------|
| `g` | glucose in plasma and extracellular fluid | mg |
| `c` | glucagon in plasma and interstitial fluids | nU |
| `i` | interstitial fluid insulin | µU |
| `l` | liver insulin | µU |
| `p` | plasma insulin | µU |
| `r` | releasable pancreatic insulin | µU |
| `s` | stored pancreatic insulin | µU |

These are the s / r / l / p / i insulin compartments plus glucose `g` and
glucagon `c` referenced in the project brief.

### Auxiliary (flux) variables
- `NHGB` = net hepatic glucose balance = `F1 − F2`
- `F1` liver glucose production rate; `F2` liver glucose uptake rate
- `F3` renal (kidney) glucose excretion rate
- `F4` peripheral (muscle/adipose) glucose use rate
- `F5` non-peripheral (CNS + RBC) glucose uptake rate
- `F6` insulin secretion rate; `F7` glucagon secretion rate
- `Ig(t)`, `Ip(t)` glucose / insulin ingestion (input) rates
- `W` insulin synthesis rate

### Governing ODEs (as reproduced in the secondary source)
```
dg/dt = NHGB − F3 − F4 − F5 + Ig(t)          (glucose)
dc/dt = −h02·c + F7                            (glucagon)
di/dt = −m13·i + m31·p                         (interstitial insulin)
dl/dt = −(m02 + m12)·l + m21·p + F6            (liver insulin)
dp/dt = −(m01 + m21 + m31)·p + m12·l + m13·i + Ip(t)   (plasma insulin)
dr/dt = k21·s − k12·r − F6                     (releasable pancreatic insulin)
ds/dt = −k21·s + k12·r + W                     (stored pancreatic insulin)
```
Doubly/triply-subscripted lower-case letters (e.g. `m12`, `k21`, `h02`) are
constant transfer-rate parameters.

### Concentrations and standardization
State variables are converted to concentrations by dividing by tissue volumes
(`Vb` blood/ECF ≈ 0.2·BW/density; `Vp` plasma ≈ 0.045·BW; `Vl` liver ≈ 0.03·BW;
`Vi` interstitial ≈ 0.10·BW), then standardized against basal values:
`Δḡ = ḡ − g_basal`, `Δp̄ = p̄ − p_basal`, etc. The model is thus scaled around a
particular patient's "normal" operating point.

### Use of `tanh` nonlinearities
Each nonlinear physiological response is a saturating `tanh` of a standardized
concentration. Increasing (positive-effect) responses take the form
`0.5·[1 + tanh(b·(Δx + c))]`; decreasing (negative-feedback) responses take
`0.5·[1 − tanh(b·(Δx + c))]`. Examples reproduced in the secondary source:

- **Glucose subsystem:** `NHGB = F1 − F2`, with
  `F1 = a11·G1·H1·M1`, where `G1 = 0.5[1 + tanh(b11(Δc̄ + c11))]` (glucagon
  stimulates hepatic glucose output), `H1 = 0.5[1 − tanh(b12(Δl̄ + c12))]` and
  `M1 = 0.5[1 − tanh(b13(Δḡ + c13))]` (insulin and glucose suppress it);
  `F2 = H2·M2`. Renal `F3 = M31·M32`; peripheral `F4 = a41·H4·M4`; CNS/RBC
  `F5 = M51 + M52`.
- **Glucagon subsystem:** `F7 = a71·H7·M7`, where elevated insulin (`H7`) and
  glucose (`M7`) each suppress glucagon secretion via `0.5[1 − tanh(...)]`.
- **Insulin subsystem:** pancreatic insulin exists in a stored (nonlabile) form
  synthesized at rate `W = 0.5·aw·[1 + tanh(bw(Δḡ + cw))]` and a promptly
  releasable form secreted at `F6 = 0.5·a6·[1 + tanh(b6(Δḡ + c6))]·r`. Glucose
  thus drives both insulin synthesis and release.

### Parameter sets (normal vs. diabetic)
The secondary source tabulates a **"normal" parameter set** (Table 2:
glucose-subsystem `a/b/c` constants such as `a11 = 1.51`, `b11 = 2.14`,
`h02 = 0.086`, etc.; insulin transfer constants `m01 = 0.125`, `m02 = 0.185`,
`m12 = 0.02`, `m13 = 0.02`, `m21 = 0.268`, `m31 = 0.042`, `k12 = 0.01`,
`k21 = 4.34e-3`; glucagon constants `a71 = 2.35`, `c71 = 99.2`, etc.).

A **diabetic** parameter set (Table 3) is obtained by: replacing the
insulin-sensitive fluxes `F2` and `H4` with constants (reduced insulin
sensitivity of liver uptake and peripheral utilization), halving `b42`/`c42`,
and reducing the insulin-secretion/synthesis parameters `bw, cw, b6, c6`
(reduced insulin secretion); glucagon secretion rises (~2×) as a consequence of
the altered glucose/insulin levels. The brief also mentions an **obese** subject
set; obese/other pathological parameterizations are documented in the original
Cobelli 1982 validation but were NOT recovered from the secondary source used
here — confirm against the original full text.

### IVGTT diagnostic test
The model is exercised with the **intravenous glucose tolerance test (IVGTT)**:
a rapid IV glucose bolus (secondary source used 0.33 g glucose / kg body weight
over 3 min) delivered via `Ig(t)`. In the normal simulation, plasma glucose and
insulin return to baseline ~90 min after the pulse, with liver and plasma
insulin rising almost immediately. The diabetic case shows higher basal glucose
(~250 mg/100 mL), much lower peak insulin, and a markedly slower return to
homeostasis. (These specific numbers are from the secondary source's
re-implementation, not necessarily identical to Cobelli 1982's own figures.)

## Relevance to Part 1

This is the primary-literature origin of Haefner Ch. 12's "intermediate
complexity" glucose–insulin model. It supplies: (a) the 7-compartment state
structure (glucose `g`, glucagon `c`, insulin pools `s/r/l/p/i`); (b) the
`tanh`-based nonlinear response formalism that Haefner adopts; (c) the
normal-vs-pathological parameterization strategy (scaling around a patient's
basal operating point); and (d) the IVGTT as the canonical model-validation /
diagnostic input. Part 1 should cite Cobelli 1982 as the source model and treat
Haefner Ch. 12 + the equations above as the working specification, flagging that
exact parameter tables for normal/diabetic/obese should be confirmed against the
original where numerical fidelity matters.

## Caveats on provenance (academic honesty)

- **Verbatim original abstract: NOT obtained** (publisher-elided; no free copy).
- **Original full text: NOT accessed** (paywalled).
- All equations, variable tables, and parameter values above come from a
  **secondary re-implementation** (Lozada, NYU, advised by C. S. Peskin and
  T. Fai) that explicitly cites "Cobelli et al. 1982 and Haefner's *Modeling
  Biological Systems*." They are consistent with Haefner Ch. 12 but should be
  spot-checked against the Cobelli 1982 original before being quoted as that
  paper's exact content. The obese-subject parameter set in particular was not
  recovered and remains to be verified.

## Sources (URLs)

- Publisher (paywalled) — ScienceDirect article page:
  https://www.sciencedirect.com/science/article/abs/pii/0025556482900505
- DOI: https://doi.org/10.1016/0025-5564(82)90050-5
- Semantic Scholar API (metadata, citation count, closed-access status):
  https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/0025-5564(82)90050-5
- Unpaywall (open-access status = false):
  https://api.unpaywall.org/v2/10.1016/0025-5564(82)90050-5
- Secondary source with full model reproduction (equations, variable tables,
  normal/diabetic parameters, IVGTT) — Samantha Lozada, "Glucose Regulation in
  Diabetes," NYU (adv. C. S. Peskin, T. Fai):
  https://math.nyu.edu/degree/undergrad/ug_research/Lozada_SURE_Paper
