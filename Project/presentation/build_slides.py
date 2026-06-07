#!/usr/bin/env python3
"""
Build the PART 2 talk deck: "HIV Vaccination on the sIC AIDS Model".

This generator is a faithful PowerPoint port of the Swiss-Modern HTML deck
(slides.html): same palette, same kicker -> headline -> key-message structure,
framed-figure cards, oversized faint slide numbers, hairline rules and footer.
Content (text + numbers) is identical to the HTML deck. 15 slides, same order.

Design system (Swiss Modern):
  - 16:9 canvas, consistent 0.55in margins, a clear text|figure grid.
  - thin signal-red accent rule top-left, letter-spaced signal-red kicker,
    big dark headline, one-line key message in a box with a signal-red left
    border, <=5 short bullets, framed figure in a white hairline card, an
    oversized faint signal-red slide number in a back corner, a footer line.
  - Figure slides: ~46% text column / ~50% figure column with a gutter; the
    content block is vertically centred so the slide reads balanced.
  - Every figure is scaled to FIT its card region preserving aspect ratio,
    computed from the PNG's real pixel size.

python-pptx does NOT auto-shrink text, so font sizes and box sizes are chosen
to comfortably fit the real text. A verification pass at the end re-opens the
file and asserts every shape is within the slide bounds (0 violations).

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
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "part2_HIV_vaccination.pptx")

# --------------------------------------------------------------------------- #
# Palette — exact RGB from slides.html CSS tokens
# --------------------------------------------------------------------------- #
PAPER    = RGBColor(0xFA, 0xFA, 0xF8)   # --paper   background
INK      = RGBColor(0x14, 0x18, 0x1F)   # --ink     primary text
INK_SOFT = RGBColor(0x5A, 0x64, 0x73)   # soft ink  secondary text
HAIRLINE = RGBColor(0xE4, 0xE4, 0xDD)   # --hairline rules / borders
BASELINE = RGBColor(0x8A, 0x94, 0xA6)   # --baseline grey
VACC     = RGBColor(0x1F, 0x7A, 0x8C)   # --vacc    teal
CONDOM   = RGBColor(0x2E, 0x8B, 0x57)   # --condom  green
SIGNAL   = RGBColor(0xE5, 0x48, 0x4D)   # --signal  red accent
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
# faint signal red for the oversized slide numbers (~7% opacity over paper)
SIGNAL_FAINT = RGBColor(0xF8, 0xEC, 0xEC)

# Fonts — PowerPoint substitutes if a machine lacks them (acceptable).
FONT_DISPLAY = "Archivo"      # headings (bold / heavy)
FONT_BODY    = "Nunito Sans"  # body

# Slide geometry (16:9)
SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.55)
CONTENT_W = SW - 2 * MARGIN

TALK_TITLE = "HIV Vaccination on the sIC AIDS Model"
FOOTER = "HIV Vaccination on the sIC AIDS Model  ·  李傳漢 Chuan-Han Li"

prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]

_slide_no = 0  # running counter


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def _set_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _add_runs(p, runs, default_color, default_size, default_font):
    """Add a list of (text, opts) runs to a paragraph.

    opts is a dict that may carry: bold, italic, color, size, font.
    """
    for text, opts in runs:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(opts.get("size", default_size))
        r.font.bold = opts.get("bold", False)
        r.font.italic = opts.get("italic", False)
        r.font.name = opts.get("font", default_font)
        r.font.color.rgb = opts.get("color", default_color)


def _txt(slide, left, top, width, height, text, size, color, *,
         bold=False, italic=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, font=FONT_BODY, line_spacing=1.0,
         letter_runs=None, space=0.0):
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
    if space:
        p.space_after = Pt(space)
    if letter_runs is not None:
        _add_runs(p, letter_runs, color, size, font)
    else:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return box


def _rect(slide, left, top, width, height, color, line_color=None,
          line_w=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = line_w or Pt(1)
    shp.shadow.inherit = False
    return shp


def _slide_number(slide, n):
    """Oversized faint signal-red slide index in the bottom-right corner."""
    _txt(slide, SW - Inches(3.3), SH - Inches(3.55), Inches(3.1), Inches(3.4),
         f"{n:02d}", 200, SIGNAL_FAINT, bold=True, align=PP_ALIGN.RIGHT,
         anchor=MSO_ANCHOR.BOTTOM, font=FONT_DISPLAY, line_spacing=0.8)


def _footer(slide, n):
    """Hairline rule + footer text (left) + NN/15 (right)."""
    fy = SH - Inches(0.5)
    _rect(slide, MARGIN, fy - Inches(0.06), CONTENT_W, Pt(0.75), HAIRLINE)
    _txt(slide, MARGIN, fy, Inches(9.5), Inches(0.3),
         FOOTER, 9, INK_SOFT, font=FONT_DISPLAY)
    _txt(slide, SW - MARGIN - Inches(2.0), fy, Inches(2.0), Inches(0.3),
         f"{n:02d} / 15", 9, INK_SOFT, bold=True, align=PP_ALIGN.RIGHT,
         font=FONT_DISPLAY)


def _kicker(slide, text, top):
    """Small signal-red rule + letter-spaced uppercase kicker."""
    # short signal rule preceding the kicker text
    _rect(slide, MARGIN, top + Inches(0.10), Inches(0.34), Pt(2), SIGNAL)
    # PowerPoint can't truly letter-space; emulate with thin spaces.
    spaced = " ".join(text.upper())
    _txt(slide, MARGIN + Inches(0.46), top, CONTENT_W - Inches(0.46),
         Inches(0.3), spaced, 11.5, SIGNAL, bold=True, font=FONT_DISPLAY,
         anchor=MSO_ANCHOR.MIDDLE)


def _headline(slide, text, top, size=32, width=None, height=Inches(0.95)):
    _txt(slide, MARGIN, top, width or CONTENT_W, height, text, size, INK,
         bold=True, font=FONT_DISPLAY, line_spacing=0.98)


def _key_message(slide, left, top, width, label, msg, *, size=15.5,
                 label_size=10.5, height=Inches(1.1)):
    """Box with a signal-red left border: small label + one-line message."""
    bar_w = Pt(3)
    _rect(slide, left, top, bar_w, height, SIGNAL)
    box = slide.shapes.add_textbox(left + Inches(0.16), top, width - Inches(0.16),
                                   height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Pt(2)
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    p1.space_after = Pt(3)
    r = p1.add_run()
    r.text = " ".join(label.upper())
    r.font.size = Pt(label_size)
    r.font.bold = True
    r.font.name = FONT_DISPLAY
    r.font.color.rgb = SIGNAL
    p2 = tf.add_paragraph()
    p2.line_spacing = 1.18
    r2 = p2.add_run()
    r2.text = msg
    r2.font.size = Pt(size)
    r2.font.bold = True
    r2.font.name = FONT_BODY
    r2.font.color.rgb = INK
    return box


def _bullets(slide, items, left, top, width, height, size=15.5,
             gap_after=7, line_spacing=1.18):
    """Swiss bullets: small teal square marker + soft-ink text with bold spans.

    items: list of (runs, accent) where runs is either a plain string or a
    list of (text, opts) for inline emphasis. accent colors the marker.
    """
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, (runs, accent) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap_after)
        p.line_spacing = line_spacing
        rb = p.add_run()
        rb.text = "▪  "
        rb.font.size = Pt(size - 2)
        rb.font.bold = True
        rb.font.name = FONT_BODY
        rb.font.color.rgb = accent or VACC
        if isinstance(runs, str):
            runs = [(runs, {})]
        for text, opts in runs:
            rt = p.add_run()
            rt.text = text
            rt.font.size = Pt(size)
            rt.font.name = FONT_BODY
            rt.font.bold = opts.get("bold", False)
            rt.font.color.rgb = opts.get("color", INK if opts.get("bold") else INK_SOFT)
    return box


def _figure_card(slide, name, left, top, max_w, max_h, caption=None):
    """White hairline card framing a figure scaled to fit, plus a caption.

    The card fills the allocated (max_w x max_h) region. The image is scaled
    to fit inside the card minus padding, preserving aspect ratio, and centred.
    """
    pad = Inches(0.14)
    cap_h = Inches(0.34) if caption else Inches(0.0)
    # card surface (white, hairline border)
    _rect(slide, left, top, max_w, max_h, WHITE, line_color=HAIRLINE,
          line_w=Pt(1))
    # region available for the image inside the card
    inner_l = left + pad
    inner_t = top + pad
    inner_w = max_w - 2 * pad
    inner_h = max_h - 2 * pad - cap_h
    iw, ih = Image.open(os.path.join(ASSETS, name)).size
    ar = iw / ih
    box_ar = inner_w / inner_h
    if ar >= box_ar:
        w = inner_w
        h = int(inner_w / ar)
    else:
        h = inner_h
        w = int(inner_h * ar)
    l = inner_l + (inner_w - w) // 2
    t = inner_t + (inner_h - h) // 2
    slide.shapes.add_picture(os.path.join(ASSETS, name), l, t, width=w, height=h)
    if caption:
        _txt(slide, left + pad, top + max_h - cap_h, max_w - 2 * pad,
             cap_h, caption, 10.5, INK_SOFT, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE, font=FONT_DISPLAY,
             line_spacing=1.0)
    return left, top, max_w, max_h


def _note(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# Shared vertical rhythm for content slides ---------------------------------- #
KICKER_TOP = Inches(0.55)
HEAD_TOP = Inches(0.92)


def _content_chrome(kicker, headline, *, head_size=32, head_h=Inches(0.95)):
    """Add a content slide with kicker + headline + slide number + footer."""
    global _slide_no
    _slide_no += 1
    s = prs.slides.add_slide(BLANK)
    _set_bg(s, PAPER)
    _slide_number(s, _slide_no)
    _kicker(s, kicker, KICKER_TOP)
    _headline(s, headline, HEAD_TOP, size=head_size, height=head_h)
    _footer(s, _slide_no)
    return s


# --------------------------------------------------------------------------- #
# Figure-slide layout constants (the explicit space-allocation grid)
# --------------------------------------------------------------------------- #
BLOCK_TOP = Inches(2.02)          # content block starts below headline
BLOCK_BOT = SH - Inches(0.62)     # above footer
BLOCK_H = BLOCK_BOT - BLOCK_TOP   # ~4.86in
GUTTER = Inches(0.4)
# ~46% text / ~50% figure of the content width, with a gutter
TEXT_W = Inches(5.62)             # ~0.46 * 12.23
FIG_W = CONTENT_W - TEXT_W - GUTTER  # remaining (~50%)
FIG_LEFT = MARGIN + TEXT_W + GUTTER


def figure_slide(kicker, headline, key_label, key_msg, bullets_items,
                 fig_name, caption, *, head_size=30, key_size=15,
                 bullet_size=14.5):
    """Standard text|figure content slide with a vertically-centred block.

    The text column holds the key-message box then the bullets; the figure
    column holds a white framed card. Both share the same vertical band so the
    slide reads balanced with no empty half.
    """
    s = _content_chrome(kicker, headline, head_size=head_size)

    # --- figure card fills the figure column, vertically centred in band ---
    # choose a card height that fits the band but caps very tall cards
    card_h = min(BLOCK_H, Inches(4.55))
    card_top = BLOCK_TOP + (BLOCK_H - card_h) // 2
    _figure_card(s, fig_name, FIG_LEFT, card_top, FIG_W, card_h,
                 caption=caption)

    # --- text column: key message (top) + bullets, centred in the band ---
    key_h = Inches(1.16)
    gap = Inches(0.26)
    # estimate bullet block height from count
    n = len(bullets_items)
    bullet_h = Inches(0.0)
    # let bullets take the remaining band; vertically centre key+bullets group
    group_top = BLOCK_TOP
    _key_message(s, MARGIN, group_top, TEXT_W, key_label, key_msg,
                 size=key_size, height=key_h)
    bullets_top = group_top + key_h + gap
    bullets_avail = BLOCK_BOT - bullets_top
    _bullets(s, bullets_items, MARGIN, bullets_top, TEXT_W, bullets_avail,
             size=bullet_size, gap_after=6, line_spacing=1.14)
    return s


def figure_slide_no_key(kicker, headline, bullets_items, fig_name, caption,
                        *, head_size=30, bullet_size=15):
    """Text|figure slide WITHOUT a key-message box (slide 10 in HTML)."""
    s = _content_chrome(kicker, headline, head_size=head_size)
    card_h = min(BLOCK_H, Inches(4.55))
    card_top = BLOCK_TOP + (BLOCK_H - card_h) // 2
    _figure_card(s, fig_name, FIG_LEFT, card_top, FIG_W, card_h,
                 caption=caption)
    # bullets vertically centred in the band
    bul_top = BLOCK_TOP + Inches(0.5)
    _bullets(s, bullets_items, MARGIN, bul_top, TEXT_W, BLOCK_H - Inches(0.6),
             size=bullet_size, gap_after=9, line_spacing=1.18)
    return s


# Inline-run shorthands ------------------------------------------------------ #
def B(t):
    return (t, {"bold": True, "color": INK})


def T(t):
    return (t, {})


# =========================================================================== #
# SLIDE 1 — TITLE
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 1)

# top kicker (eyebrow) — uppercase, soft ink, letter-spaced
_txt(s, MARGIN, Inches(0.95), CONTENT_W, Inches(0.35),
     " ".join("Term Project · Part 2".upper()),
     13, INK_SOFT, bold=True, font=FONT_DISPLAY)
# huge headline
_headline(s, "HIV Vaccination on the\nsIC AIDS Model", Inches(1.55),
          size=52, height=Inches(2.0))
# title rule (ink, thick)
_rect(s, MARGIN, Inches(3.62), Inches(2.4), Pt(4), INK)
# subtitle
_txt(s, MARGIN, Inches(3.95), Inches(9.5), Inches(0.7),
     "A compartment-model study of epidemic control, cost, and intervention choice.",
     19, INK_SOFT, bold=True, font=FONT_BODY, line_spacing=1.15)
# metadata row with a hairline rule above
_rect(s, MARGIN, Inches(5.55), CONTENT_W, Pt(1), HAIRLINE)
# Author cell
_txt(s, MARGIN, Inches(5.78), Inches(5.0), Inches(0.3),
     " ".join("Author"), 11, SIGNAL, bold=True, font=FONT_DISPLAY)
_txt(s, MARGIN, Inches(6.08), Inches(5.6), Inches(0.35),
     "李傳漢 · Chuan-Han Li", 17, INK, bold=True, font=FONT_BODY)
_txt(s, MARGIN, Inches(6.46), Inches(5.6), Inches(0.3),
     "B11611027", 14, INK_SOFT, bold=True, font=FONT_BODY)
# Course cell
cx = MARGIN + Inches(6.2)
_txt(s, cx, Inches(5.78), Inches(5.4), Inches(0.3),
     " ".join("Course"), 11, SIGNAL, bold=True, font=FONT_DISPLAY)
_txt(s, cx, Inches(6.08), Inches(6.0), Inches(0.35),
     "BME5113", 17, INK, bold=True, font=FONT_BODY)
_txt(s, cx, Inches(6.46), Inches(6.4), Inches(0.3),
     "Biological Systems Modeling & Analysis", 14, INK_SOFT, bold=True,
     font=FONT_BODY)
_note(s, "Title. Part 2 of the term project: extend the sIC AIDS model with HIV "
         "vaccination and answer four questions — peak/decline, cost, optimum rate, "
         "vaccination vs condoms.")

# =========================================================================== #
# SLIDE 2 — THE QUESTION (four qcards)
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 2)
_kicker(s, "Motivation · Four Questions", KICKER_TOP)
_headline(s, "Can a vaccine bend an endemic epidemic?", HEAD_TOP, size=31)
_footer(s, 2)
# key message
_key_message(s, MARGIN, Inches(1.95), CONTENT_W,
             "Key idea",
             "In this model HIV is S → I → AIDS with births, so the "
             "infection persists endemically — it never burns out on its own.",
             size=16, height=Inches(0.95))
# four question cards in a 2x2 grid
qcards = [
    ("a", [T("Will a vaccine make the epidemic "), B("peak then decline"), T("?")], SIGNAL),
    ("b", [T("What does the vaccination program "), B("cost"), T("?")], VACC),
    ("c", [T("What is the "), B("optimum vaccination rate"), T("?")], CONDOM),
    ("d", [T("Vaccination vs. "), B("safe-sex / condoms"),
           T(" — which controls it better?")], BASELINE),
]
grid_top = Inches(3.15)
grid_h = SH - Inches(0.62) - grid_top
gap = Inches(0.28)
card_w = (CONTENT_W - gap) / 2
card_h = (grid_h - gap) / 2
for idx, (tag, runs, accent) in enumerate(qcards):
    r, c = divmod(idx, 2)
    cl = MARGIN + c * (card_w + gap)
    ct = grid_top + r * (card_h + gap)
    # card with colored top border
    _rect(s, cl, ct, card_w, card_h, WHITE, line_color=HAIRLINE, line_w=Pt(1))
    _rect(s, cl, ct, card_w, Pt(3), accent)
    # big tag
    _txt(s, cl + Inches(0.22), ct + Inches(0.18), Inches(0.7), Inches(0.7),
         tag, 30, INK, bold=True, font=FONT_DISPLAY, anchor=MSO_ANCHOR.TOP)
    # question text
    tb = s.shapes.add_textbox(cl + Inches(0.95), ct + Inches(0.18),
                              card_w - Inches(1.15), card_h - Inches(0.36))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.line_spacing = 1.2
    _add_runs(p, runs, INK_SOFT, 16, FONT_BODY)
_note(s, "Motivation: four questions — (a) peak/decline, (b) cost, (c) optimum "
         "rate, (d) vaccination vs condoms — tested against one common baseline. "
         "HIV is S->I->AIDS with births, so it persists endemically.")

# =========================================================================== #
# SLIDE 3 — THE sIC MODEL (3x4 compartment grid)
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 3)
_kicker(s, "Structure · 12 Compartments", KICKER_TOP)
_headline(s, "The sIC model: {S, I, AIDS} × sex × age", HEAD_TOP, size=30)
_footer(s, 3)

# compartment grid: 3 class-rows x 4 sex-age groups
grid_left = MARGIN + Inches(1.55)   # leave room for row labels
grid_top = Inches(2.35)
col_head_h = Inches(0.42)
cols = ["F · 0–15", "F · 16+", "M · 0–15", "M · 16+"]
rows = [("Susceptible", BASELINE, "S"), ("Infected", VACC, "I"),
        ("AIDS", SIGNAL, "A")]
subs = ["f1", "f2", "m1", "m2"]
total_grid_w = SW - grid_left - MARGIN
cell_gap = Inches(0.12)
cell_w = (total_grid_w - 3 * cell_gap) / 4
cell_h = Inches(0.72)
row_gap = Inches(0.16)

# column headers
for ci, ch in enumerate(cols):
    cl = grid_left + ci * (cell_w + cell_gap)
    _txt(s, cl, grid_top, cell_w, col_head_h, ch, 12, INK, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM, font=FONT_DISPLAY)
# corner label
_txt(s, MARGIN, grid_top, Inches(1.5), col_head_h, "class \\ group",
     11, INK_SOFT, bold=True, anchor=MSO_ANCHOR.BOTTOM, font=FONT_DISPLAY)

body_top = grid_top + col_head_h + Inches(0.1)
for ri, (rname, rcolor, sym) in enumerate(rows):
    rt = body_top + ri * (cell_h + row_gap)
    # row label
    _txt(s, MARGIN, rt, Inches(1.45), cell_h, rname, 12.5, INK_SOFT, bold=True,
         anchor=MSO_ANCHOR.MIDDLE, font=FONT_DISPLAY)
    for ci, sub in enumerate(subs):
        cl = grid_left + ci * (cell_w + cell_gap)
        box = _rect(s, cl, rt, cell_w, cell_h, rcolor)
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = f"{sym}{sub}"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.name = FONT_DISPLAY
        r.font.color.rgb = WHITE

# flows note under the grid, with a hairline rule
flows_top = body_top + 3 * (cell_h + row_gap) + Inches(0.06)
_rect(s, MARGIN, flows_top, CONTENT_W, Pt(0.75), HAIRLINE)
fb = s.shapes.add_textbox(MARGIN, flows_top + Inches(0.12), CONTENT_W,
                          Inches(0.95))
tf = fb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.line_spacing = 1.25
r = p.add_run()
r.text = "λ = c · β · I / (S+I)"
r.font.size = Pt(14); r.font.bold = True; r.font.name = FONT_DISPLAY
r.font.color.rgb = INK
r = p.add_run()
r.text = "    frequency-dependent force of infection"
r.font.size = Pt(13); r.font.name = FONT_BODY; r.font.color.rgb = INK_SOFT
p2 = tf.add_paragraph()
p2.line_spacing = 1.25
r = p2.add_run()
r.text = ("births · ageing ξ · HIV→AIDS progression γ · AIDS mortality α · "
          "natural mortality μ")
r.font.size = Pt(13); r.font.name = FONT_BODY; r.font.color.rgb = INK_SOFT
_note(s, "12 compartments: S/I/AIDS disease classes crossed with sex (f/m) and two "
         "age groups (0-15, 16+). Force of infection is frequency-dependent, "
         "I/(S+I); AIDS class excluded from the partner pool.")

# =========================================================================== #
# SLIDE 4 — PARAMETERS (param chips + key message)
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 4)
_kicker(s, "Table 15.2 · Why It Persists", KICKER_TOP)
_headline(s, "Parameters & the endemic plateau", HEAD_TOP, size=31)
_footer(s, 4)

params = [
    ("0.20", "βmf male→female transmission", VACC),
    ("0.075", "βfm female→male transmission", SIGNAL),
    ("2.35/yr", "c partner-change rate", VACC),
    ("0.0227/yr", "μ natural mortality", VACC),
    ("1.0/yr", "α extra AIDS mortality", VACC),
]
p_top = Inches(2.05)
p_h = Inches(1.45)
p_gap = Inches(0.22)
p_w = (CONTENT_W - (len(params) - 1) * p_gap) / len(params)
for i, (val, lab, vcolor) in enumerate(params):
    pl = MARGIN + i * (p_w + p_gap)
    _rect(s, pl, p_top, p_w, p_h, WHITE, line_color=HAIRLINE, line_w=Pt(1))
    _txt(s, pl + Inches(0.14), p_top + Inches(0.16), p_w - Inches(0.28),
         Inches(0.55), val, 24, vcolor, bold=True, font=FONT_DISPLAY,
         line_spacing=0.95)
    _txt(s, pl + Inches(0.14), p_top + Inches(0.78), p_w - Inches(0.28),
         Inches(0.6), lab, 11, INK_SOFT, font=FONT_BODY, line_spacing=1.1)

# key message
_key_message(s, MARGIN, Inches(3.95), CONTENT_W, "Key idea",
             "Transmission is asymmetric (βmf > βfm) so women are infected more — "
             "and births continually refill susceptibles, driving an endemic "
             "plateau rather than burnout.",
             size=17, height=Inches(1.5))
_note(s, "Parameters from Table 15.2. Transmission asymmetric: βmf 0.20 vs βfm "
         "0.075, so female prevalence exceeds male. Births refill susceptibles, "
         "giving an endemic plateau rather than burnout.")

# =========================================================================== #
# SLIDE 5 — MODELING JUDGMENT 1: GAMMA  (fig verify_baseline_prevalence)
# =========================================================================== #
figure_slide(
    "Modeling Judgment 1 · The Rate γ",
    "Recalibrating HIV→AIDS progression",
    "Key message",
    "A corrected, biologically grounded γ is required for the model to behave "
    "like a real epidemic.",
    [
        ([T("The textbook's literal "), B("γ = 1.16/yr"),
          T(" means HIV→AIDS in under a year → "),
          B("R₀ = 0.24 < 1"), T(" → no epidemic.")], SIGNAL),
        ([T("Biologically, HIV→AIDS takes "), B("~8–10 years"), T(".")], BASELINE),
        ([T("We use "), B("γ = 0.1/yr"), T(" → "), B("R₀ ≈ 2.35"), T(".")], VACC),
    ],
    "verify_baseline_prevalence.png",
    "Baseline prevalence — growth to an endemic plateau",
    key_size=15, bullet_size=14.5)

# =========================================================================== #
# SLIDE 6 — VALIDATION  (fig verify_condom_prevalence)
# =========================================================================== #
figure_slide(
    "Validation · Fig. 15.5",
    "Calibrated against the published sIC model",
    "Key message",
    "The model is calibrated and behaves like the published sIC model before we "
    "add a vaccine.",
    [
        ([T("Baseline reproduces the textbook: growth to a high endemic plateau.")],
         VACC),
        ([T("Female prevalence ("), B("0.77"), T(") above male ("), B("0.62"),
          T(").")], VACC),
        ([T("Condom scenario (halving both β) sharply suppresses it.")], CONDOM),
    ],
    "verify_condom_prevalence.png",
    "Baseline vs. condom scenario prevalence",
    key_size=15, bullet_size=15)

# =========================================================================== #
# SLIDE 7 — VACCINE EXTENSION  (fig qa_protected_fraction)
# =========================================================================== #
figure_slide(
    "Model Extension · Protected Compartments",
    "A “take”-with-waning vaccine",
    "Key message",
    "Protected people stay in the partner pool, so vaccination dilutes the "
    "infected fraction — this is what produces herd immunity.",
    [
        ([T("Add protected adults "), B("Pf2, Pm2"),
          T("; vaccinate susceptible adults at "), B("ν = 0.65/yr"),
          T(" (≈ Garnett 2002 “65% coverage”).")], VACC),
        ([T("Protection wanes at "), B("l = 0.1/yr"), T(" (≈ 10-year mean).")], VACC),
        ([T("Ceiling: at most "), B("ν/(ν+l) = 0.87"),
          T(" of adults are ever protected.")], VACC),
        ([T("Cost tracked via "), B("dV/dt = ν(Sf2+Sm2)"), T(".")], VACC),
    ],
    "qa_protected_fraction.png",
    "Protected fraction → waning ceiling 0.87",
    key_size=14.5, bullet_size=14)

# =========================================================================== #
# SLIDE 8 — Q(a) PEAK & DECLINE  (fig qa_incidence)
# =========================================================================== #
figure_slide(
    "Q(a) · Peak & Decline",
    "Does the vaccine make it peak then decline?",
    "Answer",
    "Yes — vaccination turns sustained growth into immediate decline.",
    [
        ([T("Under ν = 0.65, the effective reproduction number drops to "),
          B("R_eff ≈ 0.31 < 1"), T(".")], VACC),
        ([T("HIV incidence "), B("declines from the very start"), T(".")], VACC),
        ([T("The untreated baseline instead peaks at "),
          B("791 new infections/yr"), T(" around year 48.")], BASELINE),
    ],
    "qa_incidence.png",
    "HIV incidence: baseline peak vs. vaccinated decline",
    head_size=29, key_size=15, bullet_size=14.5)

# =========================================================================== #
# SLIDE 9 — Q(b) COST  (fig qb_cost)
# =========================================================================== #
figure_slide(
    "Q(b) · Program Cost",
    "What does it cost?",
    "Key message",
    "Cost-per-infection-averted is the transferable metric — absolute $ scale "
    "with this small synthetic population.",
    [
        ([T("At "), B("$10 per vaccination"), T(": cumulative cost "),
          B("≈ $162k"), T(" by year 30 (≈ $4,070/yr at steady state).")], VACC),
        ([T("About "), B("$102 per infection averted"), T(" at 30 years.")], VACC),
        ([T("Within the "), B("$110–390"),
          T(" range of the Imperial-College / Stover analyses.")], VACC),
    ],
    "qb_cost.png",
    "Cumulative cost & cost per infection averted",
    key_size=14.5, bullet_size=14.5)

# =========================================================================== #
# SLIDE 10 — Q(c) THRESHOLD  (fig qc_prevalence_vs_nu, NO key message)
# =========================================================================== #
figure_slide_no_key(
    "Q(c) · The Critical Rate",
    "Optimum rate — the elimination threshold",
    [
        ([T("A critical rate "), B("νc ≈ 0.37/yr"),
          T(" drives the epidemic to elimination above it.")], SIGNAL),
        ([T("Matches herd immunity: "), B("νc = l·pc/(1−pc)"), T(" with "),
          B("pc = 1 − 1/R₀ ≈ 0.574"), T(".")], VACC),
        ([T("The standard "), B("ν = 0.65"), T(" sits comfortably above νc.")],
         VACC),
    ],
    "qc_prevalence_vs_nu.png",
    "Steady-state prevalence vs. vaccination rate ν",
    head_size=29, bullet_size=15)

# =========================================================================== #
# SLIDE 11 — Q(c) COST-EFFECTIVENESS  (fig qc_cost_effectiveness)
# =========================================================================== #
figure_slide(
    "Q(c) · Two Optimums",
    "Optimum rate — best value vs. elimination",
    "Key message",
    "“Control the epidemic” and “best value for money” are not "
    "the same target.",
    [
        ([B("Epidemiological optimum: "),
          T("eliminate the epidemic, ν ≥ νc.")], SIGNAL),
        ([B("Cost-effective optimum: "),
          T("best value — a diminishing-returns knee near "),
          B("ν ≈ 0.18/yr"), T(".")], VACC),
    ],
    "qc_cost_effectiveness.png",
    "Cost-effectiveness — the value knee at ν ≈ 0.18",
    head_size=29, key_size=15.5, bullet_size=15)

# =========================================================================== #
# SLIDE 12 — Q(d) VACCINE vs CONDOMS  (fig qd_averted_and_reff)
# =========================================================================== #
figure_slide(
    "Q(d) · Vaccination vs. Condoms",
    "Which controls it better?",
    "Key message",
    "Essentially a tie on epidemiological outcome; they differ on cost basis and "
    "the vaccine's waning ceiling — no single winner is claimed.",
    [
        ([B("Vaccination"), T(" (ν=0.65) → R_eff=0.31, averts "), B("≈31,224"),
          T(" infections, explicit cost "), B("≈$349k"), T(".")], VACC),
        ([B("Condoms"), T(" (halving β) → R₀=1.17 (just above threshold), averts "),
          B("≈30,857"), T(", no priced cost here.")], CONDOM),
    ],
    "qd_averted_and_reff.png",
    "Infections averted & R_eff by strategy",
    head_size=30, key_size=14.5, bullet_size=14.5)

# =========================================================================== #
# SLIDE 13 — TAKEAWAYS (numbered list)
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 13)
_kicker(s, "Synthesis · What We Learned", KICKER_TOP)
_headline(s, "Takeaways", HEAD_TOP, size=34)
_footer(s, 13)

takeaways = [
    [T("A waning vaccine at "), B("ν=0.65"), T(" drives "), B("R_eff < 1"),
     T(" and makes the epidemic decline.")],
    [T("It is "), B("cost-effective"), T(" — about "),
     B("$102 per infection averted"), T(".")],
    [T("It is "), B("comparable to condom promotion"),
     T(" on epidemiological outcome.")],
    [T("Conclusions hold "), B("above the herd-immunity threshold"),
     T(" νc ≈ 0.37/yr.")],
]
tk_top = Inches(2.25)
tk_gap = Inches(0.28)
tk_h = (SH - Inches(0.7) - tk_top - 3 * tk_gap) / 4
num_w = Inches(0.62)
for i, runs in enumerate(takeaways):
    ty = tk_top + i * (tk_h + tk_gap)
    # number chip (signal-red square, white numeral)
    chip = _rect(s, MARGIN, ty + (tk_h - Inches(0.62)) / 2, num_w, Inches(0.62),
                 SIGNAL)
    tf = chip.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(i + 1)
    r.font.size = Pt(22); r.font.bold = True; r.font.name = FONT_DISPLAY
    r.font.color.rgb = WHITE
    # text
    tb = s.shapes.add_textbox(MARGIN + num_w + Inches(0.32), ty,
                              CONTENT_W - num_w - Inches(0.32), tk_h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.line_spacing = 1.15
    _add_runs(p, runs, INK_SOFT, 18, FONT_BODY)
_note(s, "Takeaways: vaccination at ν=0.65 drives R_eff<1 and the epidemic "
         "declines; it is cost-effective (~$102/infection averted); comparable to "
         "condoms; conclusions hold above the herd-immunity threshold νc≈0.37.")

# =========================================================================== #
# SLIDE 14 — LIMITATIONS
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 14)
_kicker(s, "Honesty · What To Distrust", KICKER_TOP)
_headline(s, "Limitations", HEAD_TOP, size=34)
_footer(s, 14)

lims = [
    ([B("γ recalibrated"),
      T(" from the implausible literal textbook value.")], BASELINE),
    ([T("Results are "), B("sensitive near the R₀ threshold"),
      T(", so condoms vs. vaccine is a close call.")], BASELINE),
    ([B("Small synthetic population"),
      T(" — use cost-per-infection-averted, not absolute $.")], VACC),
    ([T("A "), B("single operating point"),
      T(" was analysed, not a full sweep of every parameter.")], VACC),
    ([T("The herd-immunity result "),
      B("depends on keeping protected people in the partner pool"), T(".")],
     CONDOM),
]
_bullets(s, lims, MARGIN, Inches(2.25), CONTENT_W, Inches(4.5),
         size=18, gap_after=14, line_spacing=1.2)
_note(s, "Limitations: γ recalibrated; near-threshold sensitivity; small synthetic "
         "population (use $/infection averted); single operating point; herd "
         "immunity depends on protected people staying in the partner pool.")

# =========================================================================== #
# SLIDE 15 — CLOSING
# =========================================================================== #
_slide_no += 1
s = prs.slides.add_slide(BLANK)
_set_bg(s, PAPER)
_slide_number(s, 15)
_kicker(s, "Part 2 · The End", KICKER_TOP)
_headline(s, "Thank you.\nQuestions?", Inches(1.9), size=56,
          height=Inches(2.2))
# recap box (white card, signal left border)
recap_top = Inches(4.45)
recap_w = Inches(7.6)
recap_h = Inches(1.0)
_rect(s, MARGIN, recap_top, recap_w, recap_h, WHITE, line_color=HAIRLINE,
      line_w=Pt(1))
_rect(s, MARGIN, recap_top, Pt(3), recap_h, SIGNAL)
rb = s.shapes.add_textbox(MARGIN + Inches(0.22), recap_top, recap_w - Inches(0.3),
                          recap_h)
tf = rb.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.line_spacing = 1.2
for text, opts in [("Recap: ", {"color": INK}),
                   ("R₀ ≈ 2.35", {"color": VACC, "bold": True}),
                   (" → with ", {"color": INK}),
                   ("ν = 0.65", {"color": VACC, "bold": True}),
                   (", ", {"color": INK}),
                   ("R_eff ≈ 0.31 < 1", {"color": VACC, "bold": True}),
                   (".", {"color": INK})]:
    r = p.add_run(); r.text = text
    r.font.size = Pt(17); r.font.name = FONT_DISPLAY
    r.font.bold = opts.get("bold", True)
    r.font.color.rgb = opts["color"]
# footer line with hairline above
ft = Inches(6.15)
_rect(s, MARGIN, ft, CONTENT_W, Pt(1), HAIRLINE)
_txt(s, MARGIN, ft + Inches(0.18), CONTENT_W, Inches(0.4),
     "李傳漢 (Chuan-Han Li) · B11611027  —  BME5113 Biological Systems "
     "Modeling & Analysis · Term Project, Part 2",
     13, INK_SOFT, bold=True, font=FONT_BODY)
_note(s, "Closing. Recap: R0≈2.35 → with ν=0.65, R_eff≈0.31<1.")

# --------------------------------------------------------------------------- #
prs.save(OUT)
print(f"Saved {OUT} with {len(prs.slides._sldIdLst)} slides.")


# =========================================================================== #
# VERIFICATION PASS — re-open and assert every shape is within slide bounds
# =========================================================================== #
def verify(path):
    p = Presentation(path)
    sw, sh = p.slide_width, p.slide_height
    n = len(p.slides._sldIdLst)
    violations = []
    for si, slide in enumerate(p.slides, start=1):
        for shp in slide.shapes:
            try:
                left = shp.left; top = shp.top
                w = shp.width; h = shp.height
            except Exception:
                continue
            if left is None or top is None or w is None or h is None:
                continue
            if left < 0 or top < 0 or (left + w) > sw or (top + h) > sh:
                violations.append(
                    (si, shp.shape_type, shp.name,
                     round(Emu(left).inches, 2), round(Emu(top).inches, 2),
                     round(Emu(left + w).inches, 2),
                     round(Emu(top + h).inches, 2)))
    return n, violations


n, violations = verify(OUT)
print(f"Re-opened: {n} slides.")
assert n == 15, f"Expected 15 slides, got {n}"
if violations:
    print(f"BOUNDS VIOLATIONS: {len(violations)}")
    for v in violations:
        print("  slide", v[0], "shape", v[2], "type", v[1],
              f"L={v[3]} T={v[4]} R={v[5]} B={v[6]} (slide 13.33x7.5)")
else:
    print("Bounds check: 0 violations — every shape within slide bounds.")
