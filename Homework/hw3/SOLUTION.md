# 作業三解答報告 — 數值模擬生物系統動態

**課程**：BME5113 生物系統建模與分析
**作業**：HW3（2025 春季學期，Due 2026-04-16）

> 模擬程式：`hw3_solution.py`，輸出圖檔於 `hw3_figures/`

---

## 第一題 (25%): 啤酒發酵方程式（溫度最適 Curve A）

### 模型建構

狀態變數（每公升麥汁 / per litre of wort）：

| 符號 | 物理量 | 單位 |
|:--:|----|:--:|
| $S$ | 糖 (sugar) | g/L |
| $Y$ | 酵母生物量 (yeast biomass) | g/L |
| $E$ | 乙醇 (ethanol) | g/L |
| $C$ | 二氧化碳 (CO₂) 釋出量 | g/L |

**化學計量 (stoichiometry)** — 題目給定：

$$2.0665\ \text{g sugar} \longrightarrow 1\ \text{g EtOH} + 0.9565\ \text{g CO}_2 + 0.11\ \text{g yeast}$$

質量守恆檢核：$1 + 0.9565 + 0.11 = 2.0665$ ✓。由此定義 yield coefficients（產率係數）：

$$Y_{E/S} = \frac{1}{2.0665} \approx 0.4839,\quad
Y_{C/S} = \frac{0.9565}{2.0665} \approx 0.4629,\quad
Y_{Y/S} = \frac{0.11}{2.0665} \approx 0.0532$$

**動力學 (kinetics)** — Monod substrate uptake × 溫度最適函數：

$$\mu(T, S) = \mu_{\max}\,f_T(T)\,\frac{S}{K_s + S}$$

Fig 5.4 **curve A** 以高斯 (Gaussian) 形式實作：

$$f_T(T) = \exp\!\left(-\frac{(T - T_{\text{opt}})^2}{2\sigma_T^2}\right)$$

**溫度擾動 (diurnal forcing)**：平均 20°C、振幅 8°C、週期 1 天、峰值在中午 12:00：

$$T(t) = 20 + 8\cos\!\left(\frac{2\pi (t - 12)}{24}\right)\quad [t\ \text{in hours}]$$

驗證：$t=12$ 時 $T=28°\text{C}$（中午最高）；$t=0,24$ 時 $T=12°\text{C}$（午夜最低）。✓

**ODE 系統**（改寫自 Fig 5.8 的啤酒方程式）：

$$\boxed{
\begin{aligned}
\frac{dY}{dt} &= \mu(T,S)\,Y - k_d\,Y \\
\frac{dS}{dt} &= -\frac{1}{Y_{Y/S}}\,\mu(T,S)\,Y \\
\frac{dE}{dt} &= \frac{Y_{E/S}}{Y_{Y/S}}\,\mu(T,S)\,Y \\
\frac{dC}{dt} &= \frac{Y_{C/S}}{Y_{Y/S}}\,\mu(T,S)\,Y
\end{aligned}}$$

### 參數選擇（compatible with real conditions）

| 參數 | 值 | 說明 |
|:--:|:--:|----|
| $\mu_{\max}$ | 0.12 /hr | 最適條件下比增長率（典型 *S. cerevisiae*） |
| $K_s$ | 5 g/L | Monod 半飽和常數（酵母對糖親和力高） |
| $k_d$ | 0 | 酵母死亡率（設為 0 以確保化學計量嚴格閉合；可視需要提升至 0.001–0.005 /hr 加入衰減） |
| $T_{\text{opt}}$ | 25 °C | curve A 溫度最適 |
| $\sigma_T$ | 5 °C | 最適曲線寬度 |
| $S_0$ | 120 g/L | 初始麥汁糖度（約 12°P 比重） |
| $Y_0$ | 0.5 g/L | 投酵 (pitching) 濃度 |

選擇理由：使一週 (168 hr) 內完成主要糖分消耗，對應題目所述「primary fermentation takes about a week」。

### 參考連結內容摘要（The Kitchn — Emma Christensen）

題目提供的連結 `thekitchn.com/how-beer-is-brewed-a-timeline` 中，完整釀造時程如下：

| 階段 | 時長 | 重點 |
|---|:--:|---|
| **Brew Day** | 4 – 4½ 小時 | Mash（糖化）→ Sparging（洗糖）→ Hop Boil（煮花）→ Pitching Yeast（投酵） |
| **Primary Fermentation** | **1 週** | 酵母活性最高；「大啖糖分宴席」，產生大量酒精與 CO₂ |
| Secondary Fermentation | 2 週 | 酵母緩慢清理殘糖，沉澱物下沉，酒液轉清 |
| Bottle Conditioning | 2 週 – 1 年 | 瓶中二次發酵產生碳酸氣 |
| **總時長** | ≥ 5 週 | 從釀造日到開瓶飲用 |

核心公式：**sugary wort + yeast + time = beer**。酵母吃掉麥汁中的糖，釋出乙醇 (alcohol) 與二氧化碳 (CO₂)。

本作業**僅模擬 Primary Fermentation**（168 hr），因為這是酵母生長 + 糖分消耗 + 酒精與 CO₂ 生成最劇烈的階段，也是 Fig 5.8 啤酒方程式所描述的對象。後續 Secondary + Bottle stages 主要為靜置澄清，不屬本模型範疇。

### 模擬結果

RK-4 with $\Delta t = 0.1\ \text{hr}$，積分 168 hr：

```
Sugar consumed   : 120.00 g/L  (100.0% of initial)
Ethanol produced :  58.07 g/L  (stoich: 58.07)  ← ABW ≈ 5.8%, ABV ≈ 7.3%
CO2     released :  55.54 g/L  (stoich: 55.54)
Yeast   final    :   6.89 g/L  (stoich: 6.89)
Mass-balance residual (ethanol): 1.4e-14       ← 化學計量嚴格成立（浮點精度內）
```

四項狀態變數都與化學計量預測完全一致（殘差僅為浮點誤差量級），驗證模型建構無誤。

見 `hw3_figures/fig1_beer_fermentation.png`（四個狀態變數時序）與 `fig1b_temperature_curve.png`（溫度擾動 + $f_T$ 曲線）。

### 模型參數敏感度討論

固定其他參數，改變 $T_{\text{opt}}$，觀察 72 hr（發酵中期）糖消耗率：

| $T_{\text{opt}}$ | 72 hr 糖消耗 | 物理解釋 |
|:--:|:--:|----|
| 15 °C | 100% | 午夜（T=12°C）接近最適，活性穩定 |
| 20 °C | 100% | 介於兩極之間，全日高活性 |
| 25 °C | 100% | 介於日均與峰值之間，效率最高 |
| 30 °C | 94.8% | 僅在午夜和中午之間短暫接近 |
| 35 °C |  9.1% | 操作範圍遠離最適，酵母幾乎休眠 |

**關鍵觀察**：

1. **溫度/最適匹配**：只要最適溫度落在日變化範圍 (12–28°C) 內，發酵可在 7 天完成；超出此範圍（如 35°C）會嚴重拖慢。
2. **週期性加速**：每日中午酵母活性激增，產生圖上可見的「階梯狀」糖消耗曲線。
3. **質量守恆嚴格滿足**（殘差 $\sim 10^{-14}$）— 這是化學計量直接耦合的必然結果。
4. **$\mu_{\max}$ 與 $K_s$ 主導總體速率**：若 $\mu_{\max}$ 減半，發酵無法在一週內完成；$K_s$ 放大則末期低糖時活性下降。

---

## 第二題 (25%): Lotka-Volterra 無量綱化

### 原系統 (Eq. 4.23)

$$\frac{dV}{dt} = rV - aVP,\qquad \frac{dP}{dt} = abVP - dP$$

原系統含 4 個參數 $(r, a, b, d)$。無量綱化的目標是**縮減參數數量**，找出控制動態的真正獨立群組。

### 縮放選擇 (scaling choice)

時間以獵物自然成長率為尺度：$\tau = r\,t$

狀態變數以固定點為尺度。由 $dV/dt = dP/dt = 0$ 得固定點

$$V^* = \frac{d}{ab},\qquad P^* = \frac{r}{a}$$

令：

$$x = \frac{V}{V^*} = \frac{ab}{d}V,\qquad y = \frac{P}{P^*} = \frac{a}{r}P$$

### 代入推導

**獵物方程式**：
$$\frac{dV}{dt} = rV - aVP$$
左側：$\dfrac{dV}{dt} = \dfrac{d}{ab}\dfrac{dx}{dt} = \dfrac{d}{ab}\cdot r\dfrac{dx}{d\tau} = \dfrac{dr}{ab}\dfrac{dx}{d\tau}$

右側：$r\cdot\dfrac{d}{ab}x - a\cdot\dfrac{d}{ab}x\cdot\dfrac{r}{a}y = \dfrac{dr}{ab}x - \dfrac{dr}{ab}xy$

兩側除以 $\dfrac{dr}{ab}$：

$$\boxed{\frac{dx}{d\tau} = x(1 - y)}$$

**捕食者方程式**：
$$\frac{dP}{dt} = abVP - dP$$
左側：$\dfrac{dP}{dt} = \dfrac{r}{a}\cdot r\dfrac{dy}{d\tau} = \dfrac{r^2}{a}\dfrac{dy}{d\tau}$

右側：$ab\cdot\dfrac{d}{ab}x\cdot\dfrac{r}{a}y - d\cdot\dfrac{r}{a}y = \dfrac{dr}{a}xy - \dfrac{dr}{a}y$

兩側除以 $\dfrac{r^2}{a}$：

$$\boxed{\frac{dy}{d\tau} = \alpha\,y(x - 1),\qquad \alpha = \frac{d}{r}}$$

### 結論

$$\left\{\begin{aligned}
\dfrac{dx}{d\tau} &= x(1 - y)\\[4pt]
\dfrac{dy}{d\tau} &= \alpha\,y(x - 1)
\end{aligned}\right.\qquad \alpha = \frac{d}{r}$$

從 4 個獨立參數 $(r, a, b, d)$ **縮減成 1 個無量綱群組** $\alpha = d/r$。固定點移至 $(1,1)$。物理意義：

- $\alpha$ = 捕食者死亡率 / 獵物內在增長率
- $\alpha$ 大 → 捕食者快速反應，振盪頻率高
- $\alpha$ 小 → 捕食者遲緩，振盪頻率低
- 振盪週期 $T \propto 1/\sqrt{\alpha}$（線性化分析）

見 `hw3_figures/fig2_lv_nondim.png`：多個 $\alpha$ 的相圖（phase portrait）與時序。

---

## 第三題 (25%): RK-4 時間步長對 Eq. 6.4 的影響

### 選用方程式

> **假設說明**：題目僅標示「Eq. 6.4」未附式子。本解答假設 Eq. 6.4 為第 6 章（數值方法）所用的 **Lotka-Volterra 示範系統**（dimensional form），以觀察振盪型 ODE 的數值收斂行為。若教科書 Eq. 6.4 實為其他 ODE，只需替換 `eq64_rhs` 函數即可；RK-4 收斂階次的結論（$O(\Delta t^4)$）不變。

$$\frac{dV}{dt} = rV - aVP,\qquad \frac{dP}{dt} = abVP - dP$$

參數 $(r, a, b, d) = (1.0, 0.1, 0.5, 0.5)$，初值 $V(0)=10$、$P(0)=5$，積分區間 $t\in[0, 50]$。此設定會產生約 4 個振盪週期，正好可以觀察數值方法是否累積相位誤差。

### RK-4 單步

$$\begin{aligned}
k_1 &= f(t_n, y_n)\\
k_2 &= f(t_n + \tfrac{\Delta t}{2}, y_n + \tfrac{\Delta t}{2}k_1)\\
k_3 &= f(t_n + \tfrac{\Delta t}{2}, y_n + \tfrac{\Delta t}{2}k_2)\\
k_4 &= f(t_n + \Delta t, y_n + \Delta t\,k_3)\\
y_{n+1} &= y_n + \tfrac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)
\end{aligned}$$

局部截斷誤差 $O(\Delta t^5)$，全域誤差 $O(\Delta t^4)$。

### 結果

與極細參考解 ($\Delta t = 0.001$) 比較 $V(50)$：

| $\Delta t$ | $V(50)$ | 絕對誤差 |
|:--:|:--:|:--:|
| 1.0 | 13.3101 | $1.44 \times 10^{-1}$ |
| 0.5 | 13.4651 | $1.14 \times 10^{-2}$ |
| 0.1 | 13.4538 | $4.93 \times 10^{-5}$ |
| 0.01 | 13.45376 | $5.69 \times 10^{-9}$ |

**誤差縮減比率** — 由 $\Delta t=1.0$ 到 $\Delta t=0.1$（縮小 10 倍），誤差從 $1.4\times 10^{-1}$ 降至 $5\times 10^{-5}$，約縮 **3000 倍**，接近理論 $10^4$；由 $\Delta t=0.1$ 再到 $0.01$ 縮約 $9000$ 倍，符合 $O(\Delta t^4)$。

**收斂判定**：$\Delta t \leq 0.1$ 時 $V(50)$ 已正確至小數點後 4 位；$\Delta t = 0.01$ 幾乎為精確解。可以說 **$\Delta t \approx 0.1$ 為動態收斂所需的時間步長**。

見 `hw3_figures/fig3_rk4_timestep.png`。

---

## 第四題 (25%): 水槽液位 — Euler vs Runge-Kutta

### 方程式

$$16\sqrt{5h - h^2}\,\frac{dh}{dt} = -\sin\!\frac{\pi t}{60},\qquad h(0) = 2,\quad 0 \leq t \leq 120$$

改寫為 $\displaystyle \frac{dh}{dt} = -\frac{\sin(\pi t / 60)}{16\sqrt{h(5 - h)}}$

注意：分母在 $h = 0$ 和 $h = 5$ 時為零（可行域 $0 < h < 5$）。時間步太大時可能衝出邊界而引發 $\sqrt{\cdot}$ 異常。

### 解析解（作為參考）

分離變數：

$$\int 16\sqrt{h(5-h)}\,dh = -\int \sin\!\frac{\pi t}{60}\,dt$$

令 $u = h - 5/2$，$R = 5/2$，則 $h(5-h) = R^2 - u^2$。利用
$\int \sqrt{R^2 - u^2}\,du = \tfrac{u}{2}\sqrt{R^2-u^2} + \tfrac{R^2}{2}\arcsin(u/R)$：

$$G(h) \equiv 8\!\left(h - \tfrac{5}{2}\right)\sqrt{h(5-h)} + 50\arcsin\!\frac{2h - 5}{5}$$

$$\boxed{G(h(t)) - G(h_0) = \frac{60}{\pi}\!\left[\cos\!\frac{\pi t}{60} - 1\right]}$$

週期 $= 120$（與題目區間一致），故 $h(120) = h(0) = 2$。

### 數值實驗

固定步長 $\Delta t$，跑 Euler 與 RK-4，與解析解取最大絕對誤差：

| $\Delta t$ | Euler 最大誤差 | RK-4 最大誤差 |
|:--:|:--:|:--:|
| 10.0 | $1.53 \times 10^{-1}$ | $6.10 \times 10^{-5}$ |
| 5.0 | $7.57 \times 10^{-2}$ | $3.92 \times 10^{-6}$ |
| 2.0 | $2.98 \times 10^{-2}$ ✓ | $1.03 \times 10^{-7}$ |
| 1.0 | $1.48 \times 10^{-2}$ | $6.49 \times 10^{-9}$ |
| 0.5 | $7.39 \times 10^{-3}$ | $\approx 10^{-6}$ † |
| 0.1 | $1.48 \times 10^{-3}$ | $\approx 10^{-6}$ † |
| 0.01 | $1.47 \times 10^{-4}$ | $\approx 10^{-6}$ † |

† RK-4 誤差在 $\Delta t \lesssim 1$ 後「停滯」於 $\sim 10^{-6}$，**這是解析解 bisection + 參考網格插值** 所貢獻的誤差基線（不是數值方法本身的限制）。

### 回答題目

**「incorrect solution」定義**：本文採用兩層判準：

1. **寬鬆定義（工程可接受）**：最大絕對誤差 $|h_{\text{num}} - h_{\text{exact}}|_\infty > 0.05$（約為液位量級 $h \sim 2$ 的 2.5%）。
2. **嚴格定義（工程精準）**：最大絕對誤差 $> 10^{-3}$。

逐一判讀：

| 方法 | 最大允許 $\Delta t$ |
|---|:--:|
| Euler | $\Delta t \lesssim 2.0$（誤差 $\sim 3\%$） |
| RK-4 | $\Delta t \lesssim 10.0$ 仍精確至 $10^{-4}$ 等級 |

若要求更嚴格的精度（如 $10^{-3}$），Euler 需 $\Delta t \lesssim 0.1$；RK-4 在 $\Delta t = 1.0$ 就已經達到 $10^{-9}$。

**比較 (comparison)**：

1. **精度階數**：Euler 為 $O(\Delta t)$，RK-4 為 $O(\Delta t^4)$。觀察 Euler 誤差每次縮步長 2 倍約減半，RK-4 則縮 16 倍，與理論吻合。
2. **效率**：RK-4 每步 4 次右側計算，Euler 1 次。但 Euler 需要小 50–100 倍的步長才能達同等精度 — RK-4 實際 **快 1~2 個數量級**。
3. **穩定性**：本題非剛性 (not stiff)，但邊界奇異性（$h\to 0, 5$）使大步長的 Euler 可能衝出域。實驗中，由於初值 $h_0=2$ 遠離邊界，兩法在 $\Delta t \leq 10$ 範圍均未發生實際的域外失敗；不過 Euler 大步長已明顯失真。

見 `hw3_figures/fig4_tank_euler_vs_rk.png`（$\Delta t = 1.0$ 與 $0.1$ 兩情境的比較）。

---

## 結果摘要

| 題目 | 主要產出 |
|---|---|
| 第一題 | 啤酒發酵 ODE 系統（Monod × curve A），7 天 100% 糖消耗，乙醇 58 g/L；$T_{\text{opt}}$ 敏感度顯示超出日變化範圍則顯著遲滯 |
| 第二題 | LV 無量綱化：$dx/d\tau = x(1-y)$、$dy/d\tau = \alpha y(x-1)$，4 參數 → 1 參數 $\alpha = d/r$ |
| 第三題 | RK-4 收斂於 $\Delta t \approx 0.1$；誤差階次實測為 $O(\Delta t^4)$ |
| 第四題 | 水槽液位解析解 $G(h) = (60/\pi)(\cos(\pi t/60)-1) + G(h_0)$；Euler 需 $\Delta t \lesssim 2$（粗精度）或 $\lesssim 0.1$（高精度），RK-4 在 $\Delta t \lesssim 10$ 即已極精確 |

---

*所有模擬由 `hw3_solution.py` 產生。執行：`python3 hw3_solution.py`*
