# Chapter 12 — Hormonal Control in Mammals
**Source:** Haefner, J. W. (2005). *Modeling Biological Systems: Principles and Applications*, 2nd ed. Springer. Book pp. 260–271 (PDF pp. 271–282).
**Extracted for:** BME5113 Term Project Part 1 (exercises 1–7 of §12.5).

> Transcription note: doubly/triply-subscripted letters (e.g. `a11`, `b12`, `m21`) are **constants** (Table 12.2). Notation follows Cobelli et al. (1982). A couple of subscripts printed in the book are ambiguous vs. Table 12.2 — flagged inline with ⚠ and to be cross-checked against the original Cobelli 1982 paper.

---

## 12.1 Hormonal Regulation
Vertebrate physiology relies on fine control of physiological states by **negative feedback**. Hormones are chemicals transported long distances via the blood that switch processes on/off at the site of hormone action. This chapter models the feedback system regulating **blood glucose**. It illustrates: (i) trade-offs balancing mechanistic realism vs mathematical simplicity & minimal data requirements; (ii) Forrester-diagram model exposition; (iii) introduction of a flexible nonlinear function (`tanh`) for biological processes; (iv) using the model to answer practical questions (effect of eating on blood sugar of diabetic & obese patients) → potential for diagnosis & treatment.

## 12.2 Glucose and Insulin Regulation
Most mammals need a continual energy supply; the CNS and rapid muscular reactions need carbohydrates. The stomach needs a storage capacity into which glucose can be sequestered after eating and resupplied between meals.

**Negative feedback loop (Fig. 12.1):**
- After a meal, carbohydrates → **glucose** crosses stomach wall → bloodstream.
- Excess plasma glucose stimulates the **islets of Langerhans** (pancreas) to produce **insulin**.
- Insulin attaches to cells (esp. muscle & liver), stimulating them to absorb glucose; inside storage cells glucose → **glycogen** (inert, starch-like).
- When blood glucose falls, the islets secrete **glucagon**, carried to glycogen-storing cells, reconverting glycogen → glucose.

**Normal values (70 kg individual):** ≈ **91.5 mg glucose / 100 ml** blood plasma; ≈ **11 μU/ml** insulin in plasma; ≈ **75 pg/ml** glucagon in plasma. (U = International Units, defined by bioassay.)

**Failure modes:**
- Insufficient insulin secretion → glucose not removed → dangerously high → cascade dropping blood pH to ≤6.8, reducing hemoglobin O₂ affinity → **Type I diabetes mellitus**.
- Sufficient insulin but too few insulin receptors on glycogen-storing cells → cells can't detect insulin → **Type II diabetes mellitus**.
- Obese individuals: high insulin production. Intense physical exertion reduces insulin secretion rate.

Glucose-insulin models are valuable for theoretical insight AND as diagnostic tools (driven by perturbations like oral/IV glucose ingestion).

## 12.3 Glucose Model of Intermediate Complexity
**Cobelli et al. (1982)** model: intermediate complexity — incorporates feedback loops missing from simpler models (better for diagnosis) yet simple enough to validate. Semi-phenomenological; tailored/scaled to a particular patient around "normal" operating conditions via the **hyperbolic tangent** `tanh` (domain ±∞, range ±1).

`tanh` usage: domain = basal (baseline) plasma concentration of state variables; range = production rate of a state variable. Symmetric about x=0; a negative departure from normal produces a negative response. Using `1 − tanh` gives a monotonically decreasing function = negative feedback.

```
tanh(x) = (e^x − e^−x)/(e^x + e^−x)
```

Three submodels (Fig. 12.2 Forrester diagram): **g** = glucose, **c** = glucagon, and the insulin submodel levels **s, r, l, p, i**.

### Table 12.1 — Variables
**State variables:**
| Var | Meaning |
|-----|---------|
| c | glucagon in plasma & interstitial fluids (nU) |
| g | glucose in plasma & extracellular fluid (mg) |
| i | interstitial fluid insulin (μU) |
| l | liver insulin (μU) |
| p | plasma insulin (μU) |
| r | releasable pancreatic insulin (μU) |
| s | stored pancreatic insulin (μU) |

**Auxiliary variables:**
| Var | Meaning |
|-----|---------|
| NHGB | Net Hepatic (liver) Glucose Balance (= F1 − F2) |
| F1 | Liver glucose production rate |
| F2 | Liver glucose uptake rate |
| F3 | Renal (kidney) glucose excretion rate |
| F4 | Peripheral system (muscles) glucose use rate |
| F5 | Non-peripheral (CNS & red blood cells) glucose uptake rate |
| F6 | Insulin secretion rate (promptly releasable) |
| F7 | Glucagon secretion rate |
| Ig, Ip | Glucose, insulin ingestion rate |
| W | Insulin synthesis rate |

### 12.3.1 Basic Equations
```
dg/dt = NHGB − F3 − F4 − F5 + Ig(t)                       (12.1)
dc/dt = −h02·c + F7                                        (12.2)
di/dt = −m13·i + m31·p                                     (12.3)
dl/dt = −(m02 + m12)·l + m21·p + F6                        (12.4)
dp/dt = −(m01 + m21 + m31)·p + m12·l + m13·i + Ip(t)       (12.5)
dr/dt = k21·s − k12·r − F6                                 (12.6)
ds/dt = −k21·s + k12·r + W                                 (12.7)
```

**Concentrations** (associated with each state variable):
```
ḡ = g/Vb ,  p̄ = p/Vp ,  l̄ = l/Vl ,  ī = i/Vi ,  c̄ = c/Vb
```
where (as fractions of body weight, divided by the relevant density):
- Vb = volume of blood & extracellular fluids = 0.2 × body weight / blood density
- Vp = volume of plasma = 0.045 × body weight / plasma density
- Vl = volume of liver = 0.03 × body weight / liver density
- Vi = volume of interstitial fluid = 0.10 × body weight / interstitial fluid density

**Standardized (deviation) concentrations:** subtract the patient's basal/normal value, e.g.
```
Δḡ = ḡ − g_basal      (and Δc̄, Δl̄, Δī, Δp̄ defined similarly)
```

### 12.3.2 Glucose Subsystem  (Eq. 12.1)
Net glucose production by liver = NHGB = liver production (F1) − liver uptake (F2).
F1 limited by 3 factors (multiplicatively, see §4.3.6 multiple limiting factors): standardized glucose, liver insulin, plasma glucagon. F2 = multiplicative combination of negative effect of liver insulin (H2) & positive effect of glucose (M2).
```
NHGB = F1 − F2
F1 = a11·G1·H1·M1
G1 = 0.5[1 + tanh(b11(Δc̄ + c11))]      # positive effect of glucagon on glucose production
H1 = 0.5[1 − tanh(b12(Δl̄ + c12))]      # negative effect of liver insulin
M1 = 0.5[1 − tanh(b13(Δḡ + c13))]      # negative effect of glucose
F2 = H2·M2
H2 = 0.5[1 − tanh(b21(Δl̄ + c21))]      # negative effect of liver insulin on glucose uptake
M2 = a221 + a222·0.5[1 + tanh(b22(Δḡ + c22))]   # positive effect of glucose on uptake
```
Other plasma-glucose losses: kidney excretion (F3), fatty/muscle tissue (F4), blood cells & nerves (F5):
```
F3 = M31·M32
M31 = 0.5[1 + tanh(b31(ḡ + c31))]      # ⚠ book prints "b13"; Table 12.2 has b31=20, c31=−180 (renal threshold ≈180 mg/100ml) → use b31,c31
M32 = a321·ḡ + a322                     # M31 = neg-feedback of glucose deviation from basal; M32 = linear flow plasma→urine
F4 = a41·H4·M4
H4 = 0.5[1 + tanh(b41(Δī + c41))]      # positive effect of interstitial insulin on adipose/muscle use
M4 = 0.5[1 + tanh(b42(Δḡ + c42))]      # positive effect of glucose
F5 = M51 + M52                          # CNS + red blood cell uptake
M51 = a51·tanh(b51(Δḡ + c51))
M52 = a52·Δḡ + b52
```
Glucose/insulin added to plasma by ingestion: `Ig(t)` = glucose ingestion, `Ip(t)` = insulin ingestion (time functions used for diagnostic tests). Focus = **IVGTT** (intravenous glucose tolerance test).

### 12.3.3 Glucagon Subsystem  (Eq. 12.2)
Glucagon production F7 depends on plasma glucose & insulin; large values of either lower glucagon production:
```
F7 = a71·H7·M7
H7 = 0.5[1 − tanh(b71(Δī + c71))]      # negative effect of interstitial insulin
M7 = 0.5[1 − tanh(b72(Δḡ + c72))]      # negative effect of glucose
```

### 12.3.4 Insulin Subsystem  (Eqs. 12.3–12.7)
Five compartments; most rate dynamics are linear, donor-controlled (params mij, kij, aij in Table 12.2). Insulin formed in pancreas → transported to liver → stimulates glucose→glycogen. Two pancreatic forms:
- **W** = nonlabile, stored form produced at rate W:
```
W = 0.5·aw[1 + tanh(bw(Δḡ + cw))]
```
- **F6** = "promptly releasable" form, secreted at rate F6:
```
F6 = 0.5·a6[1 + tanh(b6(Δḡ + c6))]·r
```

### Table 12.2 — Nominal parameters (normal patient; from Cobelli et al. 1982)
**GLUCOSE submodel:**
```
a11  = 1.51         a221 = 1.95e-3      a321 = 1.43e-5
b11  = 2.14         a222 = 5.21e-3      a322 = -1.31e-5
b12  = 7.84e-2      b21  = 1.11e-2      b31  = 20
b13  = 2.75e-2      b22  = 1.45e-2      c31  = -180
c11  = -0.85        c12  = 7            c21  = 51.3
c22  = -108.5       c13  = 20           a41  = 2.87e-2
a51  = 1.01e-3      a52  = 4.6e-6       b41  = 3.1e-2
b42  = 1.44e-2      b51  = 2.78e-3      b52  = 4.13e-4
c41  = -50.9        c42  = -20.2        c51  = 1.002†   († estimated; value missing from Cobelli et al. 1982)
```
**INSULIN submodel:**
```
k12 = 0.01          k21 = 4.34e-3       m01 = 0.125
m02 = 0.185         m12 = 0.209         m13 = 0.02
m21 = 0.268         m31 = 0.042         aw  = 0.287
a6  = 1.3           bw  = 1.51e-2       b6  = 9.23e-2
cw  = -92.3         c6  = -19.68
```
**GLUCAGON submodel:**
```
a71 = 2.35          b71 = 6.86e-3       b72 = 3.00e-2
c71 = 99.2          c72 = 40            h02 = 0.086
```

### 12.3.5 Normal Simulations
Table 12.2 = normal patient. Following IVGTT, plasma glucose & insulin return to normal in ≈ **90 minutes** (Fig. 12.4). Liver & plasma insulin rise almost immediately with the glucose pulse. **Fig. 12.5:** repeated glucose pulses at intervals shorter than clearance time → a "hump" after pulse 6 develops, greatly delaying recovery (does not simply decay exponentially).

### 12.3.6 Diabetic Simulations
Diabetic parameters in Table 12.3; functions F2 and H2 are **replaced with constants**. Basal glucose much higher, insulin much lower; recovery ≈ **twice as long** as normal (Fig. 12.6).

### 12.3.7 Obesity Simulations
Obese parameters in Table 12.3. Nearly normal glucose response but **abnormal hump in the insulin decay curve** (Fig. 12.7).

### Table 12.3 — Diabetic & obese subjects (all other params as in Table 12.2; after Cobelli et al. 1982)
```
                Diabetes            Obesity
F2   =          0.037               (—)
H4   =          0.0012              0.0012
b42  =          7e-3                7e-3
c42  =          -40.47              40.47
bw   =          4.5e-3              (—)
b6   =          5e-3                0.5
c6   =          -363.55             -3.64
cw   =          -306.25             (—)
m02  =          (—)                 0.13
```
(For diabetes, F2 and H2 are replaced by constants — F2 = 0.037 listed.)

## 12.4 Summary
This model epitomizes a broad class of successful biomedical models — success partly due to fitting some (not all) parameters to the patient, and partly to good understanding of the system. A class usable for diagnosis & prescription. MBS-CD has C simulation code under `.../0Glucose`.

---

## 12.5 Exercises  (Project Part 1 requires #1–#7)

**1.** Code the Cobelli model of glucose regulation and attempt to reproduce **Figs. 12.4a & b**. Also plot glucagon concentrations and rates of liver uptake of glucose. Discuss the results in light of the Forrester diagram. **Where does the majority of glucose go?**

**2.** Why does the **"hump"** in insulin concentration develop in **Fig. 12.5**? Why is there a similar hump for obese persons in **Fig. 12.7**?

**3.** Using the parameters for the **diabetic** subject, administer the sequence of glucose pulses described in Fig. 12.5. **Compare to a normal subject.**

**4.** Simulate the glucose infusion diagnostic test by adding glucose **not as a pulse (IVGTT) but as constant input spread over 60 minutes** (a meal). Administer **25 g to a 70-kg subject over 60 minutes.** Plot plasma glucose & insulin. How do these dynamics compare to the IVGTT? Explain in terms of model mechanisms.

**5.** **Hyperinsulinism** (Guyton 1986) — overproduction of insulin drives plasma glucose down (*hypoglycemia*). CNS depends almost exclusively on plasma glucose; low glucose (~70 mg/100ml) → erratic behavior & loss of motor control; <20–50 mg/100ml → convulsions, coma ("insulin shock"); short-term treatment = large IV glucose.
  - **(a)** Simulate hyperinsulinism by adjusting parameters in Table 12.2. First guess: increase **a6 in F6** (other adjustments may be needed). New model should **terminate the patient when plasma glucose falls below 20 mg/100 ml.**
  - **(b)** Attempt to resuscitate by administering glucose IV. **How much must you add to prevent death?**

**6.** A normal patient should recover from insulin shock. Simulate **rapid ingestion of insulin = 0.10 U/kg body weight over 2 minutes.** Observe the momentary hypoglycemia. Did your subject die? **Repeat with an obese subject.**

**7.** Simulate the glucose, insulin, and glucagon dynamics resulting from a **normal, diabetic, and obese subject consuming an average bowl of vanilla ice cream.**

*(Not required by the project but listed for completeness:)*
**8.** Review Chapter 2 and write an objective statement for the glucose model.
**9.** Design a validation study using profile analysis of the glucose model applied to obese patients (simulate patient values from Fig. 12.7 via normal draws; determine #patients from profile-analysis requirements).
**10.** How much total insulin is produced by all viewers of a typical Super Bowl game? (50 million viewers, 0.25 bags of chips per commercial & after each touchdown, etc.)
