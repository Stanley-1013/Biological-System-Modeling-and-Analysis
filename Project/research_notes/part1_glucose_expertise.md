# Part 1 Expertise Brief — Glucose–Insulin–Glucagon Regulation (Cobelli 1982 / Haefner Ch. 12)

**Project:** BME5113 Biological-System-Modeling, NTU — Term Project Part 1
**Scope:** Knowledge foundation for simulating the Cobelli et al. (1982) intermediate-complexity model and answering Haefner §12.5 exercises 1–7.
**Provenance discipline:** Established facts are cited (Author Year). Items marked **[synthesis]** are my own integration/inference, not a sourced claim. Numerical parameters come from Haefner Ch. 12 Tables 12.2/12.3 (which restate Cobelli et al. 1982); two transcription flags from the textbook notes are carried forward explicitly.

---

## 1. Physiology of glucose–insulin–glucagon regulation

**The core negative-feedback loop** (Haefner 2005, §12.2). Dietary carbohydrate is broken to glucose, which crosses the gut wall into blood. The body must hold plasma glucose within a narrow band because the CNS and red blood cells depend almost exclusively on glucose and cannot store it. Two opposing pancreatic hormones, secreted by the **islets of Langerhans**, do the regulating:

- **Insulin** (β-cells): released when plasma glucose is *high*. It binds receptors on muscle, adipose, and liver cells, driving glucose uptake and its polymerization into **glycogen** (an inert storage starch). Insulin is the only major glucose-*lowering* hormone.
- **Glucagon** (α-cells): released when plasma glucose is *low*. It signals glycogen-storing cells (chiefly liver) to break glycogen back to glucose (glycogenolysis) and to make new glucose (gluconeogenesis), raising plasma glucose.

The two hormones form a push–pull negative feedback that holds glucose near setpoint (Makroglou, Li & Kuang 2006, §1).

**Normal basal values** for a 70-kg adult (Haefner 2005, §12.2): plasma glucose ≈ **91.5 mg/100 ml**, plasma insulin ≈ **11 µU/ml**, plasma glucagon ≈ **75 pg/ml**. The commonly quoted normal *range* is 70–110 mg/dl (Makroglou et al. 2006). U = International Units defined by bioassay.

**The liver as the central glucose hub** **[synthesis]**. The liver both *produces* glucose (glycogenolysis + gluconeogenesis) and *consumes* it. Its **net hepatic glucose balance (NHGB)** can be positive (net output, fasting) or negative (net uptake, fed). In the model this is the single most important glucose flux because it is the one the hormones act on most strongly.

**The kidney as an overflow valve.** Glucose is freely filtered then almost fully reabsorbed in the proximal tubule (via SGLT2/SGLT1). Above the **renal threshold ≈ 180 mg/dl** the tubular transport maximum is exceeded and glucose spills into urine (glucosuria) (StatPearls *Physiology, Glycosuria*; Wikipedia *Glycosuria*). This threshold is exactly the `c31 = −180` constant in the model's renal flux F3 — i.e. F3 ≈ 0 until ḡ exceeds ~180.

**Failure modes** (Haefner 2005, §12.2; exercise 5):
- **Type I diabetes mellitus** — insufficient insulin secretion (β-cell failure). Glucose is not cleared, rises dangerously; severe hyperglycemia can drop blood pH ≤ 6.8 and impair hemoglobin O₂ affinity.
- **Type II diabetes mellitus** — adequate insulin but too few/ineffective insulin receptors on target cells, so cells "can't detect" the insulin (insulin resistance).
- **Obesity** — characterized by elevated insulin production (compensatory hyperinsulinemia) with near-normal glucose handling. Intense exertion lowers the insulin secretion rate.
- **Hyperinsulinism / hypoglycemia / insulin shock** (Guyton 1986, cited in Haefner exercise 5) — insulin overproduction drives glucose *too low*. CNS effects: erratic behavior and loss of motor control around ~70 mg/100 ml; convulsions, coma ("insulin shock") below ~20–50 mg/100 ml. Emergency treatment is a large IV glucose bolus.

---

## 2. The Cobelli et al. (1982) model in depth

Cobelli, Federspil, Pacini, Salvan & Scandellari (1982), *Math. Biosci.* 58:27–60, is an **intermediate-complexity, semi-phenomenological, nonlinear ODE model** of short-term whole-body glucose regulation. "Intermediate" means it keeps the feedback loops a diagnostic model needs while staying simple enough to validate (Haefner 2005, §12.3). Haefner Ch. 12 is the working specification used here; the original paper is paywalled (see ref1 note).

### 2.1 Seven state variables (Table 12.1)

| Symbol | Meaning | Units | Subsystem |
|--------|---------|-------|-----------|
| `g` | glucose in plasma + extracellular fluid | mg | glucose |
| `c` | glucagon in plasma + interstitial fluids | nU | glucagon |
| `p` | plasma insulin | µU | insulin |
| `l` | liver insulin | µU | insulin |
| `i` | interstitial-fluid insulin | µU | insulin |
| `r` | releasable (promptly secreted) pancreatic insulin | µU | insulin |
| `s` | stored (nonlabile) pancreatic insulin | µU | insulin |

**Insulin compartmental flow** **[synthesis from Eqs 12.3–12.7]**: pancreas synthesizes stored insulin `s`, which interconverts with the releasable pool `r` (rates k21/k12); `r` is secreted (F6) into the **liver pool `l`**; insulin shuttles liver↔plasma (`l`↔`p`, rates m12/m21) and plasma↔interstitial (`p`↔`i`, rates m13/m31), with degradation/clearance terms (m01 plasma, m02 liver). Only **interstitial insulin `i`** acts on peripheral tissue (F4) and glucagon suppression (F7); only **liver insulin `l`** acts on hepatic glucose fluxes (F1, F2). This compartment separation is why the model needs five insulin states rather than one.

### 2.2 Governing ODEs (Haefner Eqs 12.1–12.7)

```
dg/dt = NHGB − F3 − F4 − F5 + Ig(t)                      (12.1) glucose
dc/dt = −h02·c + F7                                       (12.2) glucagon
di/dt = −m13·i + m31·p                                    (12.3) interstitial insulin
dl/dt = −(m02 + m12)·l + m21·p + F6                       (12.4) liver insulin
dp/dt = −(m01 + m21 + m31)·p + m12·l + m13·i + Ip(t)      (12.5) plasma insulin
dr/dt =  k21·s − k12·r − F6                               (12.6) releasable insulin
ds/dt = −k21·s + k12·r + W                                (12.7) stored insulin
```

Insulin Eqs 12.3–12.7 are **linear, donor-controlled** transfers except for the nonlinear sources W (synthesis) and F6 (secretion). All nonlinearity that makes the model interesting lives in the auxiliary fluxes F1–F7.

### 2.3 Concentrations and volume scaling

States are *amounts* (mg, µU, nU); physiological responses depend on *concentrations*. Convert by dividing by tissue volumes (Haefner §12.3.1):

```
ḡ = g/Vb    p̄ = p/Vp    l̄ = l/Vl    ī = i/Vi    c̄ = c/Vb
Vb = 0.20·BW / blood_density          (blood + extracellular fluid)
Vp = 0.045·BW / plasma_density        (plasma)
Vl = 0.030·BW / liver_density         (liver)
Vi = 0.10·BW / interstitial_density   (interstitial fluid)
```

For a 70-kg subject these set the conversion between mg of glucose and mg/100 ml. **[synthesis]** Densities are ~1 g/ml; the project can take density ≈ 1 unless a more precise value is specified, but unit bookkeeping (mg vs mg/100 ml) must be consistent everywhere ḡ is used. Vb is the volume that turns the state `g` (mg) into the clinically reported ḡ (mg/100 ml), and `g_basal` follows from ḡ_basal × Vb ≈ 91.5 mg/100 ml × Vb.

### 2.4 Standardized (deviation) concentrations

Every tanh response operates on a **deviation from the patient's basal value**:

```
Δḡ = ḡ − g_basal ,  Δl̄ = l̄ − l_basal ,  Δī = ī − i_basal ,  Δp̄ = p̄ − p_basal ,  Δc̄ = c̄ − c_basal
```

This is what "scales the model around a particular patient's normal operating point" means: the model is calibrated so that at basal conditions all the Δ's are zero and the system sits at steady state. **[synthesis]** A practical consequence for implementation: the **initial condition is the basal steady state**, and you should verify dg/dt ≈ ... ≈ 0 at t=0 before injecting any glucose. If the published parameters do not give exactly zero derivatives, a short pre-equilibration run (or accepting a small basal drift) is the usual fix.

### 2.5 Auxiliary fluxes and the role of `0.5[1 ± tanh(...)]`

**Why tanh?** (Haefner 2005, §12.3). tanh has domain ±∞ and range ±1; it is a smooth, monotone, saturating sigmoid, symmetric about 0. Biological rates *saturate* (a tissue can only take up glucose so fast) and respond *monotonically* to a driver, so a sigmoid is the natural shape. Cobelli wraps it as **`0.5[1 + tanh(b(Δx + c))]`** so the factor runs smoothly from **0 to 1**:
- **`+tanh`** = a *positive/stimulatory* effect (factor → 1 as the driver rises),
- **`−tanh`** = a *negative-feedback/inhibitory* effect (factor → 0 as the driver rises).

`b` controls steepness (sensitivity), `c` shifts the half-activation point. Because the argument uses Δx (deviation from basal), a *negative* departure from normal produces a *negative* response — the symmetry is what makes it a proper bidirectional regulator. **[synthesis]** Domain = standardized concentration of a state variable; range (after the 0.5[1±·] wrapper) = a dimensionless gating fraction in [0,1] that multiplies a maximal rate constant (a-coefficients carry the units).

**Glucose subsystem (Eq 12.1):**
```
NHGB = F1 − F2                                            (net hepatic glucose balance)
F1 = a11·G1·H1·M1                                         (hepatic glucose PRODUCTION)
  G1 = 0.5[1 + tanh(b11(Δc̄ + c11))]    glucagon stimulates production (+)
  H1 = 0.5[1 − tanh(b12(Δl̄ + c12))]    liver insulin suppresses production (−)
  M1 = 0.5[1 − tanh(b13(Δḡ + c13))]    glucose suppresses production (−)
F2 = H2·M2                                                (hepatic glucose UPTAKE)
  H2 = 0.5[1 − tanh(b21(Δl̄ + c21))]    (see flag below)
  M2 = a221 + a222·0.5[1 + tanh(b22(Δḡ + c22))]   glucose drives uptake (+)
F3 = M31·M32                                              (renal excretion)
  M31 = 0.5[1 + tanh(b31(ḡ + c31))]    renal-threshold gate, c31 = −180 ⇒ on above ~180 mg/100ml
  M32 = a321·ḡ + a322                   linear plasma→urine flow
F4 = a41·H4·M4                                            (peripheral/muscle+adipose use)
  H4 = 0.5[1 + tanh(b41(Δī + c41))]    interstitial insulin drives use (+)
  M4 = 0.5[1 + tanh(b42(Δḡ + c42))]    glucose drives use (+)
F5 = M51 + M52                                            (CNS + RBC uptake, insulin-independent)
  M51 = a51·tanh(b51(Δḡ + c51))
  M52 = a52·Δḡ + b52
```
F1's three factors multiply (Haefner §4.3.6 "multiple limiting factors"): production is throttled if glucagon is low *or* insulin high *or* glucose high. **[synthesis]** Note `H2` uses `−tanh` of liver insulin even though it gates *uptake*; this is the published form. Don't "fix" the sign — it is the calibrated shape, and in the diabetic case H2 and F2 are replaced by constants anyway (§2.7).

**⚠ TRANSCRIPTION FLAG 1 (F3):** The book prints `M31 = 0.5[1 + tanh(b13(...))]`, but Table 12.2 lists `b31 = 20`, `c31 = −180`. The renal-threshold reading (turn on near ḡ = 180) only works with **b31, c31**. **Use b31 = 20, c31 = −180.** (Carried from textbook_notes; consistent with renal threshold ≈ 180 mg/dl, StatPearls.) Note M31 here uses *raw* ḡ (not Δḡ), so the threshold is absolute at 180 mg/100 ml.

**⚠ TRANSCRIPTION FLAG 2 (ageing term):** The textbook notes record that an "ageing-term" subscript issue belongs to **Ch. 15, not Ch. 12** — it does **not** affect this model. No action for Part 1.

**Glucagon subsystem (Eq 12.2):**
```
F7 = a71·H7·M7                                            (glucagon secretion)
  H7 = 0.5[1 − tanh(b71(Δī + c71))]    insulin suppresses glucagon (−)
  M7 = 0.5[1 − tanh(b72(Δḡ + c72))]    glucose suppresses glucagon (−)
```
Glucagon is driven *down* by high insulin and high glucose — so after a glucose load, glucagon should dip (a checkable qualitative result for exercise 1).

**Insulin source terms (Eqs 12.6–12.7):**
```
W  = 0.5·aw[1 + tanh(bw(Δḡ + cw))]                        (synthesis of stored insulin)
F6 = 0.5·a6[1 + tanh(b6(Δḡ + c6))]·r                      (secretion of releasable insulin)
```
Both are driven up by glucose; F6 is additionally *proportional to the releasable pool r* (you cannot secrete what you do not have) — this `·r` coupling is the mechanistic seed of the Fig 12.5 "hump" (§4).

### 2.6 Forcing functions: Ig(t), Ip(t)

`Ig(t)` = exogenous glucose input rate into plasma (mg/min); `Ip(t)` = exogenous insulin input rate (µU/min). These are how diagnostic tests enter the model. The canonical test is the **IVGTT**: a rapid IV glucose bolus. The secondary source used 0.33 g/kg over 3 min; the standard clinical IVGTT bolus is **0.3–0.33 g/kg given over 1–3 min** (PubMed/ScienceDirect IVGTT overviews; ref1). The project exercises specify their own doses (25 g over 60 min for the meal; 0.10 U/kg over 2 min for the insulin bolus).

### 2.7 Encoding diabetic / obese subjects (Table 12.3)

All parameters stay at Table 12.2 *except* those listed in Table 12.3. Pathology is encoded as **parameter changes**, the model structure is unchanged — except that for **diabetes the insulin-sensitive fluxes F2 and H2 are replaced by constants** (the liver stops responding to insulin):

```
                 Diabetes            Obesity
F2   =           0.037               (unchanged, still F2 = H2·M2)
H4   =           0.0012              0.0012
b42  =           7e-3                7e-3
c42  =           −40.47             +40.47        (sign differs!)
bw   =           4.5e-3              (unchanged)
b6   =           5e-3                0.5           (obese: much steeper secretion)
c6   =           −363.55            −3.64
cw   =           −306.25            (unchanged)
m02  =           (unchanged)         0.13          (obese: altered liver insulin clearance)
```
**Diabetes** (Haefner §12.3.6): F2 and H4 frozen to constants (no insulin-driven hepatic or peripheral uptake), reduced insulin synthesis/secretion (bw, cw, b6, c6 shifted), basal glucose much higher, basal insulin much lower; recovery ≈ **twice as long** as normal. **Obesity** (§12.3.7): note H4 is also reduced and b6 is greatly *increased* (0.5 vs nominal 9.23e-2) — secretion becomes hypersensitive; glucose response is near-normal but the insulin *decay* curve shows an abnormal hump. **[synthesis]** Watch the `c42` sign flip (−40.47 diabetic vs +40.47 obese) — a common transcription error; both are taken verbatim from the notes.

---

## 3. Literature lineage: where Cobelli 1982 sits

Three landmark models, three different jobs (Makroglou et al. 2006; Bergman 1979; Dalla Man et al. 2007):

| Model | Type | Forcing | Purpose | States/scope |
|-------|------|---------|---------|--------------|
| **Bergman "minimal model"** (Bergman, Ider, Bowden & Cobelli 1979) | Minimal, 3 ODEs | IVGTT (IV bolus) | *Parameter estimation*: extract glucose effectiveness **S_G** and insulin sensitivity **S_I** from one test (S_I = p3/p2) | Plasma glucose, plasma insulin, "remote" insulin action X |
| **Cobelli intermediate model** (Cobelli et al. 1982) | Intermediate, 7 ODEs, nonlinear tanh | IVGTT primarily; any Ig(t)/Ip(t) | *Mechanistic simulation + diagnosis*: glucose, insulin (5 pools), glucagon, hepatic/renal/peripheral fluxes | whole-body, normal/diabetic/obese |
| **Dalla Man "meal model"** (Dalla Man, Rizza & Cobelli 2007) | Maximal, ~12 ODEs + 18 algebraic, ~35 params | Oral **meal** (GI/gastric-emptying submodel → glucose rate of appearance Ra) | *Realistic postprandial simulation* (sensor/pump/decision-support testing); basis of the FDA-accepted UVA/Padova simulator | GI tract + 2-cmpt glucose + 2-cmpt insulin |

**Key contrast for the report** **[synthesis]**: The Bergman minimal model is *parsimonious but "structurally improper"* in a strict sense (De Gaetano & Arino, via Makroglou et al. 2006) — it is a data-fitting tool, not a simulator. Cobelli 1982 is the *mechanistic middle ground* this project uses. Dalla Man 2007 is the modern *maximal* model and is the canonical justification for representing a **meal as a distributed, time-varying Ra** (gastric emptying + intestinal absorption) rather than an IV impulse — directly relevant to exercises 4 and 7. **IVGTT = instantaneous IV bolus** (bypasses the gut); **oral/meal = gradual, delayed Ra** (gut shapes the input).

---

## 4. Expected qualitative dynamics (what "correct" output looks like)

1. **Normal IVGTT (Fig 12.4):** glucose spikes with the bolus then returns to basal in ≈ **90 min** (Haefner §12.3.5). Liver and plasma insulin rise *almost immediately* with the glucose pulse (fast secretion of the releasable pool). Glucagon should *dip* (suppressed by glucose+insulin), and hepatic glucose uptake (F2) should rise. Expected answer to exercise 1's "where does the majority of glucose go?": **[synthesis]** under normal insulin action the dominant sinks are insulin-driven hepatic uptake (F2) and peripheral/muscle use (F4); F5 (CNS+RBC) is large but relatively constant, and F3 (renal) is ~0 unless ḡ > 180. Verify numerically by integrating each flux.

2. **The "hump" from repeated pulses (Fig 12.5):** glucose pulses spaced *shorter than the clearance time* cause a hump in insulin to develop after ~the 6th pulse, greatly delaying recovery — insulin does *not* simply decay exponentially (Haefner §12.3.5). **Mechanism [synthesis]:** F6 = (...)·r couples secretion to the releasable pool r, and r is refilled from the stored pool s on its own slow timescale (k21/k12). Repeated stimulation depletes then over-refills the pools, and the multi-compartment l→p→i lag stacks contributions, so secretion overshoots and accumulates rather than tracking glucose instantaneously. This pool-depletion/refill dynamic is the heart of exercise 2.

3. **Diabetic IVGTT (Fig 12.6):** much higher basal glucose, much lower peak insulin, recovery ≈ **2× normal** (§12.3.6) — because F2/H4 are frozen (no insulin-driven uptake) and secretion is blunted.

4. **Obese insulin-decay hump (Fig 12.7):** glucose response near-normal but insulin decay shows an abnormal hump (§12.3.7). **Mechanism [synthesis]:** the greatly steepened secretion sensitivity (b6 = 0.5) plus altered liver insulin clearance (m02 = 0.13) make the insulin pools overshoot and clear sluggishly — same pool dynamics as #2 but driven by parameter changes rather than by repeated input (this is exactly what exercise 2 asks to connect).

---

## 5. Numerical / implementation guidance

**Language/solver [synthesis].** Python + `scipy.integrate.solve_ivp` is the natural choice. The system mixes fast insulin secretion/transfer (sub-minute) with slow pool refilling and ~90-min glucose recovery, so it is **moderately stiff**. SciPy's own guidance: try `RK45` first; if it needs unusually many steps or fails, the problem is stiff → use **`Radau`** or **`BDF`**; **`LSODA`** auto-detects stiffness and switches, making it a good universal first choice (SciPy `solve_ivp` docs; Mishev et al. biokinetic-solver comparison 2023). **Recommendation: start with `LSODA` (or `Radau`)**, set `rtol≈1e-6, atol` per-state (see scales), and use `max_step` small enough to resolve the forcing pulses.

**State-variable scales [synthesis]** (critical for `atol` and for catching bugs): `g` is large (basal ḡ≈91.5 mg/100ml × Vb), insulin pools `p,l,i,r,s` are µU (small), glucagon `c` is nU. Because magnitudes span orders, prefer a **vector `atol`** scaled per state rather than one scalar, or non-dimensionalize. Always integrate the *amounts* (g, p, …) and compute concentrations (ḡ, p̄, …) inside the RHS.

**Implementing the forcings:**
- **IVGTT pulse (exercises 1–3):** approximate the bolus as a short rectangular Ig(t) = dose/Δt for t∈[t0, t0+Δt] (e.g. Δt = 1–3 min), zero otherwise. **[synthesis]** Use a smooth gate or set `max_step ≤ Δt/4` and add pulse start/stop times to solve_ivp's `t_eval`/`first_step` so the solver does not step over the pulse. For repeated pulses (Fig 12.5) sum several such rectangles at the prescribed spacing.
- **60-min meal infusion (exercise 4):** Ig(t) = (25 g = 25000 mg)/(60 min) ≈ 417 mg/min, constant for t∈[0,60], else 0. A meal is biologically a *gradual* Ra (Dalla Man et al. 2007), so even a flat 60-min infusion already produces a much lower, broader glucose peak than the IVGTT impulse — that contrast is the answer to exercise 4. (Optionally shape Ra as a rise-peak-decay for realism, citing Dalla Man.)
- **Insulin bolus (exercise 6):** Ip(t) = (0.10 U/kg × 70 kg = 7 U = 7×10⁶ µU)/(2 min) for t∈[0,2], else 0 — watch the U→µU conversion (1 U = 10⁶ µU).
- **Hyperinsulinism (exercise 5):** increase `a6` in F6 (first guess per exercise); may also need to raise synthesis/secretion sensitivity.

**Unit consistency [synthesis].** Keep a single unit convention: glucose amounts in **mg**, concentration ḡ in **mg/100 ml**; insulin amounts in **µU**, concentrations in µU/ml; glucagon in nU. Conversions that bite: g (grams) → mg (×1000) for doses; U → µU (×10⁶) for insulin; mg/100 ml vs mg/dl are identical (100 ml = 1 dl). The renal gate uses **raw ḡ in mg/100 ml** with c31 = −180.

**Patient death / event detection (exercise 5).** "Terminate the patient when plasma glucose < 20 mg/100 ml" is a textbook use of `solve_ivp`'s **`events`**: define `event(t, y) = ḡ(y) − 20`, set `event.terminal = True` and `event.direction = -1`; integration stops at the crossing and `sol.t_events`/`sol.y_events` give the death time. For exercise 6 the same event tests whether a normal vs obese subject survives the transient hypoglycemia from the insulin bolus.

**Validation checks before trusting results [synthesis]:** (1) at basal IC with no forcing, all derivatives ≈ 0 (steady state); (2) total glucose mass balance — integral of Ig should roughly equal the integrated sinks plus storage change; (3) normal IVGTT returns to basal in ~90 min (matches Fig 12.4); reproduce that before attempting diabetic/obese/shock cases.

---

## 6. Strategy outline for exercises 1–7

Each entry: *what to simulate → what to produce → key check.*

- **Ex 1 — Normal IVGTT, reproduce Fig 12.4a/b.** Simulate normal subject (Table 12.2) with a single IVGTT pulse. Plot plasma glucose ḡ and insulin p̄ vs time (Fig 12.4a/b); additionally plot **glucagon c̄** and **hepatic glucose uptake F2**. Compute time-integrals of F2, F3, F4, F5 to answer *"where does most glucose go?"* Discuss against the Forrester diagram. *Check:* ~90-min recovery; glucagon dips; insulin rises immediately.

- **Ex 2 — Explain the insulin "hump" (Figs 12.5 & 12.7).** No new figure required; this is analysis. Reproduce Fig 12.5 (repeated pulses, normal) and Fig 12.7 (obese), then explain both humps via the **F6 ∝ r pool-depletion/refill** mechanism and multi-compartment lag (§4). State why repeated forcing (12.5) and the obese parameter set (b6, m02) (12.7) produce the *same* qualitative overshoot.

- **Ex 3 — Diabetic vs normal under the Fig 12.5 pulse train.** Run the identical repeated-pulse protocol for diabetic (Table 12.3: F2/H2→const, etc.) and normal subjects on the same axes. Plot ḡ and p̄ for both. *Check:* diabetic has higher basal, blunted/abnormal insulin, much slower clearance; quantify recovery-time ratio (~2×).

- **Ex 4 — Meal vs IVGTT (60-min infusion).** Normal subject; Ig = 25 g over 60 min (≈417 mg/min flat, or a shaped Ra). Plot ḡ and p̄; overlay the IVGTT result for the same total dose. *Check/explain:* the meal gives a lower, broader, delayed glucose peak and a gentler insulin response (distributed input vs impulse) — cite Dalla Man et al. 2007 for the physiological rationale.

- **Ex 5 — Hyperinsulinism → insulin shock, with rescue.** (a) Increase `a6` (and tune as needed) to drive chronic hypoglycemia; add a **terminal event at ḡ < 20** mg/100 ml; show the patient "dies" (integration stops). (b) Add IV glucose Ig(t) to rescue; *bisect/scan the glucose dose* to find the minimum amount that keeps ḡ ≥ 20 for all t. Report that threshold dose and a plot of ḡ with vs without rescue.

- **Ex 6 — Insulin-shock survival, normal vs obese.** Simulate Ip = 0.10 U/kg over 2 min (7×10⁶ µU over 2 min) for a normal subject; plot the transient hypoglycemia and confirm survival (event not triggered). Repeat for the obese subject (Table 12.3). *Check:* does either cross the ḡ<20 death threshold? Discuss why the obese insulin handling changes the nadir.

- **Ex 7 — Bowl of vanilla ice cream, three subjects.** Model the dessert as an oral meal: convert a standard vanilla ice-cream serving's carbohydrate to grams of glucose (state your assumption, e.g. ~½ cup ≈ 15–17 g carbohydrate **[synthesis — cite a nutrition source in the report]**), deliver as a ~60-min Ra (as in Ex 4). Run normal, diabetic, and obese (Tables 12.2/12.3); plot ḡ, p̄, c̄ for all three on shared axes. *Check:* normal recovers smoothly; diabetic shows sustained hyperglycemia; obese shows near-normal glucose but the insulin hump.

---

## Sources

- Haefner, J. W. (2005). *Modeling Biological Systems: Principles and Applications*, 2nd ed. Springer. Ch. 12 (pp. 260–271). [Primary working specification; Tables 12.1/12.2/12.3, Eqs 12.1–12.7, §12.5 exercises.]
- Cobelli, C., Federspil, G., Pacini, G., Salvan, A., & Scandellari, C. (1982). "An integrated mathematical model of the dynamics of blood glucose and its hormonal control." *Mathematical Biosciences* 58(1): 27–60. DOI:10.1016/0025-5564(82)90050-5. [Origin model; paywalled — used via Haefner Ch. 12 + secondary re-implementation; see ref1.]
- Makroglou, A., Li, J., & Kuang, Y. (2006). "Mathematical models and software tools for the glucose-insulin regulatory system and diabetes: an overview." *Applied Numerical Mathematics* 56(3–4): 559–573. DOI:10.1016/j.apnum.2005.04.023. [Lineage/taxonomy; Bergman minimal model; physiology; software.]
- Bergman, R. N., Ider, Y. Z., Bowden, C. R., & Cobelli, C. (1979). Minimal model of glucose regulation (IVGTT; S_G, S_I). Via Makroglou et al. 2006 and: *Origins and History of the Minimal Model of Glucose Regulation*, Frontiers in Endocrinology / PMC7917251. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7917251/
- Dalla Man, C., Rizza, R. A., & Cobelli, C. (2007). "Meal Simulation Model of the Glucose-Insulin System." *IEEE Trans. Biomed. Eng.* 54(10): 1740–1749. DOI:10.1109/TBME.2007.893506. PMID:17926672. [Meal/Ra forcing rationale; see ref3; BioModels BIOMD0000000379.]
- Guyton, A. C. (1986). *Textbook of Medical Physiology* — hyperinsulinism, hypoglycemia, insulin shock (cited in Haefner exercise 5).
- Renal glucose threshold ≈ 180 mg/dl: *Physiology, Glycosuria*, StatPearls/NCBI (NBK557441) https://www.ncbi.nlm.nih.gov/books/NBK557441/ ; *Glycosuria*, Wikipedia https://en.wikipedia.org/wiki/Glycosuria
- IVGTT protocol (0.3–0.33 g/kg over 1–3 min; ~glucose t½ ~15 min): *Intravenous Glucose Tolerance Test — an overview*, ScienceDirect Topics https://www.sciencedirect.com/topics/nursing-and-health-professions/intravenous-glucose-tolerance-test ; PMC3182338 (plasma-volume study) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3182338/
- Numerical integration of stiff biological ODEs: SciPy `solve_ivp` documentation (Radau/BDF/LSODA) https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html ; Mishev et al. (2023) "Mathematical solutions in internal dose assessment: a comparison of Python-based differential equation solvers in biokinetic modeling," PMC10613827 https://pmc.ncbi.nlm.nih.gov/articles/PMC10613827/

*Provenance: equations and parameters are from Haefner Ch. 12 (restating Cobelli et al. 1982). Web research confirmed the renal threshold (~180 mg/dl), IVGTT dosing, the Bergman/Cobelli/Dalla-Man lineage, and stiff-ODE solver guidance. Items tagged **[synthesis]** are my integration/inference, not direct quotations. No equations or numerical values were fabricated; the two transcription flags from the textbook notes are preserved.*
