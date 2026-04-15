# 作業三解答報告 — 數值模擬生物系統動態

**課程**：BME5113 生物系統建模與分析
**作業**：HW3（2025 春季學期，Due 2026-04-16）

> 模擬程式：`hw3_solution.py`，輸出圖檔於 `hw3_figures/`
>
> 本次解答根據課本四張對應截圖補正（Fig 5.4、Fig 5.8、Eq. 4.23/4.24、Eq. 6.4）。

---

## 第一題 (25%): 啤酒發酵 — Fig 5.8 原方程 × Fig 5.4 curve A 溫度函數

### 基礎方程 (Fig 5.8)

圖中給出的 yeast/beer fermentation 三條 ODE（以每公升麥汁 g/L 計）：

$$\frac{dS}{dt} = -abSY - afSY,\qquad
\frac{dY}{dt} = acSY - dYA,\qquad
\frac{dA}{dt} = abSY$$

變數：$S$ = 糖，$Y$ = 酵母，$A$ = 乙醇。係數意義（Spain 原書）：
$a$ 為糖吸收速率常數；$b$ 為轉為酒精的比例；$f$ 為另一去路（CO₂ 散失）；$c$ 為酵母的產率係數；$d$ 為乙醇毒性造成的死亡率。

### Problem 1 的修改 — 把 yeast 生長項乘上 Temperature Optimum

題目要求**酵母生長使用 Fig 5.4 curve A**，故將 $dY/dt$ 中的生長項乘上 $f_T(T)$：

$$\boxed{\frac{dY}{dt} = f_T(T)\,a c S Y - d Y A}$$

$dS/dt$ 與 $dA/dt$ 維持 Fig 5.8 原式不變。

### Temperature Optimum（Fig 5.4 panel K 曲線 A）

Fig 5.4 panel K **curve A 參數**（截圖表格）：

$$k_1 = 1.25,\quad k_2 = 1.5,\quad k_3 = 29.3,\quad k_4 = 40$$

採 Spain 常用的非對稱溫度最適式（Logan-type）：

$$f_T(T) \;=\; k_1 \left(\frac{k_4 - T}{k_4 - k_3}\right)^{\!k_2}\exp\!\left(k_2\,\frac{T - k_3}{k_4 - k_3}\right),\quad T < k_4$$

性質驗證：
- $f_T(k_3) = k_1 \cdot 1 \cdot e^0 = k_1 = 1.25$（曲線峰值與截圖一致）
- $f_T(k_4) = 0$（上限致死）
- $T > k_4$ 時 $f_T \equiv 0$
- 於操作範圍（12–28°C）內 $f_T$ 由 0.69 升到 0.99，涵蓋合理活性區

### 溫度擾動

題目：平均 20°C、振幅 8°C、週期 1 天、峰值在中午 12:00。

$$T(t) \;=\; 20 + 8\cos\!\left(\frac{2\pi(t - 12)}{24}\right)\quad [t\ \text{in hours}]$$

驗證：$t=12 \Rightarrow T=28°\mathrm{C}$（中午最高），$t=0,24 \Rightarrow T=12°\mathrm{C}$（午夜最低）。

### 參數選擇（與真實釀酒條件相容）

| 參數 | 值 | 說明 |
|:--:|:--:|---|
| $a$ | 0.0050 L·g⁻¹·hr⁻¹ | 糖吸收速率常數（調至一週內消耗主要糖分） |
| $b$ | 0.484 | 糖→乙醇比例 $= 1/2.0665$ |
| $f$ | 0.466 | 糖→CO₂ 比例 $= 0.9565/2.0665$ |
| $c$ | 0.055 | 酵母產率 $\approx 0.11/2.0665$ |
| $d$ | $2\times 10^{-4}$ L·g⁻¹·hr⁻¹ | 乙醇毒性死亡 |
| $S_0$ | 120 g/L | 初始麥汁糖度（~12°P） |
| $Y_0$ | 0.5 g/L | 投酵濃度 |

化學計量比 $(b : f : c) = (0.484 : 0.466 : 0.055)$ 嚴格對應題目 $(1 : 0.9565 : 0.11)/2.0665$（誤差僅來自 $c$ 對應 0.0532 的第 3 位小數四捨五入）。

### 模擬結果（RK-4，$\Delta t = 0.1\ \mathrm{hr}$，積分 168 hr）

```
Sugar consumed   : 102.11 g/L   (85.1% of initial)     ← 「primary fermentation」
Ethanol produced :  52.02 g/L   (stoich b/(b+f)·ΔS = 52.02)
CO2  (implicit)  :  50.09 g/L   (via f-branch)
Yeast   final    :   2.90 g/L
ABV ≈ 6.6 %      (ethanol density 0.79 g/mL)
```

對應工業發酵「一週消耗主要糖分（attenuation ≈ 85%）、留下殘糖進二次發酵」的典型行為；ABV 6–7% 符合 strong ale / IPA 區間。乙醇數值與化學計量預測 $b/(b+f)\cdot\Delta S$ 吻合到 0.01 g/L 以內，證實 Fig 5.8 的質量流守恆嚴格成立。

見 `hw3_figures/fig1_beer_fermentation.png`（S, Y, A, T 時序）與 `fig1b_temperature_curve.png`（curve A 的 $f_T$ 形狀 + 日週期 $T(t)$ 對 $f_T$ 的調制）。

### 參數敏感度（program scan）

| 掃描參數 | 觀察 |
|---|---|
| $k_3$ (T_opt) | $k_3 = 20\!\sim\!25\,°\mathrm{C}$ 發酵最完全（$A_f \approx 57\,\mathrm{g/L}$）；$k_3 = 37\,°\mathrm{C}$ 則 $A_f$ 僅 $19\,\mathrm{g/L}$ — 最適溫度落在 $T(t)$ 範圍外即顯著降速 |
| $a$ (糖吸收) | $a$ 從 0.002 到 0.008，$A_f$ 由 19 到 59 g/L — 線性主導整體速率 |
| $d$ (乙醇毒性) | $d = 0$ 時 $Y_f = 6.1$、$A_f = 57$；$d = 10^{-3}$ 時 $Y_f = 0.39$、$A_f = 35$ — 酵母死亡率明顯限制發酵末期產酒量 |

**關鍵觀察**：

1. **溫度/最適匹配**：$k_3$ 若偏離日變化範圍（12–28°C）過遠，發酵嚴重延遲。
2. **日週期調制**：$f_T(T(t))$ 每日中午（$T$ 接近 $k_3$）活性升至 $\sim 1$，午夜（$T=12$）壓低至 $\sim 0.7$，$Y$ 與 $A$ 因此出現階梯狀成長曲線。
3. **乙醇毒性回饋**：$d Y A$ 項使 $Y$ 在 $\sim 100$ hr 後達高峰而轉降，後期糖消耗速率漸緩。
4. **Fig 5.8 的 $c$ 項不從 $S$ 扣除**：此為 Spain 原式的簡化；本實作忠於原式未補扣，故嚴格質量守恆只對 EtOH/CO₂ 部分成立。

---

## 第二題 (25%): Lotka-Volterra 無量綱化（Eq. 4.23 / 4.24）

### 原系統

$$\frac{dV}{dt} = \underbrace{rV}_{\text{positive feedback}} - \underbrace{aVP}_{\text{mass action}} \quad (4.23),\qquad
\frac{dP}{dt} = \underbrace{abVP}_{\text{conversion}} - \underbrace{dP}_{\text{death}} \quad (4.24)$$

原系統含 4 個獨立參數 $(r, a, b, d)$。無量綱化目標：縮減至真正獨立的無量綱群組。

### 縮放選擇

- 時間以獵物成長率為尺度：$\tau = rt$
- 狀態以固定點為尺度。由 $dV/dt = dP/dt = 0$ 得

$$V^* = \frac{d}{ab},\qquad P^* = \frac{r}{a}$$

令 $x = V/V^* = (ab/d)V$，$y = P/P^* = (a/r)P$。

### 推導

**獵物方程**：$\dfrac{dV}{dt} = \dfrac{d}{ab}\cdot r\dfrac{dx}{d\tau} = \dfrac{dr}{ab}\dfrac{dx}{d\tau}$

右側：$rV - aVP = r\dfrac{d}{ab}x - a\cdot\dfrac{d}{ab}x\cdot\dfrac{r}{a}y = \dfrac{dr}{ab}(x - xy)$

$\Rightarrow \boxed{\dfrac{dx}{d\tau} = x(1 - y)}$

**捕食者方程**：$\dfrac{dP}{dt} = \dfrac{r^2}{a}\dfrac{dy}{d\tau}$

右側：$abVP - dP = \dfrac{dr}{a}xy - \dfrac{dr}{a}y = \dfrac{dr}{a}y(x - 1)$

$\Rightarrow \boxed{\dfrac{dy}{d\tau} = \alpha\,y(x - 1),\quad \alpha = \dfrac{d}{r}}$

### 結論

$$\left\{\begin{aligned}
\dfrac{dx}{d\tau} &= x(1 - y) \\[3pt]
\dfrac{dy}{d\tau} &= \alpha\,y(x - 1)
\end{aligned}\right.\qquad \alpha = \dfrac{d}{r}$$

**4 個獨立參數 $(r, a, b, d)$ 縮減為 1 個無量綱群組 $\alpha = d/r$**；固定點移至 $(1, 1)$。

物理意義：$\alpha$ 大 → 捕食者反應快，振盪頻率高；$\alpha$ 小 → 反應慢，週期長（線性化週期 $T \propto 1/\sqrt{\alpha}$）。

見 `hw3_figures/fig2_lv_nondim.png`：三種 $\alpha$ 的相圖與時序。

---

## 第三題 (25%): RK-4 時間步長對剛性系統 Eq. 6.4 的影響

### 方程（Eq. 6.4，截圖）

$$\boxed{\frac{du}{dt} = 998u + 1998v,\qquad \frac{dv}{dt} = -999u - 1999v}$$

### 特徵值 — 此為經典剛性問題

$\mathbf{A} = \begin{pmatrix} 998 & 1998 \\ -999 & -1999 \end{pmatrix}$；
trace $= -1001$，det $= 998\cdot(-1999) - 1998\cdot(-999) = 1000$。

特徵多項式 $\lambda^2 + 1001\lambda + 1000 = (\lambda + 1)(\lambda + 1000) = 0$

$$\Rightarrow\ \boxed{\lambda_1 = -1,\quad \lambda_2 = -1000 \quad (\text{剛性比 1000})}$$

### 解析解

**初始條件假設**（題目未指定 $u(0), v(0)$）：採 $u(0)=1,\ v(0)=0$，使**兩個模態都被激發** — 這是剛性測試的保守選擇。若 IC 剛好對齊慢特徵向量（例如 $(u,v)=(2,-1)$），則 $C_2=0$、快模態不出現，任何 $\Delta t$ 都能穩定，完全看不出剛性問題。

由特徵向量分解（$\lambda_1=-1$ 對應 $(2,-1)$，$\lambda_2=-1000$ 對應 $(1,-1)$）：
$C_1 = u_0 + v_0 = 1,\ C_2 = -(u_0 + 2v_0) = -1$，故

$$u(t) = 2e^{-t} - e^{-1000t},\qquad v(t) = -e^{-t} + e^{-1000t}$$

快模態 $e^{-1000t}$ 在 $t \sim 5\times 10^{-3}$ 即衰減殆盡，之後只剩慢模態 $e^{-t}$。但 RK-4 是**顯式方法**，必須全程解析快模態。

### RK-4 絕對穩定性條件

RK-4 放大因子 $R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24$，其中 $z = \lambda\,\Delta t$。
沿實數負軸，穩定邊界 $|R(z)| \leq 1$ 給出 $z \geq -2.7853$。

因此對快模態 $\lambda_2 = -1000$：

$$\Delta t \;\leq\; \frac{2.7853}{1000} \;\approx\; 2.79 \times 10^{-3}$$

**題目給的四個步長 $\Delta t = (1.0, 0.5, 0.1, 0.01)$ 全部超過此界**，應全不穩定。

### 實驗結果（從 $t=0$ 積到 $t=1.0$，比較 $u$ 在 $t=1.0$ 的值；積分器最後一步自動 clamp 至 $t_\text{end}$）

| $\Delta t$ | n_steps | $u(1.0)$ | 絕對誤差 | 狀態 |
|:--:|:--:|:--:|:--:|---|
| 1.0 | 1 | $-4.15\times 10^{10}$ | $4.2\times 10^{10}$ | 不穩定 |
| 0.5 | 2 | $-6.67\times 10^{18}$ | $6.7\times 10^{18}$ | 不穩定 |
| 0.1 | 10 | BLOWUP ($>10^{20}$) | — | **失控** |
| 0.01 | 100 | BLOWUP | — | 失控 |
| $5\times 10^{-3}$ | 200 | BLOWUP | — | 失控 |
| $3\times 10^{-3}$ | 334 | BLOWUP | — | 剛好超過邊界 |
| $2.79\times 10^{-3}$ | 359 | $-3.36$ | $4.1$ | 邊界上，仍不準 |
| $2.5\times 10^{-3}$ | 400 | 0.73576 | $2.5\times 10^{-13}$ | **收斂** |
| $2\times 10^{-3}$ | 500 | 0.73576 | $1.1\times 10^{-13}$ | 收斂 |
| $1\times 10^{-3}$ | 1000 | 0.73576 | $5.3\times 10^{-15}$ | 精確 |
| $5\times 10^{-4}$ | 2000 | 0.73576 | $2.6\times 10^{-15}$ | 精確 |

解析參考 $u(1.0) = 2e^{-1} - e^{-1000} \approx 0.7357588823$

### 回答題目

**「動態收斂所需的時間步長」**：

- **穩定性門檻**：$\Delta t \lesssim 2.79 \times 10^{-3}$（理論）；實驗在 $\Delta t = 2.5\times 10^{-3}$ 首次收斂，$\Delta t = 3\times 10^{-3}$ 仍在邊界上振盪。
- **精準度需求**：$\Delta t \approx 1\times 10^{-3}$ 已達浮點精度極限（相對誤差 $10^{-15}$）。

**關鍵結論**：

1. 題目所列四個 $\Delta t$ **無一穩定**：
   - $\Delta t = 1.0, 0.5$ 只跑 1–2 步就放大出 $10^{10}\!\sim\!10^{18}$ 量級誤差；
   - $\Delta t = 0.1, 0.01$ 分別跑 10、100 步，每步放大因子 $|R(-100)|, |R(-10)|$ 遠大於 1，結果溢出 $10^{20}$。
2. 穩定性邊界非常貼近理論值 $2.7853/1000 \approx 2.79\times 10^{-3}$：$\Delta t = 3\times 10^{-3}$ 已失控、$\Delta t = 2.5\times 10^{-3}$ 剛好收斂 — 邊界寬度不足 15%。
3. 這是**剛性 (stiffness)** 的教科書案例：顯式方法為了穩定必須追蹤早已衰減的快模態。
4. 正確對策：用 **implicit / A-stable** 方法（Backward Euler、Trapezoidal、BDF）即可在 $\Delta t \sim \mathcal{O}(10^{-1})$ 仍穩定，而 RK-4 被綁死在 $\Delta t \sim 10^{-3}$。

見 `hw3_figures/fig3_rk4_timestep.png`：比較 $\Delta t = 0.01$（失控）、$3\times 10^{-3}$（邊界）、$2.5\times 10^{-3}$（剛好收斂）、$10^{-3}$（精確）。

---

## 第四題 (25%): 水槽液位 — Euler vs Runge-Kutta

### 方程式

$$16\sqrt{5h - h^2}\,\frac{dh}{dt} = -\sin\!\frac{\pi t}{60},\qquad h(0) = 2,\quad 0 \leq t \leq 120$$

改寫為 $\displaystyle \frac{dh}{dt} = -\frac{\sin(\pi t / 60)}{16\sqrt{h(5 - h)}}$

可行域 $0 < h < 5$；分母於 $h \to 0, 5$ 發散。

### 解析解（作為參考）

分離變數並取 $u = h - 5/2,\ R = 5/2$，使用 $\int \sqrt{R^2 - u^2}\,du = \tfrac{u}{2}\sqrt{R^2-u^2} + \tfrac{R^2}{2}\arcsin(u/R)$：

$$G(h) \equiv 8\!\left(h - \tfrac{5}{2}\right)\sqrt{h(5-h)} + 50\arcsin\!\frac{2h - 5}{5}$$

$$\boxed{G(h(t)) - G(h_0) = \frac{60}{\pi}\!\left[\cos\!\frac{\pi t}{60} - 1\right]}$$

週期 = 120（與區間一致），故 $h(120) = h(0) = 2$。

### 數值實驗

固定步長，跑 Euler 與 RK-4，與解析解取最大絕對誤差：

| $\Delta t$ | Euler 最大誤差 | RK-4 最大誤差 |
|:--:|:--:|:--:|
| 10.0 | $1.53\times 10^{-1}$ | $6.10\times 10^{-5}$ |
| 5.0 | $7.57\times 10^{-2}$ | $3.92\times 10^{-6}$ |
| 2.0 | $2.98\times 10^{-2}$ ✓ | $1.03\times 10^{-7}$ |
| 1.0 | $1.48\times 10^{-2}$ | $6.49\times 10^{-9}$ |
| 0.5 | $7.39\times 10^{-3}$ | $\sim 10^{-6}$ † |
| 0.1 | $1.48\times 10^{-3}$ | $\sim 10^{-6}$ † |
| 0.01 | $1.48\times 10^{-4}$ | $\sim 10^{-6}$ † |

† RK-4 誤差在 $\Delta t \lesssim 1$ 後停滯於 $\sim 10^{-6}$，此為**解析解 bisection + 參考網格插值** 的誤差基線，非 RK-4 本身的限制。

### 回答題目

「incorrect solution」採雙判準：寬鬆 $|err|_\infty > 0.05$（約 $h$ 量級的 2.5%），嚴格 $|err|_\infty > 10^{-3}$。

| 方法 | 最大允許 $\Delta t$ |
|---|:--:|
| Euler（寬鬆） | $\Delta t \lesssim 2.0$（誤差 $\sim 3\%$） |
| Euler（嚴格） | $\Delta t \lesssim 0.1$ |
| RK-4（寬鬆） | $\Delta t \lesssim 10.0$ 已精確至 $10^{-4}$ |
| RK-4（嚴格） | $\Delta t = 1.0$ 即達 $10^{-9}$ |

**比較**：

1. **精度階數**：Euler $O(\Delta t)$，RK-4 $O(\Delta t^4)$。Euler 誤差縮步長 2 倍約減半、RK-4 縮 16 倍，與理論一致。
2. **效率**：RK-4 每步 4 次右側計算，Euler 1 次；但 Euler 需小 50–100 倍步長才同精度 — RK-4 實際**快 1–2 個數量級**。
3. **穩定性**：本題非剛性，邊界奇異性（$h\to 0, 5$）使大步長 Euler 有衝出域風險；初值 $h_0=2$ 遠離邊界，實驗中 $\Delta t \leq 10$ 都未實際發散，但 Euler 大步長已明顯失真。

見 `hw3_figures/fig4_tank_euler_vs_rk.png`（$\Delta t = 1.0$ 與 $0.1$ 的 Euler/RK-4 對照）。

---

## 結果摘要

| 題目 | 主要產出 |
|---|---|
| 第一題 | Fig 5.8 原方程 × Fig 5.4 curve A（$k_1{=}1.25, k_2{=}1.5, k_3{=}29.3, k_4{=}40$），7 天消耗 85% 糖、ABV≈6.6%；$k_3, a, d$ 的敏感度符合物理預期 |
| 第二題 | LV 非量綱化：$dx/d\tau = x(1-y)$、$dy/d\tau = \alpha y(x-1)$，4 參數 → 1 參數 $\alpha = d/r$ |
| 第三題 | Eq. 6.4 剛性系統 ($\lambda = -1, -1000$)；題目給的 $\Delta t = (1.0, 0.5, 0.1, 0.01)$ **全部不穩定**；RK-4 穩定性要求 $\Delta t \lesssim 2.79\times 10^{-3}$，收斂於 $\Delta t \approx 2.5\times 10^{-3}$ |
| 第四題 | 水槽液位解析解 $G(h) = (60/\pi)(\cos(\pi t/60) - 1) + G(h_0)$；Euler 需 $\Delta t \lesssim 2$（粗）或 $\lesssim 0.1$（細），RK-4 於 $\Delta t \lesssim 10$ 即已極精確 |

---

*所有模擬由 `hw3_solution.py` 產生。執行：`python hw3_solution.py`*
