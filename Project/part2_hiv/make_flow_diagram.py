"""Draw a clean compartment-flow schematic of the sIC model + vaccine extension.

Boxes: S (susceptible) -> I (infected) -> A (AIDS), plus the vaccine loop
S <-> P (protected). Arrows are labelled with the model rates so the diagram
can be pointed at while narrating the dynamics. Saved to both the Part-2
figures folder and the presentation assets folder.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# deck palette
PAPER = "#FAFAF8"
INK = "#14181F"
S_C = "#8A94A6"   # susceptible grey
I_C = "#1F7A8C"   # infected teal
A_C = "#E5484D"   # AIDS red
P_C = "#5B5BD6"   # protected indigo (distinct from teal)
SOFT = "#5A6473"

fig, ax = plt.subplots(figsize=(8.6, 4.9), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")

BW, BH = 1.7, 1.05          # box width / height


def box(cx, cy, letter, sub, color):
    """Filled rounded box centred at (cx, cy) with big letter + small sublabel."""
    ax.add_patch(FancyBboxPatch(
        (cx - BW / 2, cy - BH / 2), BW, BH,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=0, facecolor=color, zorder=2))
    ax.text(cx, cy + 0.12, letter, ha="center", va="center",
            color="white", fontsize=22, fontweight="bold", zorder=3)
    ax.text(cx, cy - 0.30, sub, ha="center", va="center",
            color="white", fontsize=8.5, zorder=3)


def arrow(x1, y1, x2, y2, color=INK, rad=0.0, lw=2.0):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=16, linewidth=lw,
        color=color, zorder=1))


def label(x, y, text, color=INK, size=12, weight="bold", style="normal"):
    ax.text(x, y, text, ha="center", va="center", color=color,
            fontsize=size, fontweight=weight, fontstyle=style, zorder=4)


# --- compartment positions (age-2 row; both sexes identical) ---
ySIA = 2.5
xS, xI, xA = 2.0, 5.3, 8.6
yP = 4.8

box(xS, ySIA, "S", "susceptible", S_C)
box(xI, ySIA, "I", "infected", I_C)
box(xA, ySIA, "A", "AIDS", A_C)
box(xS, yP, "P", "protected", P_C)

# --- disease progression: S -> I -> A ---
arrow(xS + BW / 2, ySIA, xI - BW / 2, ySIA)
label((xS + xI) / 2, ySIA + 0.42, "λ", color=I_C, size=15)
label((xS + xI) / 2, ySIA - 0.42, "force of infection", color=SOFT,
      size=8.5, weight="normal", style="italic")

arrow(xI + BW / 2, ySIA, xA - BW / 2, ySIA)
label((xI + xA) / 2, ySIA + 0.42, "γ", color=INK, size=15)
label((xI + xA) / 2, ySIA - 0.42, "progression", color=SOFT,
      size=8.5, weight="normal", style="italic")

# --- vaccine loop: S <-> P (two curved arrows side by side) ---
arrow(xS - 0.28, ySIA + BH / 2, xS - 0.28, yP - BH / 2, color=P_C, rad=0.0)
label(xS - 1.18, (ySIA + yP) / 2, "ν", color=P_C, size=15)
label(xS - 1.18, (ySIA + yP) / 2 - 0.40, "vaccinate", color=SOFT,
      size=8, weight="normal", style="italic")

arrow(xS + 0.28, yP - BH / 2, xS + 0.28, ySIA + BH / 2, color=SOFT, rad=0.0)
label(xS + 1.15, (ySIA + yP) / 2, "l", color=SOFT, size=14)
label(xS + 1.15, (ySIA + yP) / 2 - 0.40, "waning", color=SOFT,
      size=8, weight="normal", style="italic")

# --- births into S ---
arrow(0.35, ySIA, xS - BW / 2, ySIA, color=SOFT, lw=1.6)
label(0.55, ySIA + 0.34, "births", color=SOFT, size=9, weight="normal")

# --- mortality (small downward arrows) ---
for cx, lab, col in [(xS, "μ", SOFT), (xI, "μ", SOFT),
                     (xA, "μ+α", A_C), ]:
    arrow(cx, ySIA - BH / 2, cx, ySIA - BH / 2 - 0.6, color=col, lw=1.5)
    label(cx + (0.5 if lab == "μ+α" else 0.28), ySIA - BH / 2 - 0.42,
          lab, color=col, size=10, weight="normal")
# death from P
arrow(xS - 0.28 - 0.0, yP + BH / 2, xS - 0.55, yP + BH / 2 + 0.55,
      color=SOFT, lw=1.4)
label(xS - 0.95, yP + BH / 2 + 0.5, "μ", color=SOFT, size=10, weight="normal")

# --- title / note ---
ax.text(5.0, 5.85, "sIC model + vaccine: how individuals flow",
        ha="center", va="top", color=INK, fontsize=12.5, fontweight="bold")
ax.text(9.9, 0.15,
        "shown for age-2 (sexually active); both sexes identical · "
        "A excluded from λ",
        ha="right", va="bottom", color=SOFT, fontsize=7.5, fontstyle="italic")

fig.tight_layout(pad=0.4)
out1 = "figures/sic_flow_diagram.png"
out2 = "../presentation/assets/sic_flow_diagram.png"
fig.savefig(out1, facecolor=PAPER, bbox_inches="tight")
fig.savefig(out2, facecolor=PAPER, bbox_inches="tight")
print("saved:", out1, "and", out2)
