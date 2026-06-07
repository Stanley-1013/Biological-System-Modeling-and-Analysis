#!/usr/bin/env python3
"""
Build the PART 2 talk deck: "HIV Vaccination on the sIC AIDS Model".

Generates part2_HIV_vaccination.pptx (~15 slides) for a 15-minute in-class talk.
All numbers come from the report (report/part2.tex) and the qX_results.md files;
nothing is invented here.

Design direction: deep-navy / slate title family with three figure-matched accents
(baseline grey, vaccination teal-blue, condoms green). Strong title hierarchy, one
KEY MESSAGE line per content slide, large centred figures, <=4 short bullets,
thin accent rule + footer with slide number.

Run:  python3 build_slides.py
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.normpath(os.path.join(HERE, "..", "part2_hiv", "figures"))
OUT = os.path.join(HERE, "part2_HIV_vaccination.pptx")

# --------------------------------------------------------------------------- #
# Palette (deliberate, figure-matched). Consistent across every slide.
# --------------------------------------------------------------------------- #
NAVY      = RGBColor(0x14, 0x21, 0x3D)   # deep navy — titles / title slide bg
SLATE     = RGBColor(0x2B, 0x3A, 0x55)   # slate — secondary surfaces
INK       = RGBColor(0x1B, 0x26, 0x38)   # body text on light
MUTE       = RGBColor(0x6B, 0x76, 0x88)  # muted captions / footer
PAPER     = RGBColor(0xF6, 0xF7, 0xFA)   # near-white slide background
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
# accents matched to the figure curve colours
ACC_VAX   = RGBColor(0x1F, 0x7A, 0x8C)   # vaccination — teal-blue
ACC_COND  = RGBColor(0x2E, 0x8B, 0x57)   # condoms — green
ACC_BASE  = RGBColor(0x8A, 0x94, 0xA6)   # baseline — grey
ACCENT    = ACC_VAX                       # primary accent = vaccination teal

FONT = "Calibri"
FONT_H = "Calibri"  # heading family (kept consistent; Calibri available)

# Slide geometry (16:9)
SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.6)

TALK_TITLE = "HIV Vaccination on the sIC AIDS Model"

prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]

_slide_no = 0  # running counter for footer


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def _set_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _txt(slide, left, top, width, height, text, size, color, *,
         bold=False, italic=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, font=FONT, line_spacing=1.0):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font
    r.font.color.rgb = color
    return box


def _rule(slide, left, top, width, color=ACCENT, height=Pt(3)):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    bar.shadow.inherit = False
    return bar


def _footer(slide):
    """Thin footer: short talk title (left) + slide number (right)."""
    global _slide_no
    _slide_no += 1
    _txt(slide, MARGIN, SH - Inches(0.45), Inches(8), Inches(0.3),
         "sIC HIV vaccination  ·  李傳漢 B11611027  ·  BME5113",
         9, MUTE, font=FONT)
    _txt(slide, SW - Inches(1.6), SH - Inches(0.45), Inches(1.0), Inches(0.3),
         str(_slide_no), 11, MUTE, bold=True, align=PP_ALIGN.RIGHT, font=FONT)


def _content_header(slide, kicker, title):
    """Standard content-slide header: kicker label + big title + accent rule."""
    _txt(slide, MARGIN, Inches(0.42), Inches(11.5), Inches(0.32),
         kicker.upper(), 12, ACCENT, bold=True, font=FONT)
    _txt(slide, MARGIN, Inches(0.72), Inches(12.1), Inches(0.85),
         title, 32, NAVY, bold=True, font=FONT_H, line_spacing=0.98)
    _rule(slide, MARGIN, Inches(1.62), Inches(1.6))


def _key_message(slide, msg, top=Inches(1.78)):
    """One-line KEY MESSAGE band under the header."""
    box = _txt(slide, MARGIN, top, Inches(12.1), Inches(0.55),
               msg, 17, SLATE, italic=True, font=FONT, line_spacing=1.0)
    return box


def _bullets(slide, items, left, top, width, height, size=16,
             color=INK, gap_after=6):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, (txt, lvl, accent) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl
        p.space_after = Pt(gap_after)
        p.line_spacing = 1.05
        # bullet marker
        rb = p.add_run()
        rb.text = ("▸  " if lvl == 0 else "–  ")
        rb.font.size = Pt(size)
        rb.font.bold = True
        rb.font.name = FONT
        rb.font.color.rgb = accent if accent else ACCENT
        # text
        rt = p.add_run()
        rt.text = txt
        rt.font.size = Pt(size if lvl == 0 else size - 1)
        rt.font.name = FONT
        rt.font.color.rgb = color
    return box


def _fig(slide, name, left, top, max_w, max_h, align="center"):
    """Place a figure scaled to fit a box, preserving aspect (no crop)."""
    path = os.path.join(FIG, name)
    iw, ih = Image.open(path).size
    ar = iw / ih
    box_ar = max_w / max_h
    if ar >= box_ar:
        w = max_w
        h = int(max_w / ar)
    else:
        h = max_h
        w = int(max_h * ar)
    if align == "center":
        l = left + (max_w - w) // 2
    elif align == "right":
        l = left + (max_w - w)
    else:
        l = left
    t = top + (max_h - h) // 2
    slide.shapes.add_picture(path, l, t, width=w, height=h)
    return l, t, w, h


def _caption(slide, text, left, top, width):
    _txt(slide, left, top, width, Inches(0.3), text, 11, MUTE,
         italic=True, align=PP_ALIGN.CENTER, font=FONT)


def _note(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def new_content_slide(kicker, title, key_msg=None):
    s = prs.slides.add_slide(BLANK)
    _set_bg(s, PAPER)
    _content_header(s, kicker, title)
    if key_msg:
        _key_message(s, key_msg)
    return s


# --------------------------------------------------------------------------- #
# Slide 1 — Title
# --------------------------------------------------------------------------- #
s = prs.slides.add_slide(BLANK)
_set_bg(s, NAVY)
# accent block on left
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.28), SH)
band.fill.solid(); band.fill.fore_color.rgb = ACCENT
band.line.fill.background(); band.shadow.inherit = False

_txt(s, Inches(1.0), Inches(1.5), Inches(11), Inches(0.4),
     "BME5113 · BIOLOGICAL SYSTEM MODELING — TERM PROJECT, PART 2",
     13, RGBColor(0x9F, 0xB4, 0xCC), bold=True)
_txt(s, Inches(0.95), Inches(2.05), Inches(11.4), Inches(1.8),
     "HIV Vaccination on the\nsIC AIDS Model", 46, WHITE, bold=True,
     line_spacing=1.0)
_rule(s, Inches(1.0), Inches(4.05), Inches(2.4), ACCENT, height=Pt(4))
_txt(s, Inches(1.0), Inches(4.35), Inches(11), Inches(0.5),
     "Does a vaccine make the epidemic decline — at what cost, and versus condoms?",
     18, RGBColor(0xC7, 0xD3, 0xE2), italic=True)
_txt(s, Inches(1.0), Inches(5.7), Inches(11), Inches(0.9),
     "李傳漢  (Li Chuan-Han)", 22, WHITE, bold=True)
_txt(s, Inches(1.0), Inches(6.2), Inches(11), Inches(0.5),
     "B11611027   ·   simplified Imperial College (sIC) model, Haefner (2005) Ch. 15",
     14, RGBColor(0x9F, 0xB4, 0xCC))
_note(s, "Title. Part 2 of the term project: extend the sIC AIDS model with HIV "
         "vaccination and answer four questions — peak/decline, cost, optimum rate, "
         "vaccination vs condoms.")

# --------------------------------------------------------------------------- #
# Slide 2 — Motivation
# --------------------------------------------------------------------------- #
s = new_content_slide("Motivation", "Why model an HIV intervention?",
                      "A compartment model lets us ask: does a vaccine actually "
                      "turn the epidemic around — and is it worth it?")
_bullets(s, [
    ("HIV/AIDS is a long, sexually-transmitted epidemic — interventions play out "
     "over decades, so intuition alone is unreliable.", 0, ACCENT),
    ("A model turns vague policy questions into quantitative ones we can test on "
     "the same baseline.", 0, ACCENT),
    ("Four concrete questions drive Part 2:", 0, ACCENT),
    ("(a) does vaccination make the epidemic peak and decline?", 1, ACC_VAX),
    ("(b) what does it cost per infection averted?", 1, ACC_VAX),
    ("(c) what is the optimum vaccination rate?", 1, ACC_VAX),
    ("(d) how does vaccination compare with condom promotion?", 1, ACC_COND),
], MARGIN, Inches(2.5), Inches(12.0), Inches(4.2), size=18)
_note(s, "Motivation: HIV is a decades-long STI epidemic; intuition is unreliable, "
         "so we use a model. Four questions: peak/decline, cost, optimum rate, "
         "vaccination vs condoms — all tested against one common baseline.")

# --------------------------------------------------------------------------- #
# Slide 3 — The sIC model (12 compartments)
# --------------------------------------------------------------------------- #
s = new_content_slide("The model", "The sIC model: 12 compartments",
                      "Three disease states × two sexes × two age classes; "
                      "transmission is frequency-dependent on I/(S+I).")
# compartment schematic via boxes
def comp_box(slide, left, top, w, h, label, fill, txtcolor=WHITE, fsize=13):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
    b.fill.solid(); b.fill.fore_color.rgb = fill
    b.line.color.rgb = WHITE; b.line.width = Pt(1.2)
    b.shadow.inherit = False
    tf = b.text_frame; tf.word_wrap = True
    tf.margin_left = Pt(2); tf.margin_right = Pt(2)
    tf.margin_top = Pt(1); tf.margin_bottom = Pt(1)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.size = Pt(fsize); r.font.bold = True
    r.font.color.rgb = txtcolor; r.font.name = FONT
    return b

bx0 = Inches(0.75); by0 = Inches(2.55)
cw = Inches(1.15); ch = Inches(0.62); gx = Inches(0.18); gy = Inches(0.22)
states = [("S", ACC_BASE), ("I", ACC_VAX), ("A", SLATE)]
rows = [("Female", "f"), ("Male", "m")]
# header row for age classes
_txt(s, bx0 + cw + gx, by0 - Inches(0.34), Inches(2.5), Inches(0.3),
     "age 1 (0–15, pre-sexual)     age 2 (16+, sexually active)", 11, MUTE,
     bold=True)
for ri, (sexname, sx) in enumerate(rows):
    ry = by0 + ri * (3 * (ch + Inches(0.04)) + Inches(0.18))
    for si, (st, col) in enumerate(states):
        ty = ry + si * (ch + Inches(0.05))
        _txt(s, bx0 - Inches(0.02), ty, cw, ch, f"{sexname} {st}", 11, INK,
             bold=True, anchor=MSO_ANCHOR.MIDDLE)
        comp_box(s, bx0 + cw + gx, ty, cw, ch, f"{st}{sx},1", col)
        comp_box(s, bx0 + 2 * cw + 2 * gx, ty, cw, ch, f"{st}{sx},2", col)

# right column explanatory bullets
_bullets(s, [
    ("S → I → A: susceptible, HIV+ (pre-AIDS), clinical AIDS.", 0, ACCENT),
    ("Only age-2 (16+) individuals transmit.", 0, ACCENT),
    ("Forrester-style flow model: births, ageing (ξ), progression (γ), "
     "AIDS death (α).", 0, ACCENT),
    ("Frequency-dependent force of infection λ ∝ I/(S+I): what matters is the "
     "fraction of partners infectious — A excluded (not sexually active).", 0,
     ACC_VAX),
], Inches(5.6), Inches(2.5), Inches(7.2), Inches(4.2), size=15)
_note(s, "12 compartments: S/I/A disease states crossed with sex (f/m) and two age "
         "classes. Only age-2 transmit. Force of infection is frequency-dependent, "
         "I/(S+I); clinical-AIDS individuals are excluded from the partner pool.")

# --------------------------------------------------------------------------- #
# Slide 4 — Key parameters + demography
# --------------------------------------------------------------------------- #
s = new_content_slide("Parameters", "Key parameters (Table 15.2) & demography",
                      "Asymmetric transmission (male→female 2.7× higher) is why "
                      "women reach higher prevalence than men.")
# parameter table
from pptx.util import Cm
rows_tbl = [
    ("Symbol", "Meaning", "Value"),
    ("c", "new-partner acquisition rate", "2.35 / yr"),
    ("β(m→f)", "male→female transmission prob.", "0.20"),
    ("β(f→m)", "female→male transmission prob.", "0.075"),
    ("μ", "natural death rate", "0.0227 / yr"),
    ("α", "extra AIDS death rate", "1.0 / yr"),
    ("ξ", "ageing rate (age1→age2)", "0.0667 / yr"),
    ("ϑ", "perinatal transmission prob.", "0.35"),
    ("θ", "female fecundity", "0.2088 / yr"),
]
nrows, ncols = len(rows_tbl), 3
tbl_w = Inches(7.0); tbl_h = Inches(4.1)
tshape = s.shapes.add_table(nrows, ncols, MARGIN, Inches(2.55), tbl_w, tbl_h)
table = tshape.table
table.columns[0].width = Inches(1.5)
table.columns[1].width = Inches(4.0)
table.columns[2].width = Inches(1.5)
for ci in range(ncols):
    pass
for ri, row in enumerate(rows_tbl):
    for ci, val in enumerate(row):
        cell = table.cell(ri, ci)
        cell.margin_left = Pt(6); cell.margin_right = Pt(6)
        cell.margin_top = Pt(2); cell.margin_bottom = Pt(2)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 1 else PP_ALIGN.CENTER
        r = p.add_run(); r.text = val
        r.font.name = FONT
        if ri == 0:
            r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = WHITE
            cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
        else:
            r.font.size = Pt(12.5); r.font.color.rgb = INK
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 else RGBColor(0xEC, 0xEF, 0xF4)

_bullets(s, [
    ("Demography matters: births come only from age-2 females; high fertility "
     "grows the population early on.", 0, ACCENT),
    ("Perinatal route (ϑ = 0.35): infected mothers can bear infected newborns — "
     "a route a vaccine does NOT block.", 0, ACC_VAX),
    ("Initial pop. N(0) = 8005 (S split 3000/1000 per sex×age).", 0, ACCENT),
], Inches(8.1), Inches(2.6), Inches(4.6), Inches(4.0), size=15)
_note(s, "Parameters from Table 15.2. Transmission is asymmetric: β male→female "
         "0.20 vs female→male 0.075 (~2.7×), which makes female prevalence exceed "
         "male. Demography: births from age-2 females, perinatal transmission "
         "ϑ=0.35 is a route vaccination can't block.")

# --------------------------------------------------------------------------- #
# Slide 5 — Modeling judgment 1: gamma
# --------------------------------------------------------------------------- #
s = new_content_slide("Modeling judgment 1", "γ recalibration: making the epidemic ignite",
                      "Table γ = 1.16 gives R₀ < 1 (no epidemic). I use the "
                      "biologically grounded γ = 0.1 → R₀ ≈ 2.35.")
_bullets(s, [
    ("R₀ = c·√(β_mf·β_fm)/(μ+γ).", 0, ACCENT),
    ("Table value γ = 1.16/yr ⇒ mean HIV→AIDS ≈ 0.85 yr (< 1 yr) and R₀ ≈ 0.24 "
     "< 1 — the seeded infection dies out.", 0, ACC_BASE),
    ("That contradicts the textbook's own Fig. 15.5 (HIV persists) and its stated "
     "1–10 yr progression.", 0, ACC_BASE),
    ("I adopt γ = 0.1/yr ⇒ mean infectious ≈ 8.1 yr (in range), R₀ ≈ 2.35 > 1.", 0,
     ACC_VAX),
    ("Herd-immunity threshold: p_c = 1 − 1/R₀ ≈ 0.574.", 0, ACC_VAX),
], MARGIN, Inches(2.45), Inches(6.2), Inches(4.3), size=15.5)
_fig(s, "verify_baseline_prevalence.png", Inches(7.0), Inches(2.35),
     Inches(5.9), Inches(4.2))
_caption(s, "Baseline (γ = 0.1): HIV persists; female > male prevalence.",
         Inches(7.0), Inches(6.55), Inches(5.9))
_note(s, "Modeling judgment 1: the literal Table γ=1.16 gives R0≈0.24<1, so no "
         "epidemic — contradicting Fig 15.5. I switch to γ=0.1 (mean ~10yr, in the "
         "textbook's stated range), giving R0≈2.35 and herd-immunity threshold "
         "p_c≈0.574. Stated honestly because it changes results.")

# --------------------------------------------------------------------------- #
# Slide 6 — Modeling judgment 2 / validation
# --------------------------------------------------------------------------- #
s = new_content_slide("Modeling judgment 2 + validation",
                      "Seed in I, not A — then validate vs Fig. 15.5",
                      "Seeding AIDS males can't transmit (A excluded); seeding "
                      "infectious males reproduces the endemic epidemic.")
_bullets(s, [
    ("Table seeds A_{m2}=5, but A is excluded from λ — those males die without "
     "infecting anyone (incidence exactly 0).", 0, ACC_BASE),
    ("Smallest fix: seed I_{m2}=5 (infectious males) instead.", 0, ACC_VAX),
    ("Baseline then reproduces Fig 15.5a: female ≈ 0.77, male ≈ 0.61 prevalence.", 0,
     ACCENT),
    ("Condom scenario (halve both β): R₀ → 1.17, just above threshold — prevalence "
     "collapses (near-threshold sensitivity).", 0, ACC_COND),
], MARGIN, Inches(2.45), Inches(6.3), Inches(4.3), size=15)
_fig(s, "verify_condom_prevalence.png", Inches(7.1), Inches(2.35),
     Inches(5.8), Inches(4.2))
_caption(s, "Condom scenario: R₀ ≈ 1.17, prevalence near-threshold sensitive.",
         Inches(7.1), Inches(6.55), Inches(5.8))
_note(s, "Modeling judgment 2: literal A-only seed can't ignite because A is "
         "excluded from the force of infection, so I seed I_m2=5. Baseline then "
         "matches Fig 15.5a (female>male). Condoms halve β → R0≈1.17, just above "
         "threshold; prevalence collapses in this sensitive regime.")

# --------------------------------------------------------------------------- #
# Slide 7 — The vaccination extension
# --------------------------------------------------------------------------- #
s = new_content_slide("The extension", "Adding vaccination: P compartments",
                      "Take-with-waning vaccine; protected stay in the partner "
                      "pool → genuine herd immunity.")
_bullets(s, [
    ("Two protected compartments P_{f2}, P_{m2} (age-2 only).", 0, ACC_VAX),
    ("Vaccinate at ν = 0.65/yr; protection wanes back to S at l = 0.1/yr "
     "(S → P → S).", 0, ACC_VAX),
    ("Take (all-or-nothing) vaccine: in P, no force of infection acts.", 0, ACC_VAX),
    ("Waning ceiling: P/(S+P) → ν/(ν+l) = 0.65/0.75 ≈ 0.87 — at most ~87% "
     "protected at any instant.", 0, ACCENT),
    ("Cost accumulator: dV/dt = ν(S_{f2}+S_{m2}), cost = $10 × V.", 0, ACCENT),
    ("Key convention: protected people are uninfected but still partners, so they "
     "stay in the denominator λ ∝ I/(S+I+P) — this dilution IS herd immunity.", 0,
     ACC_COND),
], MARGIN, Inches(2.45), Inches(12.1), Inches(4.4), size=16)
_note(s, "Vaccination extension: protected compartments P_f2, P_m2; vaccinate at "
         "ν=0.65, wane at l=0.1 (S→P→S). Take-with-waning. Waning ceiling "
         "ν/(ν+l)≈0.87. Cost = $10 per vaccination event. Crucial convention: P "
         "stays in the partner-pool denominator I/(S+I+P) — that dilution is herd "
         "immunity.")

# --------------------------------------------------------------------------- #
# Slide 8 — Q(a) peak & decline
# --------------------------------------------------------------------------- #
s = new_content_slide("Q(a) — Peak & decline",
                      "Vaccination: the epidemic never ignites",
                      "R_eff ≈ 0.31 < 1 — incidence falls monotonically from the "
                      "seed; the baseline peaks at ~791/yr near year 48.")
_fig(s, "qa_incidence.png", MARGIN, Inches(2.45), Inches(7.7), Inches(4.4),
     align="left")
_caption(s, "Incidence: vaccine vs baseline.", MARGIN, Inches(6.85), Inches(7.7))
_bullets(s, [
    ("R_eff ≈ R₀(1 − 0.867) ≈ 0.31 < 1.", 0, ACC_VAX),
    ("Vaccine incidence is highest at t=0 (the 5 seed males), then declines to ~0.", 0,
     ACC_VAX),
    ("Baseline: peak 791 new/yr @ 47.8 yr, stays high.", 0, ACC_BASE),
    ("Protected fraction saturates ≈ 0.85 (just below 0.867 ceiling).", 0, ACCENT),
], Inches(8.5), Inches(2.55), Inches(4.3), Inches(4.0), size=15)
_note(s, "Q(a): at ν=0.65 the protected fraction (0.87) exceeds p_c (0.574), so "
         "R_eff≈0.31<1 and the epidemic never ignites. Incidence peaks at t=0 (seed) "
         "then declines monotonically. Baseline peaks ~791/yr at ~48 yr. Stronger "
         "than just 'peak and decline'.")

# --------------------------------------------------------------------------- #
# Slide 9 — Q(b) cost
# --------------------------------------------------------------------------- #
s = new_content_slide("Q(b) — Cost",
                      "Cost-effectiveness improves sharply over time",
                      "~$162k at 30 yr ≈ $102 per infection averted — within the "
                      "published Garnett/Stover range.")
_fig(s, "qb_cost.png", MARGIN, Inches(2.4), Inches(5.3), Inches(4.5),
     align="left")
# small cost table
rows_tbl = [
    ("Horizon", "Cost", "$/infection averted"),
    ("20 yr", "$113,738", "$372"),
    ("30 yr", "$162,165", "$102"),
    ("50 yr", "$247,461", "$18"),
]
tshape = s.shapes.add_table(len(rows_tbl), 3, Inches(6.4), Inches(2.7),
                            Inches(6.3), Inches(2.0))
table = tshape.table
table.columns[0].width = Inches(1.9)
table.columns[1].width = Inches(2.1)
table.columns[2].width = Inches(2.3)
for ri, row in enumerate(rows_tbl):
    for ci, val in enumerate(row):
        cell = table.cell(ri, ci)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Pt(6); cell.margin_top = Pt(2); cell.margin_bottom = Pt(2)
        p = cell.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = val; r.font.name = FONT
        if ri == 0:
            r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = WHITE
            cell.fill.solid(); cell.fill.fore_color.rgb = ACC_VAX
        else:
            r.font.size = Pt(14); r.font.color.rgb = INK
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 else RGBColor(0xEC, 0xEF, 0xF4)
_bullets(s, [
    ("Most cost is up-front (vaccinate the standing susceptible pool).", 0, ACCENT),
    ("After saturation: steady ~407 vax/yr ≈ $4,070/yr recurring.", 0, ACCENT),
    ("Transferable metric is $/infection averted, not the headline total "
     "(small synthetic population).", 0, ACC_VAX),
], Inches(6.4), Inches(4.95), Inches(6.3), Inches(1.9), size=14.5)
_caption(s, "Cumulative cost / vaccinations and infections averted.",
         MARGIN, Inches(6.95), Inches(5.3))
_note(s, "Q(b): cost grows ~linearly — $114k/$162k/$247k at 20/30/50 yr. Cost per "
         "infection averted falls from $372 (20yr) to $102 (30yr) to $18 (50yr) as "
         "the baseline epidemic accelerates. $102 is within the Stover/Garnett "
         "$110-390 band. Use $/infection averted, not absolute totals.")

# --------------------------------------------------------------------------- #
# Slide 10 — Q(c) optimum rate (threshold)
# --------------------------------------------------------------------------- #
s = new_content_slide("Q(c) — Optimum rate",
                      "A finite threshold ν_c exists",
                      "Theory ν_c = l·p_c/(1−p_c) ≈ 0.135 (lower bound); simulated "
                      "ν_c ≈ 0.37. The standard ν = 0.65 is safely above it.")
_fig(s, "qc_invasion_threshold.png", Inches(6.6), Inches(2.4), Inches(6.2),
     Inches(4.4), align="right")
_caption(s, "Invasion growth rate r(ν) crossing zero (R_eff = 1).",
         Inches(6.6), Inches(6.9), Inches(6.2))
_bullets(s, [
    ("Need the steady protected fraction ν/(ν+l) ≥ p_c.", 0, ACCENT),
    ("Closed form ν_c = l·p_c/(1−p_c) ≈ 0.135/yr — a lower bound (ignores "
     "perinatal route + mortality on P).", 0, ACC_VAX),
    ("Direct invasion test (r crosses 0): ν_c ≈ 0.366/yr.", 0, ACC_VAX),
    ("ν = 0.65 sits comfortably above ν_c → genuinely controls the epidemic.", 0,
     ACCENT),
    ("Caveat: if P is wrongly excluded from the pool, the threshold disappears — "
     "an artifact, not a real result.", 0, ACC_COND),
], MARGIN, Inches(2.45), Inches(6.1), Inches(4.4), size=14.5)
_note(s, "Q(c) threshold: requiring ν/(ν+l)≥p_c gives closed-form ν_c≈0.135 (a "
         "lower bound). Direct invasion simulation gives ν_c≈0.366. ν=0.65 is above "
         "it. Measured via R_eff/invasion, not (I+A)/N, because AIDS mortality "
         "shrinks the whole population. Excluding P from the pool spuriously erases "
         "the threshold.")

# --------------------------------------------------------------------------- #
# Slide 11 — Q(c) cost-effectiveness
# --------------------------------------------------------------------------- #
s = new_content_slide("Q(c) — Cost-effective rate",
                      "Two 'optima': epidemiological vs cost-effective",
                      "Infections averted saturate past ν_c — the cost-effective "
                      "knee is at ν ≈ 0.18, well below the standard 0.65.")
_fig(s, "qc_cost_effectiveness.png", MARGIN, Inches(2.45), Inches(7.6),
     Inches(4.4), align="left")
_caption(s, "Average & marginal cost per infection averted vs ν.",
         MARGIN, Inches(6.9), Inches(7.6))
_bullets(s, [
    ("Below ν_c each extra unit of ν averts many infections.", 0, ACCENT),
    ("Past ν_c, nearly all ~13,400 achievable infections are already averted.", 0,
     ACC_VAX),
    ("Diminishing-returns knee (99% of max): ν ≈ 0.175/yr, marginal ~$122 each.", 0,
     ACC_VAX),
    ("ν = 0.65 controls the epidemic but over-vaccinates relative to the knee.", 0,
     ACC_COND),
], Inches(8.4), Inches(2.55), Inches(4.4), Inches(4.0), size=15)
_note(s, "Q(c) cost-effective: infections averted saturate past ν_c. The knee — "
         "smallest ν capturing 99% of max aversion — is ν≈0.175, marginal ~$122 per "
         "infection. So the epidemiological optimum and the cost-effective optimum "
         "differ; ν=0.65 over-vaccinates relative to the knee but still works.")

# --------------------------------------------------------------------------- #
# Slide 12 — Q(d) vaccination vs condoms
# --------------------------------------------------------------------------- #
s = new_content_slide("Q(d) — Vaccination vs condoms",
                      "A near-tie on outcome; different cost basis",
                      "Both control the epidemic: vaccination R_eff 0.31 strictly "
                      "below 1; condoms R₀ 1.17 just above.")
_fig(s, "qd_strategy_comparison.png", MARGIN, Inches(2.45), Inches(6.5),
     Inches(4.0), align="left")
_fig(s, "qd_averted_and_reff.png", Inches(7.1), Inches(2.55), Inches(5.8),
     Inches(2.6), align="center")
_bullets(s, [
    ("Averted: vaccination 31,224 vs condoms 30,857 (of 31,235) — nearly identical.",
     0, ACCENT),
    ("Vaccination edges ahead: R_eff < 1 strictly (residual 11 vs 378 infections).",
     0, ACC_VAX),
    ("Cost basis differs: vaccine $348,618 explicit; condoms unpriced (≠ free).", 0,
     ACC_COND),
    ("Both verdicts are R₀-sensitive near threshold — honest near-tie.", 0, ACCENT),
], Inches(7.1), Inches(5.05), Inches(5.8), Inches(1.9), size=13.5)
_caption(s, "Prevalence trajectories (left); averted & R per strategy (right).",
         MARGIN, Inches(6.6), Inches(6.5))
_note(s, "Q(d): both strategies essentially control the epidemic. Vaccination drives "
         "R_eff=0.31<1 strictly; condoms put R0=1.17, just above threshold. "
         "Infections averted nearly identical (~31k each). Cost basis differs — "
         "vaccine $348k explicit, condoms unpriced (not free). Honest near-tie.")

# --------------------------------------------------------------------------- #
# Slide 13 — Key takeaways
# --------------------------------------------------------------------------- #
s = prs.slides.add_slide(BLANK)
_set_bg(s, NAVY)
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.28), SH)
band.fill.solid(); band.fill.fore_color.rgb = ACCENT
band.line.fill.background(); band.shadow.inherit = False
_txt(s, Inches(0.95), Inches(0.6), Inches(11), Inches(0.4),
     "TAKEAWAYS", 13, RGBColor(0x9F, 0xB4, 0xCC), bold=True)
_txt(s, Inches(0.92), Inches(0.95), Inches(11.6), Inches(0.9),
     "What the model says", 36, WHITE, bold=True)
_rule(s, Inches(0.95), Inches(1.85), Inches(2.2), ACCENT, height=Pt(4))
items = [
    ("Vaccination at ν = 0.65 controls the epidemic — R_eff ≈ 0.31 < 1, so it "
     "never ignites; prevalence stays near 0 vs the ~0.41 endemic plateau.",
     ACC_VAX),
    ("It is cost-effective: ~$102 per infection averted at 30 yr, within the "
     "published Garnett/Stover range.", ACC_VAX),
    ("A finite optimum exists: threshold ν_c ≈ 0.37; the cost-effective knee is "
     "~0.18 — the standard 0.65 over-vaccinates a little.", ACCENT),
    ("Vaccination ≈ condoms on outcome; vaccination strictly crosses the "
     "threshold, but the two aren't comparable on cost as priced.", ACC_COND),
]
box = s.shapes.add_textbox(Inches(0.95), Inches(2.35), Inches(11.7), Inches(4.6))
tf = box.text_frame; tf.word_wrap = True
for i, (txt, col) in enumerate(items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(14); p.line_spacing = 1.08
    rb = p.add_run(); rb.text = "●  "
    rb.font.size = Pt(18); rb.font.bold = True; rb.font.color.rgb = col
    rb.font.name = FONT
    rt = p.add_run(); rt.text = txt
    rt.font.size = Pt(18); rt.font.color.rgb = WHITE; rt.font.name = FONT
_note(s, "Takeaways: vaccination at ν=0.65 controls the epidemic (R_eff≈0.31), is "
         "cost-effective (~$102/infection averted at 30yr), has a finite optimum "
         "(ν_c≈0.37, knee ~0.18), and is roughly comparable to condoms but not "
         "directly cost-comparable as priced.")

# --------------------------------------------------------------------------- #
# Slide 14 — Limitations & honesty
# --------------------------------------------------------------------------- #
s = new_content_slide("Limitations & honesty",
                      "What these results rest on",
                      "Every conclusion is conditional on documented assumptions — "
                      "stated, not hidden.")
_bullets(s, [
    ("γ recalibration (1.16 → 0.1) was required for the epidemic to ignite at all; "
     "it shifts absolute levels.", 0, ACC_BASE),
    ("Near-threshold sensitivity: condoms leave R₀ ≈ 1.17, so small calibration "
     "changes move the endemic level a lot.", 0, ACC_BASE),
    ("Partner-pool convention (P in denominator) is load-bearing — it is what "
     "gives vaccination its herd-immunity effect.", 0, ACC_VAX),
    ("Small synthetic population (N₀ = 8005) → dollar totals are illustrative; "
     "use $/infection averted.", 0, ACCENT),
    ("Single operating point (ν = 0.65, l = 0.1); constant-rate ν simplifies the "
     "Garnett/Stover coverage scenario.", 0, ACCENT),
], MARGIN, Inches(2.45), Inches(12.1), Inches(4.3), size=16)
_note(s, "Limitations: γ recalibration was necessary but shifts levels; condom "
         "scenario sits near threshold (sensitive); the partner-pool convention is "
         "load-bearing; population is small/synthetic so use $/infection averted; "
         "single operating point. Conclusions are conditional on these documented "
         "assumptions.")

# --------------------------------------------------------------------------- #
# Slide 15 — Backup / Q&A
# --------------------------------------------------------------------------- #
s = prs.slides.add_slide(BLANK)
_set_bg(s, NAVY)
_txt(s, Inches(0.95), Inches(2.6), Inches(11.4), Inches(1.0),
     "Thank you — questions?", 40, WHITE, bold=True)
_rule(s, Inches(1.0), Inches(3.7), Inches(2.4), ACCENT, height=Pt(4))
_txt(s, Inches(1.0), Inches(4.0), Inches(11.4), Inches(1.6),
     "Backup: R₀ = c·√(β_mf·β_fm)/(μ+γ) = 2.35  ·  p_c = 1−1/R₀ = 0.574  ·  "
     "waning ceiling ν/(ν+l) = 0.87  ·  ν_c ≈ 0.37  ·  R_eff(ν=0.65) = 0.31",
     15, RGBColor(0xC7, 0xD3, 0xE2), line_spacing=1.3)
_txt(s, Inches(1.0), Inches(6.2), Inches(11), Inches(0.5),
     "李傳漢 · B11611027 · BME5113 · sIC HIV vaccination",
     13, RGBColor(0x9F, 0xB4, 0xCC))
_note(s, "Backup / Q&A slide. Key constants for fielding questions: R0=2.35, "
         "p_c=0.574, waning ceiling 0.87, ν_c≈0.37, R_eff(0.65)=0.31.")

# --------------------------------------------------------------------------- #
prs.save(OUT)
print(f"Saved {OUT} with {len(prs.slides._sldIdLst)} slides.")
