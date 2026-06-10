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

# --------------------------------------------------------------------------- #
# Speaker notes (備忘稿) — polished Traditional-Chinese script, one per slide.
# Student voice, natural spoken Taiwanese phrasing; English kept for technical
# terms and variables; all numbers unchanged from the source script.
# Keyed by 1-based slide index → applied to slide.notes_slide.
# --------------------------------------------------------------------------- #
NOTES = {
    1: (
        "各位同學、老師好，我是李傳漢，學號 B11611027。今天要報告的是 term project "
        "的 Part 2：在 sIC AIDS model 上面加入 HIV vaccination。\n\n"
        "這個 model 來自 Haefner 2005 課本第 15 章，它其實是 Imperial College model "
        "的簡化版，我們叫它 sIC。那整個 Part 2 想回答的，是一個很實際的問題：打疫苗到底"
        "能不能讓 HIV 疫情往下走？它要花多少錢？最佳的接種率又是多少？還有，跟推廣保險套"
        "比起來，到底哪一個比較有效？\n\n"
        "接下來這十五分鐘，我會先把 model 講清楚，再一題一題回答這四個問題。"
    ),
    2: (
        "先講一下為什麼要用 model。HIV 是一個透過性行為傳播、而且會拖很久的疫情，它的"
        "變化是用「幾十年」當單位在跑的。這種時間尺度，其實光靠直覺很不可靠 —— 你很難"
        "憑感覺去判斷一個介入措施在二、三十年後會累積出什麼效果。\n\n"
        "所以我們用 compartment model，把原本很模糊的政策問題，變成可以量化、而且可以"
        "在同一個 baseline 上面公平比較的問題。\n\n"
        "那 Part 2 具體就是四個問題：(a) 打疫苗會不會讓疫情先到高峰再下降；(b) 每避免"
        "一個感染要花多少錢；(c) 最佳接種率是多少；還有 (d) 疫苗跟保險套比起來怎麼樣。"
        "這四題我都會回到同一個 baseline 來比。"
    ),
    3: (
        "那先來看 model 本身。sIC 把人口切成 12 個 compartment：先是三個疾病狀態 —— "
        "S 是 susceptible 易感者、I 是感染了 HIV 但還沒發病、A 是臨床 AIDS；這三個再"
        "乘上性別，女 f、男 m，再乘上兩個年齡層 —— age 1 是 0 到 15 歲、還沒有性行為，"
        "age 2 是 16 歲以上、有性行為。所以三乘二乘二，剛好 12 格，就是右邊這張表。\n\n"
        "這裡有幾個重點：第一，只有 age 2 的人會傳染。第二，這是一個 Forrester 式的 "
        "flow model，裡面有出生、有 ageing 用 ξ、有 I 進展到 A 用 γ、還有 AIDS 死亡 α。\n\n"
        "那最關鍵的是 force of infection。HIV 是 frequency-dependent，也就是說，重要的"
        "不是感染者的「絕對數量」，而是在你可能的性伴侶裡面，有多大「比例」是感染者 —— "
        "所以是 I 除以 (S+I)。注意 A 不在分母裡面，因為臨床 AIDS 的人被假設不再有性行為。"
        "這個細節等一下會變得很重要。"
    ),
    4: (
        "這張是 Table 15.2 的關鍵參數。我想特別點出一件事：傳染機率是不對稱的。男傳女 "
        "β 是 0.20，女傳男只有 0.075，差不多 2.7 倍。這是異性戀 HIV 一個很標準的生物"
        "特性，也正是為什麼在 baseline 裡，女性的 equilibrium prevalence 會比男性高。\n\n"
        "人口結構這邊也有幾個要記得的點：出生只由 age-2 的女性產生，而且發展中國家生育率"
        "高，所以人口在前期是會成長的。另外還有一個 perinatal route，ϑ 等於 0.35，意思"
        "是感染的母親有機會生出已經感染的新生兒 —— 這條傳染路徑，疫苗是擋不住的，等一下"
        "講 threshold 的時候會再提到。初始人口 N(0) 是 8005 人。"
    ),
    5: (
        "接下來這兩張，是我為了讓 model 真的跑出課本描述的行為，必須做的兩個判斷。我選擇"
        "老實講出來，因為它們會影響結果。\n\n"
        "第一個是進展率 γ。R₀ 的公式是 c 乘上根號 (β_mf × β_fm)，再除以 (μ+γ)。課本 "
        "Table 15.2 給的 γ 是 1.16，但這代表從感染到發病平均只有 0.85 年、不到一年，這"
        "跟課本自己講的「1 到 10 年」是矛盾的。更糟的是，把 1.16 代進去，R₀ 大概只有 "
        "0.24，小於 1，疫情根本點不起來 —— 我實際去模擬，seed 進去的感染就直接消失了。"
        "這跟 Fig 15.5「HIV 持續存在」完全相反。\n\n"
        "所以我改用比較有生物根據的 γ 等於 0.1，平均感染期大概 8.1 年，落在課本說的範圍"
        "內，這時候 R₀ 大概是 2.35，大於 1，疫情就會 invade，跟課本的圖一致。對應的 "
        "herd-immunity threshold，也就是 p_c，是 1 減 1 除以 R₀，大約 0.574。右邊這"
        "張圖就是修正之後的 baseline：HIV 持續存在，而且女性 prevalence 高於男性。"
    ),
    6: (
        "第二個判斷是 seed 要放哪裡。Table 15.2 是放 5 個 AIDS 男性，A_{m2} 等於 5。"
        "但前面講過，A 不在 force of infection 裡面，所以這 5 個人根本傳不出去 —— 他們"
        "只會進展、死亡，疫情永遠不會開始，我模擬出來 incidence 剛好就是零。那最小的"
        "修正，就是改成 seed 5 個 infectious 男性，I_{m2} 等於 5。\n\n"
        "做了這兩個修正之後，baseline 就重現了 Fig 15.5a：女性 prevalence 大約 0.77，"
        "男性大約 0.61，順序對、而且 HIV 持續存在。\n\n"
        "右邊是 condom scenario，做法跟課本一樣，把兩個 β 都減半。因為 R₀ 正比於根號 "
        "β，減半剛好讓 R₀ 變成 1.17，只比 threshold 高一點點，所以 prevalence 會崩掉。"
        "這就是 near-threshold 的敏感性 —— 在 1 附近，小小的調整就會讓結果差很多。我"
        "選擇把這個 divergence 講出來，而不是去硬調參數。"
    ),
    7: (
        "現在來加上疫苗。我加了兩個 protected compartment，P_{f2} 跟 P_{m2}，只在 "
        "age 2。易感者會以 per-capita 速率 ν 被接種進 P，而保護力會以速率 l 衰退、回到 "
        "S，所以它是一個 S 到 P 再回到 S 的循環。\n\n"
        "疫苗型態我用的是 take，也就是 all-or-nothing：在 P 裡面的人完全受保護，force "
        "of infection 不會作用在他們身上。專案的標準值是 ν 等於 0.65、l 等於 0.1。\n\n"
        "那這裡有一個解析上的上限，叫 waning ceiling：P 佔 (S+P) 的比例，最多到 ν 除以 "
        "(ν+l)，也就是 0.65 除以 0.75，大約 0.87。所以就算你一直打，任何時刻最多也只有"
        "大約 87% 的人受保護。成本我用一個 accumulator 去累計，dV/dt 等於 ν 乘上兩性 "
        "age-2 的易感者，每劑算 10 美元。\n\n"
        "那最關鍵的一個慣例在最後一點：受保護的人雖然沒被感染，可是他們還是有性行為、"
        "還是合法的性伴侶，只是跟他們發生關係不會傳染。所以他們要留在分母裡面，force "
        "of infection 就變成 I 除以 (S+I+P)。把易感者移進 P 會稀釋掉感染者的比例 —— "
        "其實這個稀釋，正是 herd immunity 的機制。"
    ),
    8: (
        "那第一題：打疫苗會不會讓疫情先到高峰再下降？答案其實比「高峰再下降」還要更強。\n\n"
        "因為可達到的 protected fraction 0.87 高過 herd-immunity threshold 0.574，"
        "所以 R_eff 大概等於 R₀ 乘上 (1 − 0.867)，大約 0.31，小於 1。也就是說，疫情"
        "根本沒辦法 ignite。\n\n"
        "你看左邊這張 incidence 圖：打疫苗那一條，最高點就在 t 等於 0，那其實只是一開始 "
        "5 個 seed 男性傳給少數幾個人，之後就單調往下掉到接近零。對比 baseline，它衝到"
        "大約每年 791 個新感染、在第 48 年左右到高峰，而且維持得很高。那下降不是瞬間"
        "發生的，因為原本的 I 跟 A 還要花八到十年才會進展、死亡，但因為 R_eff 小於 1，"
        "沒有新的傳染去補充，病毒就被清掉了。同時 protected fraction 飽和在大約 0.85，"
        "剛好在 0.867 這個上限下面一點，符合 take-with-waning 的穩態。"
    ),
    9: (
        "第二題是成本。用剛剛那個 cost accumulator，右邊這張表列了幾個時間點。20 年"
        "累積花大約 11 萬 4 千美元，30 年大約 16 萬 2 千，50 年大約 24 萬 7 千 —— 大致"
        "上是線性成長。\n\n"
        "那重點是 cost-effectiveness 隨時間「明顯變好」。每避免一個感染的成本：20 年的"
        "時候是 372 美元，30 年降到 102 美元，50 年只剩 18 美元。原因是早期 baseline "
        "疫情還沒起來，能避免的感染很少，所以看起來貴；等到 baseline 加速衝向每年 791 "
        "的高峰，而疫苗這邊一直接近零，avoided infections 增加得比成本快很多，單價就"
        "一路往下掉。\n\n"
        "30 年的 102 美元，落在 Stover 跟 Garnett 2002 報告的範圍內，算合理。另外飽和"
        "之後，疫苗會因為保護力衰退、加上新人長大，持續以大約每年 407 劑、約 4070 美元"
        "的速率 re-vaccinate。我要強調一下，因為這是一個很小的合成人口，能搬到別處用的"
        "指標是「每避免一個感染的成本」，而不是總金額。"
    ),
    10: (
        "第三題：最佳接種率。先講 epidemiological threshold，也就是最小、能把 R_eff "
        "壓到 1 以下的 ν_c。\n\n"
        "條件是穩態 protected fraction、也就是 ν 除以 (ν+l)，要大於等於 p_c。解出來的"
        " closed form 是 ν_c 等於 l 乘上 p_c 除以 (1 − p_c)，大約 0.135。但這只是一個 "
        "lower bound，因為它忽略了兩件事：perinatal 那條疫苗擋不住的傳染路徑，還有 "
        "mortality 也會作用在 P 上面。\n\n"
        "所以我就直接用 invasion test 去量 —— 在打過疫苗的無病人口裡丟一點點感染，看"
        "早期成長率 r 在哪個 ν 穿過零、也就是 R_eff 等於 1。模擬出來的 ν_c 大約是 "
        "0.366，右邊這張圖就是那個 zero crossing。標準的 ν 等於 0.65 舒服地在它上面，"
        "所以確實能控制疫情。\n\n"
        "最後一點 caveat：如果錯誤地把 P 排除在分母外面，這個 threshold 會整個消失 —— "
        "但那是分母選擇造成的 artifact，不是真實的結果。所以我特別把這個對照也畫進去。"
    ),
    11: (
        "這張一樣是第三題，但「最佳」其實有兩個合理的意思，我兩個都報。前一張是 "
        "epidemiological 的；這一張是 cost-effective 的。\n\n"
        "關鍵在於：avoided infections 在超過 ν_c 之後會「飽和」。在 ν_c 以下，每多一點 "
        "ν 都能多避免很多感染；可是一旦超過 ν_c，大約 13400 個可避免的感染幾乎都已經被"
        "避免掉了，再加大接種，其實只是在重複幫衰退的人補打，效益很低。\n\n"
        "所以這裡有一個 diminishing-returns 的膝點 —— 能抓到 99% 最大避免量的最小 ν，"
        "大約在 0.175，那邊的邊際成本大約是每個感染 122 美元。標準的 ν 等於 0.65 雖然"
        "確實能控制疫情，但相對於這個 cost-effective 膝點，其實是「打多了」。這就是為什麼"
        " epidemiological 最佳跟 cost-effective 最佳，答案會不一樣。"
    ),
    12: (
        "最後一題：疫苗跟保險套，哪一個比較會控制疫情？\n\n"
        "其實兩個都能控制。疫苗把 R_eff 壓到 0.31，嚴格小於 1；保險套把 R₀ 降到 1.17，"
        "還是稍微在 1 上面 —— 也就是說，減半 β 在這個 R₀ 還差一點點才跨過 threshold，"
        "但疫情已經慢到在時間範圍內等於被控制住了。\n\n"
        "在 avoided infections 上面兩者幾乎一樣：總共 31235 個感染，疫苗避免 31224、"
        "保險套避免 30857。疫苗只是稍微領先，因為它讓 R_eff 嚴格小於 1，殘留 11 個感染，"
        "而保險套殘留 378 個。\n\n"
        "那真正差很多的是成本基礎，這也是為什麼我不願意硬選一個贏家。疫苗有明確的 34 萬 "
        "8618 美元，而且因為 waning ceiling，要無限期地幫衰退的人補打。保險套這邊是被"
        "當成永久把 R₀ 砍半、而且沒有定價 —— 但「沒定價」不等於「免費」，真實的行為改變"
        "計畫也有它自己的預算，只是專案沒給。再加上 near-threshold 的敏感性，兩邊的結論"
        "都對 R₀ 很敏感。所以老實的講法是：在疫情結果上是接近平手，疫苗因為嚴格跨過 "
        "threshold 稍微領先，但以目前的定價方式，兩者沒辦法直接比成本。"
    ),
    13: (
        "把結論收一下。\n\n"
        "第一，ν 等於 0.65 的疫苗能控制疫情：R_eff 大約 0.31、小於 1，疫情根本不會 "
        "ignite，prevalence 維持在接近零，而不是 baseline 那個大約 0.41 的 endemic "
        "plateau。\n\n"
        "第二，它具有成本效益：30 年的時候，每避免一個感染大約 102 美元，落在已發表的 "
        "Garnett/Stover 範圍內。\n\n"
        "第三，存在一個有限的最佳值：threshold ν_c 大約 0.37，而 cost-effective 膝點"
        "大約 0.18，所以標準的 0.65 其實打得稍微多了一點。\n\n"
        "第四，疫苗跟保險套在結果上差不多，疫苗嚴格跨過 threshold，但以目前的定價方式，"
        "兩者不能直接比成本。"
    ),
    14: (
        "最後我想老實交代一下，這些結論是建立在哪些假設上面。\n\n"
        "第一，γ 從 1.16 改成 0.1，是為了讓疫情能 ignite 才不得不做的，它會移動絕對"
        "水準。第二，near-threshold 敏感性：保險套讓 R₀ 停在 1.17，所以小小的校準改變"
        "就會讓 endemic level 變很多。第三，partner-pool 慣例 —— 把 P 放進分母 —— 是 "
        "load-bearing 的，它正是疫苗 herd-immunity 效果的來源。第四，人口很小、是合成"
        "的，N₀ 只有 8005，所以金額是示意性的，要用每個感染的成本來看。第五，我只測了"
        "單一操作點 ν 等於 0.65、l 等於 0.1，而且把 ν 當成常數速率，這是對 "
        "Garnett/Stover coverage 情境的簡化。\n\n"
        "換句話說，所有結論都是有條件的，而我選擇把這些條件講清楚，而不是把它藏起來。"
    ),
    15: (
        "以上就是我的報告，謝謝大家，也歡迎提問。\n\n"
        "如果需要的話，下面這幾個常數可以幫我快速回答問題：R₀ 是 2.35、p_c 是 0.574、"
        "waning ceiling 0.87、ν_c 大約 0.37、ν 等於 0.65 的時候 R_eff 是 0.31。"
    ),
}


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


def _note_for(slide, n):
    """Attach the polished Chinese speaker-notes for slide index n, if present."""
    if n in NOTES:
        slide.notes_slide.notes_text_frame.text = NOTES[n]


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
    _note_for(s, _slide_no)
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
_note_for(s, 1)

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
_note_for(s, 2)

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
_note_for(s, 3)

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
_note_for(s, 4)

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
_note_for(s, 13)

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
_note_for(s, 14)

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
_note_for(s, 15)

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
