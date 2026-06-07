# Chapter 15 — Diseases
**Source:** Haefner, J. W. (2005). *Modeling Biological Systems: Principles and Applications*, 2nd ed. Springer. Book pp. 307–323 (PDF pp. 318–334).
**Extracted for:** BME5113 Term Project Part 2 (HIV vaccination on the sIC AIDS model). **The project's Part 2 is essentially textbook Exercise 15.6 #5** (with one added sub-question on optimum vaccination rate).

> Transcription note: a conservation-of-individuals inconsistency appears in the printed AIDS age-class-2 equations (15.5f / 15.7f) — flagged with ⚠ below.

---

## 15.1 Simple Models

### Constant Infection
Simplest model: diseased persons `D` increase at constant infection rate `a`, each diseased person cured with constant probability `b`:
```
dD/dt = a − bD
```
Analytic solution:
```
D(t) = (1/b)(a − e^{−bC} e^{−bt})          (15.1)
```
with constant of integration `C = −ln(a − bD(0))/b`. Single non-trivial stable equilibrium at `D* = a/b` → the disease is never lost from the population.

### 15.1.1 SIR and Derivatives
Eq. 15.1 is unrealistic (infection independent of #cases). The **SIR** family (Kermack & McKendrick 1927) has three compartments: **S**usceptible, **I**nfected, **R**emoved.
```
dS/dt = −αSI                  (15.2)
dI/dt =  αSI − βI             (15.3)
dR/dt =  βI                   (15.4)
```
- `N = S + I + R` constant (epidemic timescale ≪ birth/death timescale).
- `α` = infection rate (mass-action between S & I); `β` = "cure"/removal rate.
- R = N − (S+I) → can eliminate Eq. 15.4.
- Nullclines: `I = 0`, `S = 0`, and `I = β/α`. Single equilibrium (0,0,N).
- **Threshold:** `dI/dt > 0` when `S > β/α` (epidemic grows); `dI/dt < 0` when `S < β/α`.
- Fig. 15.2 example: 1978 English boys' boarding-school flu (14 days). Params `S(0)=762, I(0)=1, α=0.00218, β=0.4404, N=763`.

## 15.2 AIDS

### 15.2.1 Biology of HIV/AIDS
- **AIDS** = clinically defined as < **200 CD4+** white blood cells per ml of blood + positive HIV antibody test.
- HIV attacks **helper T cells (T_H, CD4+)** — pivotal for enhancing T_C and B cells. Destroying them imperils the entire immune system.
- HIV is a **retrovirus** (RNA only); uses **reverse transcriptase** to make double-stranded DNA → incorporated into host DNA → replicated during mitosis. Error-prone → high variability → hard for immune system to adapt.
- Healthy CD4+ T_H level ≈ **1200 cells/ml** of blood → degrades to **200 cells/ml** at clinical AIDS stage (over 1–10 years). Transmission: sexual, blood transfusion, shared needles (not airborne; not viable after dehydration).

### 15.2.2 Epidemiology
- Not randomly distributed: **90%** of infections in developing countries; Sub-Saharan Africa most severe (7 southern-African countries > 20%: Botswana, Namibia, South Africa, Zimbabwe ~ leveling at 45%).
- Women have higher HIV occurrence than men (primary sexual transmission mode): ages 15–40, ~20% women vs ~15% men infected.
- Uganda = model of control (reduced 30% → 10–11%); Senegal kept < 2%.

### 15.2.3 Modeling Approaches (3 classes)
1. **Statistical curve-fit** (single time-dependent eq; e.g., gamma distribution) — short horizon, ignores mechanism, can't analyze prevention strategies.
2. **Individual-based / micro-simulation** (SimulAIDS, STDSIM) — detailed mechanistic, stochastic, needs lots of data.
3. **Compartment models** (SIR-based, age/gender/sexual-behavior/stage structured) — e.g., iwgAIDS (WHO/CDC/World Bank); and the **Imperial College ("IC") model** (Garnett & Anderson 1993; Garnett et al. 2002) — described here in two steps: simplified sIC, then full IC.

---

## 15.3 Simple IC Model (sIC)  ← **basis of project Part 2**

**Simplifications:** 2 sexes (M, F) with identical sexual behavior & drug usage; a **single stage** of AIDS development from HIV. Two age classes: **Age 1** = newborns to age 15; **Age 2** = ages 16 → death. Two activity classes collapsed to one. Single mixing → `ρ = 1.0`.

**Structure (Fig. 15.4, Forrester diagram), 12 compartments:** S/I/A × {f,m} × {age1,age2}:
`S_{f,1} S_{f,2} S_{m,1} S_{m,2}` (susceptible), `I_{f,1} I_{f,2} I_{m,1} I_{m,2}` (infected/HIV+ no AIDS), `A_{f,1} A_{f,2} A_{m,1} A_{m,2}` (AIDS).

**Reproduction:** newborns created from susceptible females `S_F` (birth rate `θ`) and infected females `I_F`. Infected females have probability `1 − ϑ` of NOT transmitting HIV to fetus (so prob `ϑ` of perinatal transmission). No info flow from males to reproduction (males don't limit female reproduction). Susceptible females produce susceptible (uninfected) newborns. Proportion `η` of newborns are female.

**Ageing:** Age 1 → Age 2 at rate `ξ`. If age interval = 5 yr, time step = 1 yr, mortality = 0.4, then proportion ageing per step = (0.2)(1−0.4) = 0.12/yr. (Note Table value `ξ = 0.0667`.)

**Infection:** new HIV cases from interaction of infected & susceptible. The *per-capita force of infection* `λ` = product of (rate of having sex / sharing needles with various types) × (proportion of population that has HIV but NOT AIDS — persons with clinical AIDS assumed to not engage in sex or transmit). Little mixing → small force of infection; large mixing → more spread. Infected acquire AIDS at rate `γ` and accrue added mortality `α` on top of natural mortality `μ`.

### sIC Equations — FEMALES (15.5a–f)
```
dS_{f,1}/dt = ηθζ( S_{f,2} + (1−ϑ)I_{f,2} ) − μS_{f,1} − ξS_{f,1}        (15.5a)
              └ fertility ┘ └non-infecting births┘  └mortality┘ └ageing┘

dS_{f,2}/dt = ξS_{f,1} − (λ_{S_{f,2}} + μ) S_{f,2}                       (15.5b)
              └ageing┘  └─ infection / death ─┘

dI_{f,1}/dt = ηθζϑ I_{f,2} − (μ+ξ)I_{f,1} − γI_{f,1}                     (15.5c)
              └infected birth┘ └death&ageing┘ └to AIDS┘

dI_{f,2}/dt = λ_{S_{f,2}} S_{f,2} − (μ+γ)I_{f,2} + ξI_{f,1}              (15.5d)
              └ infection ┘        └death&AIDS┘   └ageing┘

dA_{f,1}/dt = γI_{f,1} − (μ+ξ+α)A_{f,1}                                  (15.5e)
              └to AIDS┘ └death&ageing┘

dA_{f,2}/dt = γI_{f,2} + ξA_{f,1} − (μ+α)A_{f,2}                         (15.5f) ⚠
```
**⚠ 15.5f / 15.7f flag:** the book prints the ageing term as `ξ I_{f,1}` (and `ξ I_{m,1}`). But conservation of individuals requires the ageing inflow to `A_{,2}` to be `ξ A_{,1}` (since `A_{,1}` loses `ξA_{,1}` by ageing in 15.5e, and `I_{,1}`'s ageing is already counted in 15.5d). **Use `ξ A_{f,1}` / `ξ A_{m,1}`** for a conservative model; will re-verify against Garnett & Anderson (1993) and note the discrepancy in the report.

**Force of infection — susceptible females (15.6):**
```
λ_{S_{f,2}} = c_{S_{f,2}}(t) · ρ_{S_{f,2}} · β_{m,f} · I_{m,2} / (S_{m,2} + I_{m,2})      (15.6)
```
- `c_{S_{f,2}}(t)` = current rate of choosing a new male partner by a sexually-active susceptible female.
- `ρ_{S_{f,2}}` = prob. the new male partner comes from a particular age & activity class (social mixing); in simplified 1-age/1-activity model `ρ = 1.0`.
- `β_{m,f}` = prob. an infected male transmits disease to a female.
- `I_{m,2}/(S_{m,2}+I_{m,2})` = prob. of encountering an infected individual among possible partners.

### sIC Equations — MALES (15.7a–f)
```
dS_{m,1}/dt = (1−η)θζ( S_{f,2} + (1−ϑ)I_{f,2} ) − (μ+ξ)S_{m,1}          (15.7a)
dS_{m,2}/dt = ξS_{m,1} − (λ_{S_{m,2}} + μ)S_{m,2}                        (15.7b)
dI_{m,1}/dt = (1−η)θζϑ I_{f,2} − (μ+ξ)I_{m,1} − γI_{m,1}                 (15.7c)
dI_{m,2}/dt = λ_{S_{m,2}} S_{m,2} − (μ+γ)I_{m,2} + ξI_{m,1}              (15.7d)
dA_{m,1}/dt = γI_{m,1} − (μ+ξ+α)A_{m,1}                                  (15.7e)
dA_{m,2}/dt = γI_{m,2} + ξA_{m,1} − (μ+α)A_{m,2}                         (15.7f) ⚠ (book prints ξI_{m,1})
```
Note: male births also come from female reproduction (`S_{f,2}`, `I_{f,2}`), with proportion `(1−η)` male.

**Force of infection — susceptible males (15.8):**
```
λ_{S_{m,2}} = c_{S_{m,2}}(t) · ρ_{S_{m,2}} · β_{f,m} · I_{f,2} / (S_{f,2} + I_{f,2})       (15.8)
```

### Table 15.2 — Parameters for the Simple IC AIDS model (values based on Garnett & Anderson 1993; variable values are initial conditions)
**Initial conditions (Numbers of individuals):**
```
S_{f,1} = 3000   S_{f,2} = 1000   S_{m,1} = 3000   S_{m,2} = 1000
I_{f,1} = 0      I_{f,2} = 0      I_{m,1} = 0      I_{m,2} = 0
A_{f,1} = 0      A_{f,2} = 0      A_{m,1} = 0      A_{m,2} = 5      ← seed: 5 AIDS males age-2
```
**Parameters:**
```
α      AIDS death rate                              = 1.0    /year
β_{f,m} female→male transmission probability         = 0.075
β_{m,f} male→female transmission probability         = 0.2
c_{S_{m,2}} rate of new partners at t=0              = 2.35   /year
η      proportion females of newborns               = 0.5    (unitless)
γ      transition rate infected→AIDS                = 1.16   /year
μ      natural death rate                           = 0.0227 /year¹
ρ      social mixing probabilities                  = 1.0
θ      female fecundity                             = 0.2088 /year
ϑ      probability perinatal transmission           = 0.35   (unitless)
ξ      proportion moving to age class 2             = 0.0667
ζ      proportion individuals in sexual activity class = 1.0
```
¹ μ = 0.0227/yr ≈ 1/44 yr (life expectancy ~44 yr).

### sIC Results (baseline behavior)
- Fig. 15.5a: with nominal params (developing country, high birth rate) the **population as a whole increases**; **HIV/AIDS does NOT go away** (unlike flu, which terminates in resistance).
- Auxiliary variable of interest = **proportion of population that has the virus**.
- **Condom-use / safe-sex scenario** (Fig. 15.5b): modeled by **halving the transmission betas** → `β_{f,m}: 0.075→0.0375` and `β_{m,f}: 0.2→0.1`. Effect: equilibrium prevalence drops (females 0.9→0.7, males 0.75→0.45); time-lag to exceed 10% prevalence rises from ~20 yr to ~50 yr. (Text body also loosely says "from 0.1 and 0.2 to 0.05 and 0.1" — minor inconsistency vs Table's β_{f,m}=0.075; the figure caption's halving is authoritative.)
- Fig. 15.6: increasing new partners per year `c = 1.0 → 2.0 → 3.0` dramatically increases HIV spread (monogamy reduces STD spread; even +1 partner/yr matters a lot).

## 15.4 Full IC Model
Full IC (Garnett & Anderson 1993): ~18 age classes, 3 stages of HIV infection, 4 sexual-activity classes → 133 classes. `γ` decomposed into 3 stage-dependent levels (infectiousness high initially, drops in stage 2, rises for HIV→AIDS transition). New-partner rates 1–4/yr by activity class. Largest complication = **partner mixing** (mixing matrix; assortative ↔ dissortative ↔ proportionate; rows of mixing matrix sum to 1). Validated against African data (Fig. 15.7, Uganda/Malawi/Zaire). Simplified sIC produces results similar to the full model.

## 15.5 AIDS Modeling Prognosis
Age-structured full model (Fig. 15.8): high fraction (~25%) of very young children with HIV (womb transmission); after age 15 prevalence rises sharply; ~80% of females 25–50 infected after 100 yr; drops after 50 (progression to AIDS + mortality). Concern: forecasts are strongly model-dependent. Intervention strategies addressed: condoms, clean-needle programs, vaccinations. Models help identify ineffective policies.

---

## 15.6 Exercises  (Project Part 2 = **Exercise #5**)

**1.** For Eq. 15.1: (a) derive the equation & initial-condition expression; (b) local stability analysis (§9.3.2) of the equilibrium.
**2.** Draw a Forrester diagram for the SIR model.
**3.** Show algebraically for SIR that `dI/dt < 0` if `S < β/α`, and `dI/dt > 0` if `S > β/α`.
**4.** English flu data (Day, No. Infected): (3,25)(4,75)(5,227)(6,296)(7,258)(8,236)(9,192)(10,126)(11,71)(12,28)(13,11)(14,7). Use validation techniques (Ch 8) to assess the model. (Data were used to estimate params → calibration-quality assessment, not a valid validation test.)

**★ 5. (PROJECT PART 2)** Examine the effects of a **HIV vaccination** on the sIC AIDS model (loosely based on **Garnett et al. (2002)**). Assume the vaccine is applied to **`S_{f,2}` and `S_{m,2}`** at rate **`ν = 0.65/year`** per individual. Vaccinated individuals become protected (move into variables **`P_{f,2}` and `P_{m,2}`**). Further assume a fraction of vaccinated individuals **lose protection at rate `l = 0.1/year`**. Address:
  - Will vaccination cause the epidemic to peak and, if so, when will the decline occur?
  - How much will it cost (assume one vaccination costs **$10**)?
  - **[Project-added question]** What is the **optimum vaccination rate** needed to effectively control the epidemic?
  - Which intervention strategy is better: **vaccination** or **safe-sex education + condom use**?

  MBS-CD has `sIC_AIDS` (models Eqs. 15.5 & 15.7) to help with this exercise.

**6.** Bombay 1905 plague data (Kermack & McKendrick 1927): (a) approximate data with the model using `SimSIR-Bombay.ctrl` hints; (b) accuracy via `SimValidate-Template.c`.
**7.** *Abstinence:* propose changes to sIC parameter(s) approximating abstinence, then alter to test whether promoting abstinence is a "radical behavioral modification".

---

## Design notes for Part 2 vaccination extension (to be confirmed during modeling)
Add protected compartments `P_{f,2}`, `P_{m,2}` (age-2 only, terminal age class → no ageing out):
```
dP_{f,2}/dt = ν·S_{f,2} − (l + μ)·P_{f,2}
dP_{m,2}/dt = ν·S_{m,2} − (l + μ)·P_{m,2}
```
and modify the susceptible age-2 equations:
```
dS_{f,2}/dt = ξS_{f,1} − (λ_{S_{f,2}} + μ + ν) S_{f,2} + l·P_{f,2}
dS_{m,2}/dt = ξS_{m,1} − (λ_{S_{m,2}} + μ + ν) S_{m,2} + l·P_{m,2}
```
Total vaccinations administered up to time T (for cost @ $10 each) = ∫₀ᵀ ν·(S_{f,2}(t) + S_{m,2}(t)) dt.
"Optimum vaccination rate" = sweep ν, find the value that drives the epidemic to decline / minimizes prevalence (or cost-effectiveness threshold). Compare against condom scenario (halved betas) for question (d).
