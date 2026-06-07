# Reference 3 — Dalla Man, Rizza & Cobelli (2007): Meal Simulation Model of the Glucose-Insulin System

> Academic-honesty note: Items below are tagged **[Abstract/verbatim]**, **[Full text]**,
> **[Secondary source]**, or **[Bibliographic]** to indicate provenance. The full IEEE PDF is
> paywalled and was **not** read in full for this summary; the model-structure description is
> drawn from open secondary sources by the same authors (BioModels curation and the open-access
> GIM software paper), not from the primary article's main text. No equations or numerical
> parameter values are reproduced here, to avoid fabrication.

## Full citation

Dalla Man, C., R. A. Rizza, and C. Cobelli. 2007. "Meal Simulation Model of the
Glucose-Insulin System." *IEEE Transactions on Biomedical Engineering* 54(10): 1740–1749.

- **DOI:** 10.1109/TBME.2007.893506 — **verified** [Bibliographic; PubMed, SciRP, Mayo Clinic Pure]
- **PMID:** 17926672 [Bibliographic; PubMed]
- **Author affiliation:** Department of Information Engineering, University of Padova (Padova), Italy
  (Rizza: Mayo Clinic). [Bibliographic]

Note on author-name form: PubMed/IEEE index the first author as "Chiara Dalla Man"
("Dalla Man" is the surname). The assignment lists her as "C. Dalla Man"; the widely used
citation key is often "Dalla Man et al. 2007." Both refer to the same author. [Bibliographic]

## Access status

- **Paywalled.** The primary article is behind the IEEE Xplore paywall; full text was not
  obtained for this note. [Access limitation]
- **Open / freely available related material** (availability reported only; not all read in full):
  - PubMed abstract — open. [Abstract source]
  - **BioModels** curated SBML encoding of this exact model:
    `BIOMD0000000379` ("DallaMan2007_MealModel_GlucoseInsulinSystem"). Useful for reproducing the
    equations/parameters in simulation. [Secondary source]
  - **GIM simulation software paper** (Dalla Man, Raimondo, Rizza, Cobelli, 2007,
    *J. Diabetes Sci. Technol.*) is open access on PMC (`PMC2769591`) and SAGE; it documents and
    implements the same meal model (MATLAB/Simulink). [Secondary source]
  - Semantic Scholar and ResearchGate host listing pages; ResearchGate is "Request PDF"
    (not guaranteed open). [Access listing]

## Abstract (verbatim) [Abstract/verbatim — PubMed]

"A simulation model of the glucose-insulin system in the postprandial state can be useful in
several circumstances, including testing of glucose sensors, insulin infusion algorithms and
decision support systems for diabetes. Here, we present a new simulation model in normal humans
that describes the physiological events that occur after a meal, by employing the quantitative
knowledge that has become available in recent years. Model parameters were set to fit the mean
data of a large normal subject database that underwent a triple tracer meal protocol which
provided quasi-model-independent estimates of major glucose and insulin fluxes, e.g., meal rate
of appearance, endogenous glucose production, utilization of glucose, insulin secretion. By
decomposing the system into subsystems, we have developed parametric models of each subsystem
by using a forcing function strategy. Model results are shown in describing both a single meal
and normal daily life (breakfast, lunch, dinner) in normal. The same strategy is also applied
on a smaller database for extending the model to type 2 diabetes."

## Model summary

> Source provenance: the structural description below is from the **BioModels** curation of this
> model and the open-access **GIM** software paper (same authors), **[Secondary source]**, not
> from the primary IEEE article's body. Treated as a faithful but secondary account.

**Overall structure** [Secondary source — GIM paper]
The whole-body postprandial model is built by **decomposing the system into subsystems** and
identifying each with a **forcing-function strategy** (each subsystem is fitted against measured
flux time courses obtained quasi-model-independently from a triple-tracer meal protocol). The
GIM documentation states the assembled model comprises on the order of **12 nonlinear
differential equations, 18 algebraic equations, and ~35 parameters**. (Reported from secondary
source; not independently verified against the primary PDF.)

**1. Gastro-intestinal tract / oral glucose absorption submodel** [Secondary source]
- The stomach is represented by **two compartments** (solid/undigested phase and triturated/liquid
  phase); the gut (intestine) is a **single compartment**.
- **Gastric emptying** is modeled with a **nonlinear rate constant that depends on the amount of
  glucose remaining in the stomach** (rate varies through the course of digestion rather than
  being constant).
- Output of this submodel is the **glucose rate of appearance (Ra)** in plasma — i.e., the meal
  is converted into a time-varying glucose influx into the glucose subsystem. This is the
  mechanism that represents "eating a meal" as opposed to an instantaneous intravenous bolus.

**2. Glucose subsystem** [Secondary source]
- **Two-compartment** representation: a plasma / rapidly-equilibrating-tissue compartment and a
  remote (peripheral tissue) compartment.
- **Insulin-independent glucose utilization** occurs in the first (plasma) compartment;
  **insulin-dependent utilization** occurs in the remote compartment.
- Includes **endogenous glucose production (EGP)** (hepatic, suppressed by insulin signals) and
  **renal glucose excretion** above a threshold.
- Driven by the meal Ra from the GI submodel plus EGP, with utilization and renal loss as sinks.

**3. Insulin subsystem** [Secondary source]
- **Two compartments:** the first representing the **liver**, the second **plasma**.
- **Insulin secretion** has **dynamic (anticipatory) and static** components driven by the
  glucose signal; hepatic insulin extraction links the two compartments.
- Plasma insulin then feeds back to drive insulin-dependent glucose utilization and to suppress
  EGP, closing the glucose-insulin loop.

**4. The "meal" forcing** [Abstract + secondary source]
The meal is an oral glucose input. Ingested glucose flows stomach → gut → plasma, producing a
**smooth, delayed, time-varying glucose rate of appearance** rather than a step/impulse. The
abstract confirms the model reproduces both a **single meal** and **a full day (breakfast, lunch,
dinner)**.

**Difference vs. the IVGTT-based Cobelli (1982) "minimal model" lineage** [Secondary source +
general background — flag for verification]
- **Input route:** Earlier minimal models were identified from the **intravenous glucose
  tolerance test (IVGTT)**, where glucose enters as an essentially **instantaneous IV bolus**.
  The 2007 meal model instead represents **oral ingestion**, adding the explicit **GI/gastric-
  emptying submodel** that turns a meal into a gradual plasma Ra. There is **no GI absorption
  compartment** in the IV minimal model.
- **Purpose/scope:** The minimal model is a **parsimonious, parameter-estimation** tool (e.g.,
  insulin sensitivity SI, glucose effectiveness SG from one test). The 2007 model is a **maximal /
  simulation** model meant to generate realistic postprandial trajectories for testing sensors,
  insulin algorithms, and decision-support systems.
- **Identification data:** The 2007 model is anchored to **quasi-model-independent flux estimates**
  from a **triple-tracer meal** study (directly measuring Ra, EGP, utilization, secretion), which
  the single-test IVGTT minimal model does not provide.
- (The precise relationship to Cobelli 1982 specifically is stated here from general domain
  knowledge and should be confirmed against the primary article's Introduction before citing in
  the report.)

## Relevance to Part 1 (meal simulation exercise)

The term-project exercise asks to simulate a **meal / glucose infusion delivered over ~60 minutes**
rather than an instantaneous IV pulse. This paper is the canonical justification:

- It shows physiologically **why** an oral meal should be modeled as a **distributed, time-varying
  glucose rate of appearance** (gastric emptying + intestinal absorption) instead of an impulse —
  directly motivating replacing an IV bolus with a finite-duration infusion/Ra profile.
- The **GI submodel** provides the conceptual template for shaping a 60-minute glucose input
  (gradual rise, peak, decay) rather than a Dirac-like spike.
- It contrasts cleanly with **IVGTT minimal-model** assignments earlier in the course, making it a
  strong reference for explaining the modeling choice and its biological basis.
- For hands-on reproduction, the **BioModels SBML (BIOMD0000000379)** and the open-access **GIM**
  software paper give the equations/implementation without needing the paywalled PDF — useful if
  Part 1 requires running or referencing the actual equations (cite those sources explicitly, and
  verify any equation/parameter against them before use).

## Sources (URLs)

- PubMed (abstract, citation, PMID 17926672):
  https://pubmed.ncbi.nlm.nih.gov/17926672/
- IEEE Xplore (primary article, paywalled):
  https://ieeexplore.ieee.org/document/4303268
- BioModels curated model BIOMD0000000379:
  https://www.ebi.ac.uk/biomodels/BIOMD0000000379  (redirects to https://biomodels.org/BIOMD0000000379)
- GIM software paper, open access (PMC2769591):
  https://pmc.ncbi.nlm.nih.gov/articles/PMC2769591/
- GIM software paper (SAGE):
  https://journals.sagepub.com/doi/10.1177/193229680700100303
- Semantic Scholar listing:
  https://www.semanticscholar.org/paper/Meal-Simulation-Model-of-the-Glucose-Insulin-System-Man-Rizza/b6970e13815808b07dd4405a69f4311f4f9862a4
- Mayo Clinic Pure (bibliographic):
  https://mayoclinic.elsevierpure.com/en/publications/meal-simulation-model-of-the-glucose-insulin-system/
- SciRP reference record (citation/pages confirmation):
  https://www.scirp.org/reference/referencespapers?referenceid=3059317
- ResearchGate listing (Request PDF, not guaranteed open):
  https://www.researchgate.net/publication/5917874_Meal_Simulation_Model_of_the_Glucose-Insulin_System
