# Reference 4 — Garnett & Anderson (1993): IC HIV Model (basis of the sIC model)

> **Academic-honesty note.** Everything below is sourced from the **abstract** and
> bibliographic metadata only. The **full text is paywalled** (see Access status), so
> internal equations, exact parameter values, and tables from the paper could **not** be
> read directly. Statements taken verbatim from the abstract are quoted. Statements that
> describe the model structure but are *inferred* from the abstract, the paper title, or
> the standard IC-model literature are explicitly flagged as **[inferred — not confirmed
> from full text]**. No equations or numbers have been invented; where a quantity is not
> available it is stated as "not available from abstract."

---

## Full citation

Garnett, G. P., and R. M. Anderson. 1993. "Factors controlling the spread of HIV in
heterosexual communities in developing countries: patterns of mixing between different
age and sexual activity classes." *Philosophical Transactions of the Royal Society of
London. Series B, Biological Sciences* **342** (1300): 137–159.

- **DOI:** 10.1098/rstb.1993.0143
- **PMID:** 7904355
- **Published:** 29 October 1993
- **Author affiliation:** Parasite Epidemiology Research Group, Imperial College, London
  University, U.K. (the "Imperial College / IC" group — this is the origin of the "IC
  model" name used in Haefner Ch. 15).
- **Citation count:** ~201 (Semantic Scholar, as of retrieval).

This is the **foundational paper for the Imperial College (IC) HIV/AIDS compartment
model**. Haefner's textbook (Ch. 15) presents a *simplified* version, the **sIC model**,
and term-project Part 2 (HIV vaccination on the sIC AIDS model) builds on that
simplification.

---

## Access status

- **NOT open access / paywalled.** Europe PMC reports `isOpenAccess = N`; Semantic Scholar
  reports access status `CLOSED` with no open-access PDF URL.
- The publisher landing page (`royalsocietypublishing.org/doi/10.1098/rstb.1993.0143`)
  returned **HTTP 403** to automated fetching; access requires an institutional
  subscription, library access, or interlibrary loan.
- **Abstract is freely available** via PubMed (PMID 7904355) and the Europe PMC REST API
  — the verbatim abstract below comes from the Europe PMC `abstractText` field.
- For full-text retrieval, use an institutional login at the DOI above, or request via a
  university library.

---

## Abstract (verbatim — from Europe PMC `abstractText`, PMID 7904355)

> "The paper describes the development and analysis of a mathematical model of the spread
> and demographic impact of HIV in heterosexual communities in developing countries. The
> model extends previous work in this area by the representation of patterns of mixing
> between and within different age and sexual activity classes in a two sex structure.
> Summary parameters are derived to represent different mixing patterns, ranging from
> assortative via random to disassortative, as are methods to ensure that particular
> mixing patterns between different age and sexual classes (stratified on the basis of
> rates of sexual partner change) meet constraints that balance the supply and demand for
> sexual partners as AIDS induced mortality influences the demographic structure of a
> population. Analyses of model behaviour rely on numerical methods due to the complexity
> of the mathematical framework, and sensitivity analyses are conducted to assess the
> significance of different assumptions and different parameter assignments. Simulated
> patterns of HIV spread across the two sexes and various age classes are compared with
> observed patterns in Uganda. The principle conclusion of the study is that the pattern
> of mixing between age and sexual activity classes, combined with the assumptions made to
> balance supply and demand between the sexes have a very major influence on the predicted
> pattern of HIV spread and the demographic impact of AIDS. The paper ends with a
> discussion of future needs in model development and data acquisition."

---

## Model summary

### Confirmed from the abstract

- **Two-sex structure.** The model tracks both sexes (male / female) explicitly — required
  for heterosexual transmission and for the male→female vs. female→male asymmetry.
- **Stratification by age class AND sexual-activity class.** Individuals are partitioned
  into multiple **age classes** and multiple **sexual-activity classes**, where activity
  classes are **"stratified on the basis of rates of sexual partner change."** This is the
  source of the partner-change-rate parameter (commonly denoted *c*) used downstream.
- **Mixing matrix with a tunable assortativeness.** The paper derives **"summary
  parameters … to represent different mixing patterns, ranging from assortative via random
  to disassortative."** That is, a mixing matrix governs who pairs with whom across age and
  activity classes, spanning the spectrum:
  - **Assortative** (like-with-like; high-activity with high-activity),
  - **Random / proportionate** (mixing in proportion to availability),
  - **Disassortative** (unlike-with-unlike).
- **Supply–demand balancing of partnerships.** A central methodological contribution is the
  set of **constraints that "balance the supply and demand for sexual partners"** between
  the sexes — i.e. the total partnerships demanded by one sex/class must equal those
  supplied by the partner sex/class. This balancing must hold even as **AIDS-induced
  mortality changes the demographic structure** over time. (This balancing problem is the
  subject of the companion paper — see Sources.)
- **Demographic impact of AIDS.** The model couples HIV/AIDS dynamics to population
  demography, so AIDS mortality feeds back on age/sex structure.
- **Solved numerically**, with **sensitivity analyses** over assumptions and parameter
  assignments.
- **Empirical comparison: Uganda.** Simulated HIV spread by sex and age class is compared
  with observed Ugandan data — i.e. a sub-Saharan / developing-country epidemiological
  setting.

### Relevant to the sIC simplification — [inferred — NOT confirmed from full text]

The following describe the *standard IC-model structure* that Haefner's sIC model
simplifies. They are consistent with the title/abstract but the **specific compartment
equations, force-of-infection algebra, and parameter values are in the paywalled full
text and were not read.** Treat as background context, not as quotations from the paper:

- **Compartments by sex.** Susceptible (S), HIV-infected (I), and AIDS (A) compartments,
  maintained separately for males and females within each age × activity class.
- **Force of infection (λ).** For a susceptible in a given sex/class, the hazard of
  infection is **[inferred]** built from: the **partner-change rate** *c* of that class,
  the **per-partnership transmission probability** (sex-specific: β_{m→f} for
  male-to-female and β_{f→m} for female-to-male), the **mixing matrix** weighting which
  partner classes are contacted, and the **prevalence of infectious partners** in those
  classes. The asymmetry β_{m→f} ≠ β_{f→m} is a well-known feature of heterosexual HIV
  models. **Exact functional form: not available from abstract.**
- **Partner-change rate c.** The activity classes are defined by *c*; the project brief
  cites typical developing-country values on the order of **~1–4 partners/year** for the
  represented activity classes. **These specific numeric values are NOT in the abstract**
  and could not be confirmed against the full-text tables — flag as unverified.
- **AIDS progression / incubation.** Movement I → A at some progression rate, and
  AIDS-associated mortality. **Specific rates: not available from abstract.**
- **Perinatal (vertical / mother-to-child) transmission.** A perinatal transmission
  pathway is a standard feature of two-sex developing-country IC models and is plausibly
  present here given the demographic coupling, **but the abstract does not mention it
  explicitly** — treat as **[inferred / unconfirmed]**.
- **Demographic rates** (births, non-AIDS mortality, recruitment into the sexually active
  population) appropriate to a high-fertility developing-country setting. **Specific
  values: not available from abstract.**

> **On Haefner Table 15.2.** The brief states the textbook's Table 15.2 parameter values
> are "based on Garnett & Anderson 1993." I could **confirm the lineage** (this paper is
> the IC-model source, by the Imperial College group) but **could NOT independently verify
> the specific numbers** (transmission probabilities, partner-change rates, AIDS-progression
> rate, demographic rates) against the paper's own tables, because the full text is
> paywalled. **Do not present Table 15.2 values as quoted from this paper.** They should be
> cited as "Haefner Ch. 15, attributed to / adapted from Garnett & Anderson 1993," with the
> understanding that Haefner may have rounded or adapted them.

---

## Relevance to Part 2 (HIV vaccination on the sIC AIDS model)

- This paper is the **primary-source root** of the model chain:
  **Garnett & Anderson 1993 (IC model)** → **Haefner Ch. 15 (sIC simplification)** →
  **term-project Part 2 (add vaccination)**.
- The **S / I / A compartment-by-sex** structure and the **force of infection** built from
  partner-change rate *c*, sex-specific transmission probabilities β_{m→f}/β_{f→m}, and the
  **mixing matrix** are exactly the components a **vaccination extension** modifies:
  a vaccine typically adds a protected/vaccinated class (or reduces susceptibility /
  per-act transmission probability / progression), altering λ for vaccinated susceptibles.
- The paper's headline result — that **mixing pattern (assortative ↔ disassortative) and
  the supply–demand balancing assumptions dominate predicted spread** — is the key caveat
  for Part 2: **vaccination outcomes will be sensitive to the assumed mixing structure**,
  so any vaccination result should be reported alongside a sensitivity analysis over the
  mixing parameter (mirroring the original paper's own sensitivity-analysis approach).
- The Uganda calibration establishes the **developing-country parameter regime** the sIC
  model inherits.

---

## Sources (URLs)

- PubMed record (citation + abstract): https://pubmed.ncbi.nlm.nih.gov/7904355/
- DOI / publisher landing page (PAYWALLED, returned HTTP 403 to fetch):
  https://royalsocietypublishing.org/doi/10.1098/rstb.1993.0143
- Europe PMC REST API (verbatim `abstractText`, `isOpenAccess = N`):
  https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7904355&resultType=core&format=json
- Semantic Scholar (access status CLOSED, citation count ~201):
  https://api.semanticscholar.org/graph/v1/paper/DOI:10.1098/rstb.1993.0143
- Wikidata entry: https://www.wikidata.org/wiki/Q38889802
- Companion paper on the supply–demand balancing problem, "Balancing sexual partnerships
  in an age and activity stratified model of HIV transmission in heterosexual
  populations": https://pubmed.ncbi.nlm.nih.gov/7822888/
