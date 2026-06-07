# Papers read in preparing this term project

This folder is the "papers you have read" submission. Each `refN_*.md` file is a structured
reading summary (full citation, access status, key content, and how it informed the project),
written with explicit provenance — verbatim quotes where a paper was read in full, and clear
flags where only the abstract/secondary sources were accessible (paywalled originals). No content
is fabricated; access limits are stated honestly.

## Part 1 — glucose–insulin regulation
1. **Cobelli, Federspil, Pacini, Salvan & Scandellari (1982)** — *An integrated mathematical model of
   the dynamics of blood glucose and its hormonal control.* Math. Biosci. 58:27–60.
   → `ref1_cobelli_1982.md`. The model implemented in Part 1 (via Haefner Ch. 12). **Paywalled
   (Elsevier);** model structure/parameters taken from the textbook restatement and cross-checked
   against secondary sources; access flagged in the file.
2. **Makroglou, Li & Kuang (2006)** — *Mathematical models and software tools for the glucose–insulin
   regulatory system and diabetes: an overview.* Appl. Numer. Math. 56(3–4):559–573.
   → `ref2_makroglou_2006.md`. **Open access (author copy);** read in full. Situates the Cobelli model
   among the broader modeling/software landscape (minimal model, delay models, etc.).
3. **Dalla Man, Rizza & Cobelli (2007)** — *Meal simulation model of the glucose–insulin system.*
   IEEE TBME 54(10):1740–1749.
   → `ref3_man_2007.md`. **Paywalled;** abstract + model description captured. The modern meal-model
   lineage (UVA/Padova simulator) that motivates Part 1's meal/ice-cream exercises (Ex 4, Ex 7).

## Part 2 — HIV/AIDS transmission and vaccination
4. **Garnett & Anderson (1993)** — *Factors controlling the spread of HIV in heterosexual communities in
   developing countries.* Phil. Trans. R. Soc. Lond. B 342:137–159.
   → `ref4_garnett_anderson_1993.md`. **Paywalled;** abstract + the IC-model structure (age/activity
   classes, mixing matrices) captured. Source of the sIC parameters (Table 15.2).
5. **Garnett, Desai & Williams (2002)** — *The epidemiological impact of an HIV/AIDS vaccination as a
   function of vaccine properties* (Imperial College model). World Bank Policy Research WP 2811.
   → `ref5_garnett_2002_worldbank.md`. **Open access; read in full.** The direct basis of Part 2 —
   confirms the project's vaccine parameters: **ν = 0.65/yr ↔ the paper's "65% coverage"**, and
   **l = 0.1/yr ↔ its "10-year mean" exponential waning of protection**; informs the cost-effectiveness
   framing (cost per infection averted).

Textbook background (not a "paper" but the primary source for both models): Haefner (2005),
*Modeling Biological Systems*, 2nd ed., Ch. 12 & 15 — extracted notes in `../textbook_notes/`.
