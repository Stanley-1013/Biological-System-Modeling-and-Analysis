# Reference 2 — Makroglou, Li & Kuang (2006): Glucose-Insulin Models & Software (Overview)

## Full citation

Makroglou, A., J. Li, and Y. Kuang. 2006. "Mathematical models and software tools for the glucose-insulin regulatory system and diabetes: an overview." *Applied Numerical Mathematics* 56(3–4): 559–573.

- DOI: 10.1016/j.apnum.2005.04.023
- ISSN: 0168-9274
- Publisher: Elsevier B.V. (© 2005 IMACS)
- Available online: 31 May 2005
- Author affiliations (from full text): A. Makroglou — Department of Mathematics, University of Portsmouth, UK; J. Li and Y. Kuang — Department of Mathematics and Statistics, Arizona State University, Tempe, AZ, USA.
- Funding note (from full text): partially supported by NSF DMS-0077790 and DMS/NIGMS-0342388.

The full citation, including volume, issue (3–4), page range, and DOI, is **confirmed**. The page count (559–573) and DOI string were verified against the article's own title page/footer in the open-access preprint.

## Access status

- **Publisher (ScienceDirect):** paywalled / closed access (abstract page returned HTTP 403; Semantic Scholar reports "Closed access," no open-access PDF flagged there).
- **Open-access preprint AVAILABLE** on Yang Kuang's ASU homepage: http://math.la.asu.edu/~kuang/paper/athena.pdf (entry #81 on his publications list, ~358 KB). This PDF is the full published article (matching journal pagination 559–573) and was successfully retrieved and read for this summary.
- Other copies referenced online: ResearchGate, Academia.edu (not independently verified here).

**Important:** The content summary below is drawn from the **FULL TEXT** of the ASU open-access PDF, not merely the abstract. The abstract is quoted verbatim and labeled as such.

## Abstract (verbatim, from full text)

> An overview of some of the mathematical models appearing in the literature for use in the glucose-insulin regulatory system in relation to diabetes is given, enhanced with a survey on available software. The models are in the form of ordinary differential, partial differential, delay differential and integro-differential equations. Some computational results are also presented.

**Keywords (verbatim):** Glucose-insulin; Diabetes; Mathematical models; Software tools; Overview.

## Content summary (from FULL TEXT)

This is a survey/overview paper, not a single new model. It catalogues classes of glucose-insulin models and surveys software for their analysis and simulation. The paper notes models in the literature can be classified mathematically as ODEs, DDEs, PDEs, Fredholm integral equations (FIEs, in parameter estimation), stochastic differential equations (SDEs), and integro-differential equations (IDEs); the paper itself focuses on ODE, DDE, IDE, and PDE models.

**Section structure (as stated in the paper):**

- **§1 Introduction** — physiology of the glucose-insulin regulatory system (β-cells/insulin, α-cells/glucagon, Langerhans islets), normal glucose range 70–110 mg/dl, type 1 vs. type 2 diabetes, and the multiple time-scales of insulin secretion oscillations (seconds-scale, rapid 5–15 min, and ultradian 50–120 min).
- **§2 ODE models** — Centered on the Bergman et al. "minimal model" (the IVGTT minimal model used to estimate glucose effectiveness S_G and insulin sensitivity S_I from intravenous glucose tolerance test data). Notes the minimal model is "structurally incorrect"/improper in a rigorous mathematical sense (citing De Gaetano & Arino). Also reviews the Sturis et al. (1991) six-dimensional ODE model of ultradian oscillations and the Tolić et al. (2000) simplification, plus subcutaneous-insulin-kinetics models reviewed by Nucci & Cobelli (2000).
- **§3 DDE (delay differential equation) models** — Models adding explicit time delays (e.g., hepatic glucose production delay, insulin response delay) to capture ultradian oscillations; references the authors' own related work (Li, Kuang and collaborators) and the Generic IVGTT model; bifurcation analysis using DDE-BifTool.
- **§4 Integro-differential equation (IDE) models** — Motivated because the widely used minimal model is considered improper; presents the De Gaetano & Arino "dynamic" delay integro-differential model as a more realistic alternative.
- **§5 PDE models** — e.g., Wach et al. (1995) subcutaneous insulin absorption model, Keener (2001) infusion-induced oscillatory secretion, Boutayeb & Derouich / Boutayeb & Twizell age-structured models, and reaction-diffusion models of the islets.
- **§6** — Pointers to other modeling approaches.
- **§7 Parameter estimation techniques** — e.g., classical methods (Pacini & Bergman), Bayesian estimation, and deconvolution/regularization (Caumo & Cobelli; De Nicolao et al.).
- **§8 Software packages** — surveyed below.
- **§9 Computational results** — worked examples applying DDE-BifTool, DDE23, and MatCont to the Generic IVGTT and Sturis ultradian-oscillation models (e.g., a Hopf bifurcation located at τ ≈ 457.72 in the Generic IVGTT model; the paper notes some detected bifurcation points fall in physiologically non-meaningful parameter zones).

**Named models referenced:** Bergman minimal model (Bergman, Ider, Bowden & Cobelli 1979); Bolie (1961, a pioneering ODE model); Sturis et al. (1991) ultradian-oscillation model; Tolić et al. (2000); De Gaetano & Arino (2000) delay integro-differential "dynamic" model; Li et al. (2001) IVGTT delay models / Generic IVGTT model; Wach et al. (1995) and Keener (2001) PDE models.

**Software tools surveyed (named in the paper):**

- Minimal-model / estimation tools: **WINSTODEC** (Sparacino et al. 2001, MATLAB, stochastic deconvolution); a **MATLAB FSIGTT minimal-model routine suite** (Van Riel 2004); **SAAM II**; **WinSAAM**; **COMKAT** (MATLAB-based compartmental kinetics); a **Mathematica**-based tool (Benyó et al.) using the Control System Professional Suite; **Mlab** (Civilized Software).
- ODE/DDE analysis, continuation & bifurcation: **DDE-BifTool**; **AUTO / AUTO97** (with HomCont); **XPPAUT**; **DDE23** (Shampine & Thompson; bundled in MATLAB 6.5); **Time-Delay System Toolbox** (Ural Branch, Russian Academy of Sciences); **MatCont** (MATLAB ODE bifurcation GUI package).

## Relevance to Part 1 (glucose-insulin regulation modeling)

This is an ideal **background/orientation reference** for Part 1. It:
- frames the physiology and the type 1 vs. type 2 distinction that motivate the modeling;
- provides a clean taxonomy (ODE → DDE → IDE → PDE) for organizing a literature/methods section;
- introduces the **Bergman minimal model** (the canonical entry point for IVGTT-based S_G/S_I estimation) and flags its known mathematical shortcomings, pointing to delay/integro-differential alternatives (De Gaetano-Arino, Li-Kuang) if Part 1 extends beyond the minimal model;
- lists concrete, citable **software** (MatCont, DDE-BifTool, XPPAUT, DDE23) usable for simulating and analyzing such models in the project.

Note: this paper is a 2006 overview; for current numerical values, parameters, or the latest models, primary sources (Bergman 1979, Sturis 1991, De Gaetano-Arino 2000, Li-Kuang 2006/2007) should be cited directly rather than relying on this survey's secondary descriptions.

## Sources (URLs)

- Open-access full-text PDF (ASU / Yang Kuang homepage): http://math.la.asu.edu/~kuang/paper/athena.pdf
- Publisher (paywalled): https://www.sciencedirect.com/science/article/abs/pii/S0168927405000929
- Bibliographic record (University of Portsmouth): https://researchportal.port.ac.uk/en/publications/mathematical-models-and-software-tools-for-the-glucose-insulin-re/
- Citation record (SCIRP reference): https://www.scirp.org/reference/referencespapers?referenceid=1177051
- Kuang ASU publications list: http://math.la.asu.edu/~kuang/paper.html

---
*Compiled via WebSearch/WebFetch + direct extraction of the open-access PDF. Abstract is verbatim; content summary is from the full text. No equations or numbers were fabricated; the few numeric values cited (glucose range, oscillation periods, the τ ≈ 457.72 bifurcation example) are reproduced from the paper's own text.*
