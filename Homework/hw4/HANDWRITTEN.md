# HW4 手寫版（精簡）

> 這份是給手寫繳交用的精簡版。**粗體 [貼圖]** 表示直接貼程式輸出圖；其餘段落只寫關鍵式子與
> 數字。完整推導見 `SOLUTION.md`。

---

## P1 — Michaelis-Menten 4 法 (25%)

**模型**：$\;v = \dfrac{V_{\max}\,S}{K_m + S}$

**資料**：$S = (4, 10, 30, 90, 173, 256)$，$v = (2.5, 9.5, 12.5, 19.5, 21.5, 19.0)$

**(a) Lineweaver-Burke**：$\dfrac{1}{v} = \dfrac{K_m}{V_{\max}}\cdot\dfrac{1}{S} + \dfrac{1}{V_{\max}}$
　→ OLS on $(1/S,\,1/v)$；slope $= K_m/V_{\max}$, intercept $= 1/V_{\max}$

**(b) Eadie-Hofstee**：$v = V_{\max} - K_m\cdot\dfrac{v}{S}$
　→ OLS on $(v/S,\,v)$；slope $= -K_m$, intercept $= V_{\max}$

**(c) Levenberg-Marquardt**：$\min\sum(v_i - \hat v_i)^2$ 直接非線性 LSQ（用 Jacobian + 阻尼）

**(d) Nelder-Mead**：同目標，但用無導數 simplex

### 結果

| 法 | $V_{\max}$ | $K_m$ | SSE | $R^2$ |
|---|--:|--:|--:|--:|
| (a) LB | 34.43 | 47.83 | 152.2 | 0.43 |
| (b) EH | 20.99 | 17.21 | 15.83 | 0.94 |
| (c) LM | **22.21** | **18.22** | **12.68** | **0.95** |
| (d) NM | 22.21 | 18.22 | 12.68 | 0.95 |

**[貼圖 fig1_mm_fits.png]**

**討論**（4 點）：
1. LB $R^2$ 慘 ($0.43$) — 倒數放大低 $v$ 端誤差，OLS 被低 $S$ 點主導 → $K_m$ 高估 2.6×
2. EH 較好但仍偏 — 兩軸都含 $v$，自相關
3. LM $\equiv$ NM，互相驗證收斂到同一極值
4. 結論：**用 LM 或 NM**；LB/EH 只當手算速估

---

## P2 — Boston lettuce 生長 (25%)

**資料**：$N=34$ 點，$t \in [0, 16.81]$ d；$M_0$ 取第一筆觀測。

**Logistic**：$M = \dfrac{M_0 K}{M_0 + (K-M_0)e^{-rt}}$，$\;\text{AGR}=rM(1-\tfrac{M}{K})$，$\;\text{RGR}=r(1-\tfrac{M}{K})$

**Gompertz**：$M = K\!\left(\tfrac{M_0}{K}\right)^{e^{-rt}}$，$\;\text{AGR}=rM\ln\tfrac{K}{M}$，$\;\text{RGR}=r\ln\tfrac{K}{M}$

### 擬合結果

| 處理 | 模型 | $r$ (d⁻¹) | $K$ (cm²) | RMSE | $R^2$ |
|:-:|:-:|--:|--:|--:|--:|
| 16-hr | **Logistic** | **0.309** | **518** | **7.55** | **0.998** |
| 16-hr | Gompertz | 0.103 | 945 | 16.7 | 0.988 |
| 24-hr | **Logistic** | **0.297** | **434** | **8.81** | **0.994** |
| 24-hr | Gompertz | 0.086 | 1053 | 15.4 | 0.983 |

### 生長率特徵（解析推導）

Logistic 峰：$t_{\text{pk}} = \tfrac{1}{r}\ln\tfrac{K-M_0}{M_0}$，$\text{AGR}_{\max} = rK/4$
Gompertz 峰：$t_{\text{pk}} = \tfrac{1}{r}\ln\!\ln\tfrac{K}{M_0}$，$\text{AGR}_{\max} = rK/e$

| 處理 / 模型 | $t_{\text{pk}}$ (d) | $\text{AGR}_{\max}$ |  RGR(0) | RGR($t_{\text{end}}$) |
|:-:|:-:|:-:|:-:|:-:|
| 16-hr Logistic | 10.43 | 40.1 | 0.298 | 0.038 |
| 16-hr Gompertz | 13.13 | 35.8 | 0.398 | 0.071 |
| 24-hr Logistic | 11.57 | 32.2 | 0.287 | 0.052 |
| 24-hr Gompertz | **17.19**(超出資料) | 33.1 | 0.372 | 0.088 |

**[貼圖 fig2_lettuce_growth.png]** ← 6 panel：M(t), AGR(t), RGR(t) × 兩處理
**[貼圖 fig2b_lettuce_compare.png]** ← 兩處理 Gompertz 直接對比

**結論與比較**：
- **Logistic 較佳**：RMSE 約一半，$K$ 在生物上合理 (518 vs 945)
- **24-hr 反而 $K$ 較低** (434 < 518)：連續光照引起 CLI（continuous light injury），植物需暗期修復
- AGR 峰皆在 $t \approx 10\!\sim\!12$ d，對應 $M\approx K/2 \approx$ 220–260 cm²
- RGR 隨時間單調下降 → 自我遮蔭 / 非光合組織比例上升

---

## P3 — Reilly (1970) Fig 8.7 模型鑑別 (25%)

**資料**：$x=(0,1,2,3)$，$y=(-1.290, 5.318, 7.049, 19.886)$

**4 模型**：
M1: $y = ax$　|　M2: $y = a + bx$　|　M3: $y = a\,e^{bx}$　|　M4: $y = a + bx + cx^2$

### 三準則

**(i) 1:1 regression**：$\hat y = \alpha + \beta\,y_{\text{obs}}$，理想 $\beta=1, \alpha=0$；t 檢定

**(ii) Paired t**：$H_0: \overline{\hat y - y} = 0$（無系統偏差）

**(iii) Theil's U**：
$$U_1 = \frac{\sqrt{\overline{(\hat y - y)^2}}}{\sqrt{\overline{\hat y^2}} + \sqrt{\overline{y^2}}} \in [0,1],\qquad
U_2 = \sqrt{\frac{\sum(\hat y_t - y_t)^2}{\sum(y_t - y_{t-1})^2}}\quad(<1\text{ 才合格})$$

### 結果

| 模型 | 參數 | RMSE | $R^2$ | slope | paired-p | $U_1$ | $U_2$ |
|---|---|--:|--:|--:|--:|--:|--:|
| M1 | $a=5.65$ | 2.67 | 0.879 | 0.78 | 0.66 | 0.124 | 0.356 |
| M2 | $a=-2.05,\,b=6.53$ | 2.37 | 0.905 | 0.91 | 1.00 | 0.110 | 0.322 |
| **M3** | $a=1.17,\,b=0.94$ | **1.72** | **0.95** | 0.92 | 0.86 | **0.080** | **0.165** |
| M4 | $a=-0.49,\,b=1.85,\,c=1.56$ | 1.79 | 0.946 | 0.95 | 1.00 | 0.083 | 0.240 |

**[貼圖 fig3_reilly_models.png]** ← 左：4 條曲線 + 資料；右：1:1 plot

**結論**：**M3 (exponential) 最佳**
- RMSE / $R^2$ / $U_1$ / $U_2$ 全勝
- 與 Reilly (1970) 似然比結論一致：$L_{\max,3} = 202.2 \gg L_{\max,2} = 1$
- 註：M2、M4 含截距 OLS 強制 $\sum r_i = 0$，paired-t 結構失能（$p=1.0$）→ 必看 Theil's U

---

## P4 — Harrison (1995) 標準模型 vs Luckinbill 18-day (25%)

**模型**：
$$\frac{dx}{dt} = \rho(1 - \tfrac{x}{K})x - \omega y\frac{x}{\phi+x},\qquad
\frac{dy}{dt} = \sigma y\frac{x}{\phi+x} - \gamma y$$

**參數**：$\rho=1.85,\ K=898,\ \omega=25.5,\ \phi=284.1,\ \sigma=12.40,\ \gamma=2.07$
**ICs**：$x_0 = 15.0$ (Paramecium/mL)，$y_0 = 5.833$ (Didinium/mL)

### 平衡點分析

$x^* = \dfrac{\gamma\phi}{\sigma-\gamma} = \dfrac{2.07 \times 284.1}{12.40 - 2.07} = 56.93$
$y^* = \dfrac{\rho}{\omega}(1-\tfrac{x^*}{K})(\phi + x^*) = 23.17$
prey nullcline 頂點 $\dfrac{K-\phi}{2} = 306.95$

→ $x^* = 57 \nless 307$ → **Rosenzweig-MacArthur 條件不成立**，$E_1$ **不穩**，發散震盪

### 數值積分

LSODA，$rtol=10^{-8}$, $atol=10^{-10}$；$t \in [0, 18.5]$ d

### Chapter 8 統計

| 指標 | Prey | Predator | 聯合 (σ-scaled) |
|---|--:|--:|--:|
| n | 36 | 37 | 73 |
| RMSE | 115.4 | 74.3 | 1.17 |
| 1:1 $R^2$ | **−0.06** | **−0.65** | −0.35 |
| slope (vs 1) | **0.35** ($p<10^{-3}$) | **0.06** ($p<10^{-7}$) | 0.20 ($p<10^{-9}$) |
| paired-t | $p = 0.166$ | **$p = 0.005$** | **$p = 0.002$** |
| Theil $U_1$ | 0.45 | 0.60 | 0.52 |
| Theil $U_2$ | **1.58** | **2.61** | **2.01** |

**[貼圖 fig4_harrison_validation.png]** ← 上：時序對照；下：1:1 plot
**[貼圖 fig4b_harrison_phase.png]** ← 相平面 + nullclines

### 「好模型」定義（4 項全滿才 PASS）

1. $R^2 > 0.7$
2. 1:1 之 $\beta=1, \alpha=0$ 不被拒絕（$p > 0.05$）
3. paired-t 不顯著
4. Theil $U_2 < 1$

| 判準 | Prey | Predator |
|:-:|:-:|:-:|
| ① $R^2 > 0.7$ | ❌ | ❌ |
| ② $\beta=1$ | ❌ | ❌ |
| ③ paired-t | ✓ | ❌ |
| ④ $U_2 < 1$ | ❌ | ❌ |

### 結論：**不是好模型**

- 模型振幅遠小於資料（slope = 0.35, 0.06）→ 模型「太扁」
- $U_2 > 1$：比 naive「明天等於今天」還差 1.6–2.6 倍
- 與 Harrison 自評一致（Table 1: $S_1^2 = 236{,}137$，"disappointing"）
- 改善方向：(a) 加入 mutual interference $-\delta y^2$；(b) Holling Type III sigmoid $f(x)$；(c) 延遲響應

---

## 摘要一頁

| 題 | 結論 | 關鍵數字 |
|---|---|---|
| P1 | LM/NM 為金標準；LB 失真 | $V_{\max}=22.21,\,K_m=18.22$ |
| P2 | Logistic > Gompertz；24-hr CLI | $r_{16}=0.309,\,K_{16}=518$；$r_{24}=0.297,\,K_{24}=434$ |
| P3 | M3 (exp) 各準則均勝 | $U_1=0.080,\,U_2=0.165$ |
| P4 | 標準模型 fail | $R^2 < 0$；$U_2 = 1.6\!\sim\!2.6 > 1$ |

---

*程式：`hw4_solution.py`；圖檔：`hw4_figures/`；完整版：`SOLUTION.md`*
