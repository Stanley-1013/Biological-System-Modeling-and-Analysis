"""
BME5113 HW2 — Forrester 圖繪製與模擬
=============================================
產出：
  hw2_figures/fig1_lotka_volterra.png   (Problem 1)
  hw2_figures/fig2_tree_dynamics.png    (Problem 2)
  hw2_figures/fig3_foodweb.png          (Problem 3)
  hw2_figures/fig4_immune_sim.png       (Problem 4, 補充模擬)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# 中文字型設定（依環境選擇可用字型）
for font in ['Noto Sans CJK TC', 'Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']:
    try:
        plt.rcParams['font.family'] = font
        break
    except Exception:
        continue
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hw2_figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Forrester 圖繪製工具
# ============================================================

def draw_stock(ax, cx, cy, label, w=2.0, h=0.9, color='#B3D9FF'):
    """繪製存量（矩形）"""
    rect = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor='black', linewidth=2
    )
    ax.add_patch(rect)
    ax.text(cx, cy, label, ha='center', va='center',
            fontsize=9, fontweight='bold')


def draw_cloud(ax, cx, cy, label='', size=0.35):
    """繪製源/匯（灰色圓，代表系統邊界外）"""
    circle = plt.Circle((cx, cy), size,
                         facecolor='#E8E8E8', edgecolor='gray',
                         linewidth=1.5, linestyle='--', zorder=2)
    ax.add_patch(circle)
    if label:
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=6.5, color='#555555')


def draw_auxiliary(ax, cx, cy, label, r=0.4, color='#FFFFCC'):
    """繪製輔助變數（圓形）"""
    circle = plt.Circle((cx, cy), r,
                         facecolor=color, edgecolor='black',
                         linewidth=1.5, zorder=3)
    ax.add_patch(circle)
    ax.text(cx, cy, label, ha='center', va='center',
            fontsize=7, wrap=True)


def draw_flow(ax, x1, y1, x2, y2, label='', color='#1565C0', lw=2.5):
    """繪製物質流（粗實線箭頭）"""
    ax.annotate(
        '', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='-|>', color=color, lw=lw,
                        mutation_scale=18),
        zorder=4
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # 自動偏移標籤（水平流偏上，垂直流偏右）
        if abs(y2 - y1) < abs(x2 - x1):
            ax.text(mx, my + 0.3, label, ha='center', va='bottom',
                    fontsize=8, color=color, fontweight='bold')
        else:
            ax.text(mx + 0.3, my, label, ha='left', va='center',
                    fontsize=8, color=color, fontweight='bold')


def draw_info(ax, x1, y1, x2, y2, label='', color='#C62828'):
    """繪製資訊連結（虛線箭頭）"""
    ax.annotate(
        '', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.2,
                        linestyle='--', mutation_scale=12),
        zorder=3
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.15, label, ha='center', va='bottom',
                fontsize=6.5, color=color, style='italic')


def draw_valve(ax, cx, cy, size=0.18):
    """繪製蝶形閥（bowtie）"""
    top = patches.Polygon(
        [(cx - size, cy + size), (cx + size, cy + size), (cx, cy)],
        closed=True, facecolor='white', edgecolor='black', linewidth=1.2, zorder=5
    )
    bot = patches.Polygon(
        [(cx - size, cy - size), (cx + size, cy - size), (cx, cy)],
        closed=True, facecolor='white', edgecolor='black', linewidth=1.2, zorder=5
    )
    ax.add_patch(top)
    ax.add_patch(bot)


# ============================================================
# Problem 1: Lotka-Volterra Forrester 圖
# ============================================================

def fig1_lotka_volterra():
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Problem 1: Lotka-Volterra Forrester Diagram (g C)',
                 fontsize=13, fontweight='bold', pad=10)

    # --- 存量 ---
    draw_stock(ax, 3.5, 3, 'V\n(prey, g C)')
    draw_stock(ax, 10, 3, 'P\n(predator, g C)')

    # --- 源/匯 ---
    draw_cloud(ax, 0.8, 3, 'source')       # 獵物繁殖碳來源
    draw_cloud(ax, 12.8, 3, 'sink')         # 捕食者死亡碳去向
    draw_cloud(ax, 6.75, 0.5, 'sink')       # 代謝損耗碳去向

    # --- 物質流 ---
    # F1: 獵物繁殖 source → V
    draw_flow(ax, 1.15, 3, 2.5, 3, 'rV')
    draw_valve(ax, 1.8, 3)

    # F2: 捕食 V → 分配點 (6.75, 3)
    draw_flow(ax, 4.5, 3, 6.75, 3, 'aVP')
    draw_valve(ax, 5.6, 3)

    # F3: 同化 分配點 → P
    draw_flow(ax, 6.75, 3, 9.0, 3, 'abVP')
    draw_valve(ax, 7.9, 3)

    # F4: 代謝損耗 分配點 → sink
    draw_flow(ax, 6.75, 2.7, 6.75, 0.85, 'a(1-b)VP')
    draw_valve(ax, 6.75, 1.8)

    # F5: 捕食者死亡 P → sink
    draw_flow(ax, 11.0, 3, 12.45, 3, 'dP')
    draw_valve(ax, 11.7, 3)

    # --- 分配點標記 ---
    ax.plot(6.75, 3, 'ko', markersize=6, zorder=6)

    # --- 資訊連結 ---
    draw_info(ax, 3.5, 3.5, 1.8, 3.5, 'V')         # V → 繁殖閥
    draw_info(ax, 3.5, 2.5, 5.2, 2.5, 'V')          # V → 捕食閥
    draw_info(ax, 10, 2.5, 5.6, 2.5, 'P')            # P → 捕食閥
    draw_info(ax, 10, 3.5, 11.7, 3.5, 'P')           # P → 死亡閥

    # --- 圖例 ---
    legend_y = 5.0
    draw_stock(ax, 1.5, legend_y, 'Stock', w=1.2, h=0.5)
    draw_cloud(ax, 3.5, legend_y, 'Src/Sink', size=0.25)
    ax.annotate('', xy=(5.5, legend_y), xytext=(4.5, legend_y),
                arrowprops=dict(arrowstyle='-|>', color='#1565C0', lw=2.5))
    ax.text(5.0, legend_y + 0.25, 'Material Flow', ha='center', fontsize=7)
    ax.annotate('', xy=(7.5, legend_y), xytext=(6.5, legend_y),
                arrowprops=dict(arrowstyle='->', color='#C62828', lw=1.2, linestyle='--'))
    ax.text(7.0, legend_y + 0.25, 'Info Link', ha='center', fontsize=7)
    draw_valve(ax, 8.5, legend_y, size=0.12)
    ax.text(8.5, legend_y + 0.25, 'Valve', ha='center', fontsize=7)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_lotka_volterra.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("[OK] fig1_lotka_volterra.png")


# ============================================================
# Problem 2: 樹木碳水動態 Forrester 圖
# ============================================================

def fig2_tree_dynamics():
    fig, ax = plt.subplots(1, 1, figsize=(16, 11))
    ax.set_xlim(-1, 16)
    ax.set_ylim(-1, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Problem 2: Tree Carbon-Water Dynamics Forrester Diagram',
                 fontsize=13, fontweight='bold', pad=10)

    # --- 存量 ---
    # 水循環（左側）
    draw_stock(ax, 3, 3, '$W_r$\nRoot Water\n(g H₂O)', color='#B3E5FC')
    draw_stock(ax, 3, 7, '$W_l$\nLeaf Water\n(g H₂O)', color='#B3E5FC')
    # 碳循環（右側）
    draw_stock(ax, 11, 7, '$C_l$\nLeaf Sugar\n(g C)', color='#C8E6C9')
    draw_stock(ax, 11, 3, '$C_r$\nRoot Sugar\n(g C)', color='#C8E6C9')

    # --- 源/匯（雲朵）---
    draw_cloud(ax, 3, 0.5, 'Soil\nWater')         # 土壤水
    draw_cloud(ax, 3, 9.5, 'Atm\nH₂O')            # 大氣水蒸氣
    draw_cloud(ax, 11, 9.5, 'Atm\nCO₂')           # 大氣 CO₂（光合來源）
    draw_cloud(ax, 11, 0.5, 'Atm\nCO₂')           # 大氣 CO₂（呼吸去向）
    draw_cloud(ax, 14.5, 7, 'Atm\nCO₂')           # 葉呼吸去向

    # --- 外部驅動 ---
    draw_auxiliary(ax, 7, 9.5, 'Light', r=0.45, color='#FFF9C4')
    draw_auxiliary(ax, 0.5, 5, 'Precip.', r=0.45, color='#E3F2FD')
    draw_auxiliary(ax, 14.5, 4.5, 'Temp.', r=0.45, color='#FFCCBC')

    # --- 輔助變數 ---
    draw_auxiliary(ax, 6.5, 7, '$g_s$\nStomatal\nCond.', r=0.55, color='#FFF59D')

    # --- 水循環流量 ---
    # W1: 土壤 → W_r（根部吸水）
    draw_flow(ax, 3, 0.85, 3, 2.55, 'Uptake')
    draw_valve(ax, 3, 1.7)
    # W2: W_r → W_l（木質部輸送）
    draw_flow(ax, 3, 3.45, 3, 6.55, 'Xylem')
    draw_valve(ax, 3, 5)
    # W3: W_l → 大氣（蒸散）
    draw_flow(ax, 3, 7.45, 3, 9.15, 'Transpiration')
    draw_valve(ax, 3, 8.3)

    # --- 碳循環流量 ---
    # C1: 大氣 CO₂ → C_l（光合作用）
    draw_flow(ax, 11, 9.15, 11, 7.45, 'Photosynthesis')
    draw_valve(ax, 11, 8.3)
    # C2: C_l → C_r（韌皮部輸送）
    draw_flow(ax, 11, 6.55, 11, 3.45, 'Phloem')
    draw_valve(ax, 11, 5)
    # C3: C_l → 大氣 CO₂（葉呼吸）
    draw_flow(ax, 12.0, 7, 14.1, 7, 'Leaf Resp.')
    draw_valve(ax, 13, 7)
    # C4: C_r → 大氣 CO₂（根呼吸）
    draw_flow(ax, 11, 2.55, 11, 0.85, 'Root Resp.')
    draw_valve(ax, 11, 1.7)

    # --- 資訊連結 ---
    # W_l → g_s
    draw_info(ax, 4.0, 7, 5.95, 7, '$W_l$')
    # g_s → 蒸散閥
    draw_info(ax, 6.0, 7.4, 3.3, 8.1)
    # g_s → 光合閥
    draw_info(ax, 7.0, 7.4, 10.7, 8.1)
    # Light → 光合閥
    draw_info(ax, 7.4, 9.2, 10.7, 8.5)
    # Temp → 葉呼吸閥
    draw_info(ax, 14.2, 5.0, 13.2, 6.8)
    # Temp → 根呼吸閥
    draw_info(ax, 14.2, 4.1, 11.3, 1.9)
    # Precip → 吸水閥
    draw_info(ax, 0.9, 4.7, 2.7, 1.9)
    # W_r, W_l → 木質部閥（水勢梯度驅動）
    draw_info(ax, 3.5, 3.5, 3.3, 4.8)
    # CO₂ → 光合閥（大氣 CO₂ 濃度）
    draw_info(ax, 11, 9.15, 11, 8.5)

    # --- 區域標示 ---
    # 葉部框
    rect_leaf = patches.FancyBboxPatch(
        (1.5, 6.2), 12, 2.0,
        boxstyle="round,pad=0.2", facecolor='none',
        edgecolor='green', linewidth=1.5, linestyle=':'
    )
    ax.add_patch(rect_leaf)
    ax.text(7.5, 6.3, '─── LEAVES ───', ha='center', fontsize=9,
            color='green', style='italic')

    # 根部框
    rect_root = patches.FancyBboxPatch(
        (1.5, 2.2), 12, 2.0,
        boxstyle="round,pad=0.2", facecolor='none',
        edgecolor='#8D6E63', linewidth=1.5, linestyle=':'
    )
    ax.add_patch(rect_root)
    ax.text(7.5, 2.3, '─── ROOTS ───', ha='center', fontsize=9,
            color='#8D6E63', style='italic')

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_tree_dynamics.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("[OK] fig2_tree_dynamics.png")


# ============================================================
# Problem 3: 食物網 Forrester 圖
# ============================================================

def fig3_foodweb():
    fig, ax = plt.subplots(1, 1, figsize=(15, 9))
    ax.set_xlim(-1, 15)
    ax.set_ylim(-1, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Problem 3: Foodweb Forrester Diagram (1 prey, 2 predators, g C)',
                 fontsize=13, fontweight='bold', pad=10)

    # --- 存量 ---
    draw_stock(ax, 4, 4.5, '$x$\n(prey, g C)', color='#C8E6C9')
    draw_stock(ax, 10, 7, '$y$\n(pred. 1, g C)', color='#FFCDD2')
    draw_stock(ax, 10, 2, '$z$\n(pred. 2, g C)', color='#D1C4E9')

    # --- 源/匯 ---
    draw_cloud(ax, 0.8, 4.5, 'source')          # 獵物成長碳來源
    draw_cloud(ax, 13.5, 7, 'sink')              # y 死亡
    draw_cloud(ax, 13.5, 2, 'sink')              # z 死亡
    draw_cloud(ax, 7, 8.5, 'sink')               # y 代謝損耗
    draw_cloud(ax, 7, 0.5, 'sink')               # z 代謝損耗

    # --- 物質流 ---
    # 獵物成長 source → x
    draw_flow(ax, 1.15, 4.5, 3.0, 4.5, 'rx(1-x/K)')
    draw_valve(ax, 2.0, 4.5)

    # y 捕食 x → 分配點 (7, 7)
    draw_flow(ax, 5.0, 5.0, 6.7, 6.7, '[ax/(h+x)]y')
    draw_valve(ax, 5.8, 5.8)
    ax.plot(7, 7, 'ko', markersize=5, zorder=6)  # 分配點
    # y 同化
    draw_flow(ax, 7.2, 7, 9.0, 7, r'$e_1 \frac{ax}{h+x} y$')
    draw_valve(ax, 8.1, 7)
    # y 代謝損耗
    draw_flow(ax, 7, 7.2, 7, 8.15, r'$(1{-}e_1)\frac{ax}{h+x}y$')
    draw_valve(ax, 7, 7.7)

    # z 捕食 x → 分配點 (7, 2)
    draw_flow(ax, 5.0, 4.0, 6.7, 2.3, 'cxz')
    draw_valve(ax, 5.8, 3.2)
    ax.plot(7, 2, 'ko', markersize=5, zorder=6)  # 分配點
    # z 同化
    draw_flow(ax, 7.2, 2, 9.0, 2, '$e_2 cxz$')
    draw_valve(ax, 8.1, 2)
    # z 代謝損耗
    draw_flow(ax, 7, 1.8, 7, 0.85, '$(1{-}e_2)cxz$')
    draw_valve(ax, 7, 1.3)

    # y 死亡 y → sink
    draw_flow(ax, 11.0, 7, 13.15, 7, '$d_1 y$')
    draw_valve(ax, 12.0, 7)

    # z 死亡 z → sink
    draw_flow(ax, 11.0, 2, 13.15, 2, r'$d_0 e^{-\gamma z} z$')
    draw_valve(ax, 12.0, 2)

    # --- 輔助變數 ---
    draw_auxiliary(ax, 5.8, 7, 'ax/(h+x)\nType II', r=0.5, color='#FFECB3')
    draw_auxiliary(ax, 5.8, 2, 'cx\nType I', r=0.45, color='#FFECB3')
    draw_auxiliary(ax, 12.0, 0.5, r'$d_0 e^{-\gamma z}$', r=0.5, color='#FFECB3')
    draw_auxiliary(ax, 2.0, 6, '1-x/K', r=0.45, color='#FFECB3')

    # --- 資訊連結 ---
    # x → 成長閥
    draw_info(ax, 4, 5.0, 2.2, 5.6)
    # x → y 捕食
    draw_info(ax, 4.5, 5.2, 5.5, 6.6)
    # x → z 捕食
    draw_info(ax, 4.5, 3.8, 5.5, 2.4)
    # y → y 捕食
    draw_info(ax, 9.5, 7.3, 6.3, 7.3)
    # z → z 捕食
    draw_info(ax, 9.5, 1.7, 6.3, 1.7)
    # z → z 死亡率輔助
    draw_info(ax, 10, 1.5, 12.0, 0.9)
    # z 死亡率輔助 → z 死亡閥
    draw_info(ax, 12.0, 1.0, 12.0, 1.8)
    # y → y 死亡閥
    draw_info(ax, 10.5, 7.4, 12.0, 7.4)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_foodweb.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("[OK] fig3_foodweb.png")


# ============================================================
# Problem 4: 免疫系統模擬（補充）
# ============================================================

def fig4_immune_simulation():
    """
    模擬免疫系統 ODE（前向 Euler 法），展示癌細胞與免疫反應的動態競賽。
    此模擬為補充內容，題目只要求寫方程式與驗證單位。
    """
    # 參數
    r_H = 0.5         # 健康細胞成長率 [1/day]
    T = 1e6            # 健康細胞穩態 [cells]
    alpha = 1e-7       # 癌細胞殺傷健康細胞 [1/(cells*day)]
    r_C = 0.2          # 癌細胞增長率 [1/day]
    beta = 1e-7        # 免疫殺傷（三體）[1/(cells^2*day)]
    sigma_M = 1e-4     # M 增殖對 C 的響應 [1/(cells*day)]
    sigma_K = 1e-4     # K 增殖對 C 的響應 [1/(cells*day)]
    delta_M = 0.1      # M 衰減率 [1/day]
    delta_K = 0.1      # K 衰減率 [1/day]
    M0_base = 50.0     # M 基線 [cells]
    K0_base = 50.0     # K 基線 [cells]

    # 初始條件
    H0 = 1e6
    C0 = 100.0
    M0_init = 50.0
    K0_init = 50.0

    # Euler 模擬
    dt = 0.01   # day
    t_max = 60  # days
    n = int(t_max / dt) + 1
    t = np.linspace(0, t_max, n)

    H = np.zeros(n)
    C = np.zeros(n)
    M = np.zeros(n)
    K = np.zeros(n)

    H[0], C[0], M[0], K[0] = H0, C0, M0_init, K0_init

    for i in range(n - 1):
        dH = r_H * H[i] * (1 - H[i] / T) - alpha * C[i] * H[i]
        dC = r_C * C[i] - beta * M[i] * K[i] * C[i]
        dM = sigma_M * C[i] * M[i] - delta_M * (M[i] - M0_base)
        dK = sigma_K * C[i] * K[i] - delta_K * (K[i] - K0_base)

        H[i + 1] = max(H[i] + dt * dH, 0)
        C[i + 1] = max(C[i] + dt * dC, 0)
        M[i + 1] = max(M[i] + dt * dM, 0)
        K[i + 1] = max(K[i] + dt * dK, 0)

    # 繪圖
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Problem 4: Immune System Simulation (Forward Euler)',
                 fontsize=13, fontweight='bold')

    # H
    axes[0, 0].plot(t, H, 'b-', linewidth=1.5)
    axes[0, 0].set_ylabel('Healthy cells $H$')
    axes[0, 0].set_title('Healthy Cells')
    axes[0, 0].ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    axes[0, 0].grid(True, alpha=0.3)

    # C
    axes[0, 1].plot(t, C, 'r-', linewidth=1.5)
    axes[0, 1].set_ylabel('Cancer cells $C$')
    axes[0, 1].set_title('Cancer Cells')
    axes[0, 1].grid(True, alpha=0.3)

    # M
    axes[1, 0].plot(t, M, 'g-', linewidth=1.5)
    axes[1, 0].set_ylabel('WBC type $M$')
    axes[1, 0].set_xlabel('Time (days)')
    axes[1, 0].set_title('White Blood Cells M')
    axes[1, 0].grid(True, alpha=0.3)

    # K
    axes[1, 1].plot(t, K, 'm-', linewidth=1.5)
    axes[1, 1].set_ylabel('WBC type $K$')
    axes[1, 1].set_xlabel('Time (days)')
    axes[1, 1].set_title('White Blood Cells K')
    axes[1, 1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4_immune_sim.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("[OK] fig4_immune_sim.png")


# ============================================================
# 主程式
# ============================================================

if __name__ == '__main__':
    print(f"Output directory: {OUTPUT_DIR}\n")
    fig1_lotka_volterra()
    fig2_tree_dynamics()
    fig3_foodweb()
    fig4_immune_simulation()
    print(f"\nAll figures saved to {OUTPUT_DIR}/")
