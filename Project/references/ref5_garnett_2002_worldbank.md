# Reference 5 — Stover, Garnett, Seitz & Forsythe (2002): The Epidemiological Impact of an HIV/AIDS Vaccine in Developing Countries (World Bank PRWP 2811)

> Academic-honesty note: Items are tagged **[Full text]** (read directly from the open-access
> World Bank PDF retrieved and OCR-free text-extracted in this session), **[Abstract/verbatim]**,
> or **[Bibliographic]**. Quoted passages are reproduced verbatim from the extracted PDF text and
> marked with quotation marks. Nothing here is invented; where the source does not state a value,
> that is noted explicitly rather than filled in.

## Full citation & URL

**As listed in the term-project bibliography (the relevant Technical Annex):**

> Garnett, G. P., K. Desai, and J. Williams. 2002. "Technical Annex I. The epidemiological
> impact of an HIV/AIDS vaccination as a function of vaccine properties: Results of the Imperial
> College model." Pages i–26 in J. Stover, G. P. Garnett, S. Seitz, and S. Forsythe, editors.
> Policy Research Working Paper 2811. World Bank, New York, USA.

**Parent World Bank working paper that was located and read in full:**

Stover, J., G. P. Garnett, S. Seitz, and S. Forsythe. 2002. *The Epidemiological Impact of an
HIV/AIDS Vaccine in Developing Countries.* Policy Research Working Paper 2811. World Bank,
Development Research Group (Public Services), Washington, DC. March 2002. [Full text]

- **World Bank documents landing page:**
  https://documents.worldbank.org/en/publication/documents-reports/documentdetail/896881468760559617/the-epidemiological-impact-of-an-hiv-aids-vaccine-in-developing-countries
- **Direct PDF (read this session):**
  http://documents1.worldbank.org/curated/en/896881468760559617/pdf/multi0page.pdf
  (the documents.worldbank.org `.../pdf/multi0page.pdf` path 302-redirects to documents1.worldbank.org)
- Project sponsored by the European Commission and the World Bank Development Research Group
  (task manager Martha Ainsworth); launched on the recommendation of the World Bank's AIDS
  Vaccine Task Force (May 2000). [Full text]

## Access status

- **OPEN ACCESS — confirmed and obtained.** The 40-page parent working paper PDF (PRWP 2811)
  was downloaded from the World Bank documents repository (file ~1.84 MB, 40 pages, PDF 1.4,
  CreationDate 2002-04-12) and its embedded text layer was extracted cleanly with `pdftotext`.
  No paywall, no login.
- **Important scope note on the cited "Technical Annex I":** The standalone *Technical Annex I*
  (Garnett, Desai & Williams; paginated i–26) is a **separate companion document** to PRWP 2811
  and is **not contained inside** the 40-page PDF that the World Bank serves under this document
  ID. The parent paper references the underlying Imperial College technical write-up in its
  footnote 6 as: Garnett, G. P., and J. Williams. 2001. "The potential impact of prophylactic HIV
  vaccination as a function of vaccine properties." Department of Infectious Disease Epidemiology,
  Imperial College, London, July. [Full text — footnote 6]
  That standalone annex / 2001 technical report was **not separately located in open-access form**
  in this session. **However**, the parent paper itself describes the Imperial College
  vaccination-modeling approach in enough detail to support Part 2 — that description is the basis
  for everything below and is all **[Full text]** from the retrieved PDF.

## Document summary

The paper uses **two simulation models** to study how vaccine characteristics and program
strategies affect the epidemiological impact and cost-effectiveness of a preventive HIV/AIDS
vaccine in developing-country settings: [Full text]

1. **The Imperial College (IC) model** — "derived from a long tradition of HIV/AIDS models
   developed by Roy Anderson, Geoff Garnett and others now at the Imperial College in London."
   Applied to **rural Zimbabwe (Manicaland)** data. This is the model the term project is "loosely
   based on."
2. **iwgAIDS** — maintained by Steve Seitz (University of Illinois), applied to **Kampala
   (Uganda)** and **Thailand**.

Headline finding (verbatim, Abstract): *"A vaccine with 50 percent efficacy and 10 years duration
supplied to 65 percent of all adults could reduce HIV incidence by 25 to 60 percent, depending on
the context and stage of the epidemic. Better efficacy and longer duration would provide even more
impact."* [Abstract/verbatim]

## Vaccination modeling approach (Imperial College model)

This is the section most relevant to Part 2. All **[Full text]**.

### Compartments by immunization status

The IC model "examines the heterosexual spread of HIV in a population of adults aged 15–49,"
segregated by **age, sex, and sexual activity class** (four activity classes; individuals stay in
their class for life, but class characteristics vary with age). On top of that, it
**"further divides the population into four categories according to immunization status"**:

1. **Fully immunized** — "completely protected from HIV infection."
2. **Partially immunized** — "has a reduced probability of HIV infection."
3. **Not immunized** (i.e., susceptible / not vaccinated).
4. **Previously vaccinated but no longer protected** by the vaccine and not yet eligible for
   re-vaccination — here the person is "fully exposed to the risk of HIV infection."

Once infected, a person "progresses eventually to AIDS and death."

### Transitions (verbatim)

> "The effect of a vaccine in the model is to move the vaccinated person from the susceptible
> (not immunized) category to the fully immunized or partially immunized category, depending on
> the type of vaccine. … If the duration of the protection of the vaccine is not lifetime, then a
> person can move from the fully or partially immunized category to the previously vaccinated
> category, where he or she is fully exposed to the risk of HIV infection." [Full text]

So the flow is: **Susceptible → (vaccination) → Immunized (fully or partially) → (waning) →
Previously-vaccinated-unprotected → (re-vaccination, after a delay) → Immunized again.**

### Vaccine property #1 — Type of protection ("take" vs "degree")

> "A vaccine might achieve 50 percent effectiveness by completely protecting 50 percent of those
> vaccinated (**take**) or by reducing the probability of infection by 50 percent for everyone
> (**degree**)." [Full text]

- **Take:** a fraction of vaccinees are moved into the **fully immunized** (sterilizing) compartment;
  the rest get no protection.
- **Degree:** all vaccinees are moved into a **partially immunized** compartment with a reduced
  per-exposure infection probability.
- The paper's "standard" vaccine is **degree-type** (see results below).

### Vaccine property #2 — Efficacy

> "In a take type vaccine, efficacy is the percentage of people vaccinated who are completely
> protected. In a degree type vaccine, efficacy is the percent reduction in probability of
> infection for those vaccinated." Scenarios examined: **50, 75, and 95 percent.** [Full text]

### Vaccine property #3 — Duration / waning

> "Duration refers to the length of protection… we examined vaccines with durations of **5 years,
> 10 years and lifetime.** In the **Imperial College model, waning vaccine protection is simulated
> with a mean exponential decay process, with a mean of five or ten years.**" [Full text]

This is the key mechanism the project's loss-of-protection rate `l` represents: **exponential
decay of protection** at a constant per-capita rate. (A mean duration of 10 years corresponds to a
waning rate of 1/10 = 0.1 per year — exactly the project's `l = 0.1/yr`.) Note: in the IC model,
people whose protection wanes are "eligible for re-vaccination **but only after a two year delay**"
— i.e., there is an intermediate unprotected-but-not-yet-revaccinable compartment. [Full text]

### Vaccination rate / coverage (strategy)

> "In this study we have assumed that vaccine coverage will reach **65 percent of the target
> population five years after the program starts.**" [Full text]

The "standard" program (verbatim): *"Coverage grows to reach 65 percent of all adults 15–49 five
years after the start of the program. After year five new vaccinations occur at a rate to cover 65
percent of the population growth. These vaccinations are given to new entrants into the adult
population and older adults who were not vaccinated earlier or whose protection from an earlier
vaccination has waned. Thus, 65 percent coverage means that roughly 65 percent of adults have ever
been vaccinated, even though for some, the vaccination may no longer be providing protection."*
[Full text]

- **Targeting strategies examined:** all adults; high-risk groups; teenagers (age-15 entrants);
  adult women (reachable via ante-natal clinics). [Full text]
- **Re-vaccination:** programs both with no re-vaccination and with re-vaccination "in order to
  maintain coverage at 65 percent of the target group." [Full text]
- Footnote 26 (verbatim): *"this coverage figure applies only to susceptible adults."* [Full text]

### Behavioral reversal (risk compensation)

The model also tests behavioral reversal: vaccinees (or everyone) returning "to the levels of
unsafe sex at the start of the epidemic." Key qualitative result: with **take** protection,
behavior reversal among the effectively (sterilizingly) protected "will not matter at all"; with
**degree** protection, reversal "could offset much of the protective effect." [Full text]

### Impact measures

- **Adult HIV incidence** = "number of new adult infections occurring each year divided by the
  number of adults who are not infected at the beginning of the year." (Primary outcome; most
  results shown this way.) [Full text]
- **HIV prevalence** = "number of adults … [infected]." [Full text]
- **Infections averted** (vs. a no-vaccine baseline), over a 15-year horizon. [Full text]
- **Cost per infection averted** = net present value of vaccination cost ÷ infections averted
  over the projection period; real **discount rate 4 percent**; standard cost **$20/person**
  (sensitivity $5 and $100). [Full text]

## Key quantitative results

All **[Full text]** unless noted. Baseline = no-vaccine projection; horizon = 15 years from program
start.

**Standard vaccine** (degree type, 50% efficacy, 10-yr duration, 65% adult coverage by year 5, no
behavioral reversal):

- Reduces adult HIV incidence by **~60% in Thailand and Kampala** and **~25% in Zimbabwe.**
- "Incidence is not reduced to zero … Since coverage is only 65 percent, efficacy is only 50
  percent and the duration of effectiveness is only ten years, many people are left unprotected."
- Short-run effect ≈ **0.50 × 0.65 ≈ 32%** incidence reduction once coverage is reached (verbatim:
  *"HIV incidence is about 32 percent (0.50 × 0.65) lower than it would be without the vaccine"*).

| Scenario | Imperial College / rural Zimbabwe | iwgAIDS / Kampala | iwgAIDS / Thailand |
|---|---|---|---|
| Standard-vaccine cost per infection averted ($20/person) | $290 | $280 | $1,410 |

**Efficacy** (cost per infection averted, $20/person):

| Efficacy | Rural Zimbabwe | Kampala | Thailand |
|---|---|---|---|
| 50% | $290 | $280 | $1,410 |
| 75% | $160 | $180 | $960 |
| 95% | $110 | $150 | $780 |

At 95% efficacy "the vaccination program can nearly extinguish the epidemic." No incidence
threshold below which the vaccine is useless was observed in these settings; impact increases
regularly with efficacy. [Full text]

**Duration** (cost per infection averted, $20/person):

| Duration | Rural Zimbabwe | Kampala | Thailand |
|---|---|---|---|
| 5 years | $390 | $310 | $1,470 |
| 10 years | $290 | $280 | $1,410 |
| Lifetime | $190 | $260 | $1,410 |

In the IC model a short-duration (5-yr) vaccine has "only half" the effect of a lifetime vaccine
(because of the 2-year re-vaccination delay leaving people exposed). In iwgAIDS, duration matters
little for an all-adult program because risk is concentrated in adolescence. [Full text]

**Targeting & behavioral reversal (qualitative):** vaccinating only teenagers gives ~half the
impact of all-adults but is often more cost-effective; targeting women gives ~half the impact
(women not protected by herd effect from other women); behavioral reversal "could erode much of
the benefits," especially for degree-type vaccines. [Full text]

## Direct relevance to Part 2 (how to model P_{f,2}, P_{m,2}, ν, l)

The project asks to add HIV vaccination to the sIC AIDS model with a **Protected (P) compartment**,
vaccinating **susceptible age-2** individuals at rate **ν = 0.65/yr**, with a fraction losing
protection at rate **l = 0.1/yr**. The Garnett/IC approach maps onto this directly:

1. **Protected compartment = the IC "immunized" category.** The project's single `P` compartment
   is the modeling simplification of the IC model's "fully immunized" + "partially immunized"
   states. If `P` is treated as **fully protecting** (no infection while in `P`), that is the IC
   **"take"** action; if `P` only **reduces** the force of infection, that is **"degree"** action.
   The source supports either reading — choose one and state it. The paper's *standard* vaccine is
   **degree** type, but it also models full (take) protection.

2. **Vaccination flux Susceptible → P.** The IC model moves susceptibles into the immunized
   category at the program's vaccination rate. The project's **ν = 0.65/yr** is the per-capita
   vaccination rate applied to **susceptible age-2** individuals — consistent with the paper's
   choice to target a coverage of **"65 percent"** and its footnote that coverage "applies only to
   susceptible adults." (Caveat: in the paper 65% is a *coverage level reached after 5 years*,
   whereas the project uses 0.65 as a *constant per-year rate constant* — a deliberate
   simplification; worth noting in the write-up.) Restricting vaccination to **age-2** mirrors the
   paper's interest in vaccinating **new entrants / teenagers (age-15 entrants)** at the start of
   sexual activity.

3. **Waning Protected → Susceptible at rate l.** The IC model waning is an **exponential decay of
   protection with a mean of 5 or 10 years.** A mean duration of **10 years ⇒ rate 1/10 = 0.1/yr**,
   exactly the project's **l = 0.1/yr.** The "fraction losing protection" returning to susceptible
   is the project's analogue of the IC transition from "immunized" to "previously vaccinated but no
   longer protected" — which the project collapses straight back into `S` (the project omits the
   IC model's intermediate 2-year re-vaccination-delay compartment). Flux out of `P` = `l · P`.

4. **Two protected compartments P_{f,2}, P_{m,2}.** These are simply the female/male
   sex-disaggregated Protected compartments at age class 2 — matching the IC model's segregation
   "by age, sex, and sexual activity class." The female-vs-male split also lets the project capture
   the paper's "targeting women" insight (women not protected by herd immunity from other women).

5. **Expected qualitative behavior to validate against.** Because coverage and efficacy are
   partial, prevalence/incidence should drop **but not to zero**; the steady-state protected
   fraction is governed by ν vs. l (inflow vs. waning); higher ν or lower l (longer duration) ⇒
   larger incidence reduction — all consistent with the paper's results.

**Bottom line for Part 2:** model `dS/dt` to lose `ν·S` to `P` and gain `l·P` back; model
`dP/dt = ν·S − l·P − (deaths)`, with `P` either immune (take) or under a reduced force of infection
(degree). ν = 0.65/yr and l = 0.1/yr correspond to the paper's "65% coverage" and "10-year mean
duration" standard scenario.

## Sources (URLs)

- World Bank document landing page (open access):
  https://documents.worldbank.org/en/publication/documents-reports/documentdetail/896881468760559617/the-epidemiological-impact-of-an-hiv-aids-vaccine-in-developing-countries
- World Bank direct PDF, read in full this session (302-redirect target):
  http://documents1.worldbank.org/curated/en/896881468760559617/pdf/multi0page.pdf
- Underlying IC technical report referenced as the basis of the cited Technical Annex I
  (footnote 6 of PRWP 2811; not separately retrieved): Garnett, G. P., and J. Williams. 2001.
  "The potential impact of prophylactic HIV vaccination as a function of vaccine properties."
  Department of Infectious Disease Epidemiology, Imperial College, London.
- Related open-access modeling work corroborating the take/degree/duration framework (context
  only, not the cited source): PLOS ONE / PMC4701445 —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4701445/
