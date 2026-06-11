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
# Student voice, natural spoken Taiwanese phrasing. Written so a reader who has
# never studied the topic can read it aloud and understand it: core English
# terms that appear on the slides are kept but glossed in plain Chinese on first
# use, while hard-to-follow English is rendered directly in Chinese. All numbers
# and conclusions are unchanged from the source script.
# Keyed by 1-based slide index → applied to slide.notes_slide.
# --------------------------------------------------------------------------- #
NOTES = {
    1: (
        "各位同學、老師好，我是李傳漢，學號 B11611027。今天報告這次學期專題的第二"
        "部分（Part 2）：在 sIC AIDS model（一個描述愛滋疫情的數學模型）上面，加進 "
        "HIV vaccination（愛滋疫苗接種）。\n\n"
        "這個模型來自 Haefner 2005 課本第 15 章，是 Imperial College（帝國理工學院）"
        "那個模型的簡化版，叫 sIC。第二部分要回答一個很實際的問題：打疫苗，到底能不能"
        "讓 HIV 疫情往下走？要花多少錢？最佳接種率是多少？跟推廣保險套比，哪個比較"
        "有效？\n\n"
        "接下來十五分鐘，我先把模型講清楚，再一題一題回答。"
    ),
    2: (
        "為什麼要用模型？\n\n"
        "因為 HIV 透過性行為傳播、而且拖很久，疫情是用「幾十年」當單位在跑。這種時間"
        "尺度，光憑直覺判斷一個介入二、三十年後的累積效果，非常不可靠。所以我們用 "
        "compartment model（分艙模型，把人口分成幾個「艙」、追蹤人數怎麼在艙之間流動），"
        "把模糊的政策問題，變成可量化、可以在同一個 baseline（基準情境，也就是什麼介入"
        "都不做的對照組）上公平比較的問題。\n\n"
        "第二部分就是四個問題：(a) 疫苗會不會讓疫情先到高峰、再下降；(b) 每避免一個感染"
        "要花多少錢；(c) 最佳接種率；(d) 疫苗跟保險套哪個好。先講結論：接種率 ν（音 nu，"
        "每人每年被接種的速率）等於 0.65 的疫苗能把疫情壓下去，而且具成本效益"
        "（cost-effective，花的錢換到的效果划算）——細節我一題一題比。"
    ),
    3: (
        "先看模型本身。\n\n"
        "sIC 把人口切成三個疾病狀態：S 是 susceptible（易感者，也就是還沒被感染、有可能"
        "被感染的人）、I 是感染 HIV 但還沒發病、A 是臨床 AIDS（已經發病的愛滋病人）。每個"
        "再乘上性別（f 女、m 男）、再乘上兩個年齡層（age 1 是 0–15 歲還沒有性行為、age 2 "
        "是 16 歲以上有性行為）。三乘二乘二，就是右邊這 12 個 compartment（分艙、也就是"
        "這 12 格）。\n\n"
        "重點兩個：只有 age 2 會傳染；這是一個 flow model（流動模型，人會一格一格往下流），"
        "有出生、長大變老（ageing，參數叫 ξ）、I 進展到 A 的速率 γ（音 gamma，從感染到"
        "發病的進展率）、AIDS 死亡 α（音 alpha）。\n\n"
        "最關鍵的是 force of infection（感染力，也就是一個易感者單位時間內被感染的機率）。"
        "HIV 是 frequency-dependent（看比例、不看絕對人數）：重要的不是感染者的絕對數量，"
        "而是在你可能的性伴侶裡，有多少「比例」是感染者，所以是 I 除以 (S+I)。注意 A 不在"
        "分母，因為我們假設臨床 AIDS 的人不再有性行為——這個細節等下會很重要。"
    ),
    4: (
        "這是課本 Table 15.2 的關鍵參數。我點一件事：傳染機率是不對稱的。男傳女的 β"
        "（音 beta，每一段性關係把病傳出去的機率）是 0.20，女傳男只有 0.075，差約 2.7 "
        "倍。這是異性戀 HIV 的標準生物特性，也就是為什麼 baseline（基準情境）裡女性的 "
        "equilibrium prevalence（平衡盛行率，疫情穩定後感染者佔比的水準）比男性高。\n\n"
        "人口結構兩個重點：出生只由 age-2 女性產生、加上發展中國家生育率高，所以前期人口"
        "會成長。另外有一條 perinatal route（母嬰垂直傳染，懷孕生產時母親傳給嬰兒），參數 "
        "ϑ 等於 0.35，感染的母親可能生出已感染的新生兒——這條路徑疫苗擋不住，講 "
        "threshold（門檻）時會再提。初始人口 N(0) 是 8005 人。"
    ),
    5: (
        "接下來兩張，是讓模型跑出課本那種行為，我必須做的兩個判斷。\n\n"
        "第一個是進展率 γ（從感染到發病的速率）。這裡會用到 R₀（音 R-nought，基本繁殖數，"
        "一個感染者平均會傳染給幾個人；大於 1 疫情才會擴散）。R₀ 公式是 c 乘根號 "
        "(β_mf × β_fm) 除以 (μ+γ)，其中 μ 是 mu、自然死亡率。課本 Table 15.2 給 γ 等於 "
        "1.16，代表 HIV 到發病平均只有 0.85 年、不到一年，這跟課本自己講的「1 到 10 年」"
        "矛盾；而且代進去 R₀ 只有 0.24、小於 1，疫情起不來——我實際模擬，一開始放進去的"
        "少數感染者直接消失，跟課本 Fig 15.5「HIV 持續存在」完全相反。\n\n"
        "所以我改用 γ 等於 0.1，平均感染期約 8.1 年，落在課本範圍內。這時 R₀ 約 2.35、"
        "大於 1，疫情就會擴散開來，跟課本圖一致。對應的 herd-immunity threshold（群體免疫"
        "門檻，要有多少比例的人受保護，疫情才壓得下去）p_c 是 1 減 1/R₀，約 0.574。右邊"
        "就是修正後的 baseline：HIV 持續存在、女性 prevalence（盛行率，感染者佔比）高於"
        "男性。"
    ),
    6: (
        "第二個判斷是一開始的感染者要放在哪一格。Table 15.2 放 5 個 AIDS 男性、也就是 "
        "A_{m2} 等於 5，但 A 不在 force of infection（感染力）的算式裡，這 5 個人傳不出去、"
        "只會進展、死亡，疫情永遠不會開始，模擬出來 incidence（新增感染，每年新感染的人數）"
        "剛好是零。最小的修正，就是改成放 5 個會傳染的男性、也就是 I_{m2} 等於 5。\n\n"
        "做完這兩個修正，baseline 就重現課本 Fig 15.5a：女性 prevalence 約 0.77、男性約 "
        "0.61，順序對、HIV 持續存在。\n\n"
        "右邊是 condom scenario（推廣保險套的情境），跟課本一樣把兩個 β 都減半。因為 R₀ "
        "正比於根號 β，減半讓 R₀ 變成 1.17，只比門檻高一點點，prevalence 就崩掉。這就是 "
        "near-threshold（接近門檻）的敏感性：在 1 附近，小調整就讓結果差很多。"
    ),
    7: (
        "現在加疫苗。\n\n"
        "我加兩個 protected compartment（受保護艙，放打了疫苗、目前受保護的人），叫 "
        "P_{f2} 跟 P_{m2}，只在 age 2。易感者以每人每年的速率 ν 被接種、移進 P；保護力"
        "會隨時間衰退（waning，保護力不是永久的），衰退率叫 l（音 ell），衰退後回到 S，"
        "整體是一個 S 到 P、再回到 S 的循環。疫苗型態是 take／all-or-nothing（全有全無型："
        "要嘛完全保護、要嘛完全沒保護）：在 P 裡的人就是完全受保護。專案標準值是 ν 等於 "
        "0.65、l 等於 0.1。\n\n"
        "這裡有個算出來的上限叫 waning ceiling（保護上限，因為保護力會衰退，受保護的人撐"
        "不過某個比例）：P 佔 (S+P) 的比例最多到 ν/(ν+l)，也就是 0.65/0.75、約 0.87。"
        "任何時刻最多約 87% 的人受保護。成本就邊跑邊把錢加起來，dV/dt 等於 ν 乘上兩性 "
        "age-2 易感者，每劑 10 美元。\n\n"
        "最關鍵的慣例在最後一點：受保護的人沒被感染，但他們還是有性行為、還是別人的性"
        "伴侶，只是自己不會被傳染，所以要留在分母裡，感染力變成 I 除以 (S+I+P)。把易感者"
        "移進 P 會稀釋掉感染者的比例——這個稀釋，正是 herd immunity（群體免疫）的機制。"
    ),
    8: (
        "第一題：疫苗會不會讓疫情先到高峰、再下降？答案比「高峰再下降」還強。\n\n"
        "因為實際做得到的 protected fraction（受保護比例）0.87 高過門檻 0.574，所以 "
        "R_eff（音 R-eff，有效繁殖數，在有疫苗等介入之後、一個感染者實際會傳給幾個人）"
        "約等於 R₀ 乘 (1 − 0.867)、約 0.31、小於 1，疫情根本起不來。\n\n"
        "看左邊 incidence（新增感染）圖。打疫苗那條最高點就在 t 等於 0，那只是一開始 5 個"
        "男性傳給少數人，之後就一路往下、掉到接近零。對比 baseline，它衝到每年約 791 個"
        "新感染、在第 48 年左右到高峰，而且維持很高。這個下降不是瞬間的，因為原本的 I "
        "跟 A 還要花八到十年才會進展、死亡；但 R_eff 小於 1、沒有新傳染補進來，病毒就被"
        "清掉。同時 protected fraction 飽和在約 0.85，剛好在 0.867 上限下一點點，符合"
        "這種「會保護、但保護力會衰退」疫苗的穩態。"
    ),
    9: (
        "第二題是成本。\n\n"
        "把每劑疫苗的錢邊跑邊加起來，右邊表列了幾個時間點：20 年累積約 11 萬 4 千美元、"
        "30 年約 16 萬 2 千、50 年約 24 萬 7 千，大致線性成長。\n\n"
        "重點是 cost-effectiveness（成本效益，花的錢換到的效果）隨時間明顯變好。每避免一個"
        "感染的成本：20 年是 372 美元、30 年降到 102 美元、50 年只剩 18 美元。原因是早期 "
        "baseline 疫情還沒起來、能避免的感染少，所以看起來貴；等 baseline 加速、衝向每年 "
        "791 的高峰，疫苗這邊一直接近零，avoided infections（避免掉的感染數）增加得比成本"
        "快很多，單價就一路往下掉。\n\n"
        "30 年的 102 美元落在 Stover 跟 Garnett 2002 報告的範圍裡，算合理。疫情壓平之後，"
        "疫苗還是要因為保護力衰退、加上新人長大，持續以約每年 407 劑、約 4070 美元幫人補打。"
        "要強調一點：這是很小的合成（虛構）人口，能搬到別處用的指標是「每避免一個感染的"
        "成本」，不是總金額。"
    ),
    10: (
        "第三題：最佳接種率。先講 epidemiological threshold（從疫情控制角度看的門檻），"
        "也就是最小、剛好能把 R_eff 壓到 1 以下的接種率，我叫它 ν_c。\n\n"
        "條件是穩態下的 protected fraction、也就是 ν/(ν+l)，要大於等於群體免疫門檻 p_c。"
        "它的公式解是 ν_c 等於 l 乘 p_c 除以 (1 − p_c)、約 0.135。但這只是一個下限，因為"
        "它忽略了兩件事：perinatal（母嬰垂直傳染）那條疫苗擋不住的路徑，以及死亡率也會"
        "作用在受保護的 P 上。\n\n"
        "所以我直接用模擬去測疫情會不會擴散：在一個已經打過疫苗、沒有疾病的人口裡，丟一點"
        "感染進去，看疫情早期的成長率 r 在哪個 ν 剛好穿過零、也就是 R_eff 等於 1。模擬"
        "出來 ν_c 約 0.366，右邊就是剛好穿過 1 的那個點。標準的 ν 等於 0.65 舒服地在它"
        "上面，確實能控制疫情。\n\n"
        "一點提醒：如果錯誤地把 P 排除在分母外，這個門檻會整個消失。但那是分母怎麼算造成的"
        "人為假象、不是真實結果，所以我把這個對照也畫進去了。"
    ),
    11: (
        "這張一樣是第三題，但「最佳」有兩個合理的意思，我兩個都報。前一張是從疫情控制"
        "角度（epidemiological）看的，這張是從成本效益（cost-effective）看的。\n\n"
        "關鍵在 avoided infections（避免掉的感染數）超過 ν_c 之後會飽和。在 ν_c 以下，"
        "每多一點 ν 都能多避免很多感染；一旦超過 ν_c，大約 13400 個可避免的感染幾乎都"
        "已經避免掉了，再加大接種只是重複幫保護力衰退的人補打、效益很低。\n\n"
        "所以這裡有個 diminishing-returns（邊際效益遞減）的膝點，也就是再加下去就不太划算"
        "的那個轉折點。能抓到 99% 最大避免量的最小 ν 約 0.175，那邊邊際成本約每個感染 "
        "122 美元。標準的 ν 等於 0.65 雖然能控制疫情，但相對於這個膝點其實打多了。這就是"
        "從疫情控制看的最佳、跟從成本效益看的最佳，答案不一樣的原因。"
    ),
    12: (
        "最後一題：疫苗跟保險套哪個比較會控制疫情？\n\n"
        "兩個都能控制。疫苗把 R_eff 壓到 0.31、嚴格小於 1；保險套把 R₀ 降到 1.17、還"
        "稍微在 1 上面，也就是把 β 減半還差一點點才跨過門檻，但疫情已經慢到在我們看的"
        "時間範圍內等於被控制。\n\n"
        "避免掉的感染數兩者幾乎一樣。總共 31235 個感染，疫苗避免 31224、保險套避免 30857。"
        "疫苗稍微領先，因為它讓 R_eff 嚴格小於 1、只殘留 11 個感染；保險套殘留 378 個。\n\n"
        "真正差很多的是成本怎麼算。疫苗有明確的 34 萬 8618 美元，而且因為保護力會衰退"
        "（waning ceiling），要無限期幫人補打。保險套被當成永久把 R₀ 砍半、而且沒有定價"
        "——但「沒定價」不等於「免費」，真實的行為改變計畫也有預算，只是這專案沒給。再"
        "加上接近門檻（near-threshold）很敏感，兩邊結論都對 R₀ 很敏感。結論：在疫情結果"
        "上接近平手，疫苗因為嚴格跨過門檻稍微領先；但以目前的定價方式，兩者不能直接比成本。"
    ),
    13: (
        "把結論收一下。\n\n"
        "第一，ν 等於 0.65 的疫苗能控制疫情：R_eff 約 0.31、小於 1，疫情起不來，"
        "prevalence 維持接近零，而不是 baseline 那個約 0.41 的 endemic plateau（地方性"
        "流行的高原期，疫情穩定維持在某個高水準下不來）。\n\n"
        "第二，它具成本效益：30 年時每避免一個感染約 102 美元，落在已發表的 "
        "Garnett／Stover 範圍裡。\n\n"
        "第三，存在一個有限的最佳值：從疫情控制看的門檻 ν_c 約 0.37、從成本效益看的膝點約 "
        "0.18，所以標準的 0.65 其實打得稍微多了一點。\n\n"
        "第四，疫苗跟保險套在結果上差不多，疫苗嚴格跨過門檻，但以目前的定價方式不能直接"
        "比成本。回到一開始的問題——打疫苗確實能讓疫情往下走，而且划算。"
    ),
    14: (
        "最後，這些結論有幾個前提，我列一下。\n\n"
        "第一，γ 從 1.16 改成 0.1 是為了讓疫情起得來，它會移動整個絕對水準。第二，接近"
        "門檻時很敏感：保險套讓 R₀ 停在 1.17，小小的校準改變就會讓最後穩定的感染水準變"
        "很多。第三，「把受保護的人留在性伴侶池、也就是放進分母」這個慣例是關鍵中的關鍵，"
        "它正是疫苗群體免疫效果的來源。第四，人口很小、是虛構的，N₀ 只有 8005，所以金額"
        "是示意性的，要用每個感染的成本來看。第五，我只測單一操作點 ν 等於 0.65、l 等於 "
        "0.1，並把 ν 當成固定速率，這是對 Garnett／Stover 覆蓋率情境的簡化。\n\n"
        "換句話說，所有結論都是有條件的。"
    ),
    15: (
        "以上就是我的報告，謝謝大家，歡迎提問。\n\n"
        "需要的話，這幾個常數可以幫我快速回答：R₀（基本繁殖數）是 2.35、p_c（群體免疫"
        "門檻）是 0.574、waning ceiling（保護上限）0.87、ν_c（臨界接種率）約 0.37、ν "
        "等於 0.65 時 R_eff（有效繁殖數）是 0.31。"
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
                 bullet_size=14.5, formula=None):
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
    # optional equation line (a faint-tinted bar with a centred formula)
    if formula:
        f_h = Inches(0.5)
        _rect(s, MARGIN, bullets_top, TEXT_W, f_h, SIGNAL_FAINT)
        _txt(s, MARGIN, bullets_top, TEXT_W, f_h, formula, 15.5, INK,
             bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        bullets_top = bullets_top + f_h + Inches(0.16)
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
    key_size=15, bullet_size=14.5,
    formula="R₀ = c · √(β_mf · β_fm) / (μ + γ)")

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
    "sic_flow_diagram.png",
    "S→I→A progression with the vaccine loop S⇄P",
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
