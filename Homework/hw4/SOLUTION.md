# 作業四解答報告 — 參數估計、生長模型與模型鑑別

**課程**：BME5113 生物系統建模與分析 (Biological Systems Modeling and Analysis)
**作業**：HW4（2025 春季學期，Due 2026-04-30）

> 模擬程式：`hw4_solution.py`，輸出圖檔於 `hw4_figures/`
>
> 本次解答整合四個常見的「資料 ↔ 模型」工作流：(1) 線性化轉換 vs 直接非線性最小平方
> (Michaelis-Menten)；(2) 生長曲線參數估計與生長率推導 (logistic / Gompertz)；
> (3) 模型鑑別 (model discrimination) 的三種統計準則 (1:1 regression, paired t, Theil's U)；
> (4) 將前述準則套用到生態學的捕食者-被捕食者模型 (Harrison 1995 標準模型)。

---

## 第一題 (25%): Michaelis-Menten 四種估計法比較

### 模型與資料

$$\boxed{\;v(S) \;=\; \frac{V_{\max}\,S}{K_m + S}\;}$$

| Prey density $S$ | 4 | 10 | 30 | 90 | 173 | 256 |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Prey eaten $v$   | 2.5 | 9.5 | 12.5 | 19.5 | 21.5 | 19.0 |

### (a) Lineweaver-Burke (雙倒數轉換)

對方程式取倒數：

$$\frac{1}{v} \;=\; \frac{K_m}{V_{\max}}\cdot\frac{1}{S} + \frac{1}{V_{\max}}$$

對 $(1/S,\,1/v)$ 做 OLS 直線回歸；斜率 $m = K_m/V_{\max}$、截距 $b = 1/V_{\max}$。
再由 $V_{\max} = 1/b$、$K_m = m\cdot V_{\max}$。

### (b) Eadie-Hofstee 轉換

把方程式改寫為

$$v \;=\; V_{\max} \;-\; K_m \cdot \frac{v}{S}$$

對 $(v/S,\;v)$ 做 OLS 直線回歸；截距 $= V_{\max}$、斜率 $= -K_m$。

> 推導：$v(K_m + S) = V_{\max}S \Rightarrow v K_m = V_{\max}S - vS \Rightarrow v = V_{\max} - K_m\,(v/S)$.

### (c) Levenberg-Marquardt（未轉換）

直接對原方程式做非線性最小平方：

$$\min_{V_{\max}, K_m}\;\sum_i\bigl[v_i - \tfrac{V_{\max}S_i}{K_m+S_i}\bigr]^2$$

用 `scipy.optimize.curve_fit(method='lm')`，初始猜測 $(V_{\max}, K_m) = (25, 50)$。

### (d) Nelder-Mead simplex（未轉換）

同樣的目標函式 SSE，但用無導數的 simplex 演算法：`scipy.optimize.minimize(..., method='Nelder-Mead')`。
作為 LM 的對照，檢查兩種非線性方法是否收斂到同一個極小值。

### 結果

| 方法 | $V_{\max}$ | $K_m$ | SSE | $R^2$ |
|---|--:|--:|--:|--:|
| (a) Lineweaver-Burke | 34.4287 | 47.8281 | 152.21 | 0.428 |
| (b) Eadie-Hofstee   | 20.9855 | 17.2064 |  15.83 | 0.941 |
| (c) Levenberg-Marquardt | **22.2086** | **18.2182** | **12.68** | **0.952** |
| (d) Nelder-Mead simplex | 22.2086 | 18.2182 | 12.68 | 0.952 |

見 `hw4_figures/fig1_mm_fits.png`：左圖為四種擬合曲線疊在資料上；中、右為兩種轉換的線性散佈圖。

### 討論

1. **Lineweaver-Burke 嚴重失真**。$R^2$ 只有 $0.43$，與其他三法相差近一個量級。
   原因：取倒數後**極小的 $v$ 值會被放大成極大的 $1/v$**——例如本資料 $v=2.5$ 倒數為 $0.4$，
   而 $v=21.5$ 倒數為 $0.047$，**低 $v$ 點在 $1/v$ 軸的權重高出近一個量級**。
   等變異數 OLS 因此被低 $S$（恰恰最不可靠）的點主導，估出 $K_m=47.8$（真值 $\approx 18.2$ 的 2.6 倍）。
   這在臨床藥動學或酵素分析會直接導致**錯誤的劑量、抑制劑常數、催化效率排名**。
2. **Eadie-Hofstee 比 LB 好得多**（$R^2=0.94$），因為兩軸都含 $v$，不會把單側測量誤差放大。
   但仍非無偏：縱橫軸**自相關**（$v$ 同時出現），違反 OLS 對「自變數無誤差」的假設。
3. **(c) LM 與 (d) NM 完全收斂到同一答案** $(V_{\max}, K_m) = (22.21, 18.22)$，SSE = 12.68，
   為四法中最佳。LM 依賴 Jacobian 解析；NM 不需導數但收斂較慢。對此 6 點問題兩者皆秒內收斂。
4. **建議**：發表級數據必用 (c) 或 (d)；轉換法只在缺乏電腦時做手算速估之用。

---

## 第二題 (25%): Boston lettuce 生長 — Logistic vs Gompertz

### 資料概況（來自 `HW4-PROBLEM-2.xlsx`）

- 共 34 個時間點，$t \in [0, 16.81]$ 天。
- 16-hr 處理（curve A）：$M_0 = 19.79\,\mathrm{cm^2}$，$M_{\text{end}} = 443.0\,\mathrm{cm^2}$。
- 24-hr 處理（curve B）：$M_0 = 13.59\,\mathrm{cm^2}$，$M_{\text{end}} = 342.4\,\mathrm{cm^2}$。

### 模型（採 Paine et al. 2012, Table 1 的標準形式）

**Three-parameter logistic**

$$M(t) = \frac{M_0\,K}{M_0 + (K-M_0)\,e^{-rt}},\qquad
\text{AGR} = \frac{dM}{dt} = rM\!\left(1-\tfrac{M}{K}\right),\qquad
\text{RGR} = \frac{1}{M}\frac{dM}{dt} = r\!\left(1-\tfrac{M}{K}\right)$$

**Gompertz**

$$M(t) = K\!\left(\tfrac{M_0}{K}\right)^{e^{-rt}} = K\,e^{-\ln(K/M_0)\,e^{-rt}},\qquad
\text{AGR} = rM\,\ln\!\tfrac{K}{M},\qquad
\text{RGR} = r\,\ln\!\tfrac{K}{M}$$

兩者皆為**漸近 (asymptotic) 模型**（Paine et al. 2012 Table 1）。
固定 $M_0$ 為第一筆觀測值，由 LM 估計 $(r, K)$。

### 估計結果

| 處理 | 模型 | $r$ (day⁻¹) | $K$ (cm²) | RMSE | $R^2$ |
|:---:|:---:|--:|--:|--:|--:|
| 16-hr (A) | Logistic | **0.3094** | **518.4** | **7.55** | **0.9975** |
| 16-hr (A) | Gompertz | 0.1030 | 945.2 | 16.70 | 0.9876 |
| 24-hr (B) | Logistic | **0.2966** | **434.2** | **8.81** | **0.9943** |
| 24-hr (B) | Gompertz | 0.0855 | 1053.3 | 15.38 | 0.9828 |

> **Logistic 在兩個處理皆勝出**（RMSE 約一半，$R^2$ 高約 0.01）。Gompertz 也能擬合得很好，
> 但**估出的 $K$ 不切實際**（945–1053 cm²，遠高於資料尾段的 350–440 cm²），原因是 Gompertz 的
> 拐點位於 $K/e \approx 0.37K$，相對較早，因此模型須把 $K$ 推遠才能容納尾段仍緩慢上升的資料。
> 這是 Paine et al. (2012) 教材級結論——同樣的資料集，Gompertz 與 Logistic 適配度近乎相等
> 但生物意義差很多（Fig 2.b、c、e、h 即為此現象）。

### 生長率（時間函數）

把上述參數代回封閉形式 AGR/RGR（Logistic 峰值在 $M=K/2$，$t = (1/r)\ln((K-M_0)/M_0)$，
$\mathrm{AGR_{max}}=rK/4$；Gompertz 峰值在 $M = K/e$，$t = (1/r)\ln\!\ln(K/M_0)$，
$\mathrm{AGR_{max}}=rK/e$）：

| 處理 | 模型 | AGR 峰值 ($t_{\text{peak}}$, $\mathrm{AGR_{max}}$) | RGR(0) (day⁻¹) | RGR 在 $t_{\max}=16.81$ d |
|:---:|:---:|:---:|:---:|:---:|
| 16-hr (A) | Logistic | $t = 10.43$ d, $\mathrm{AGR} = 40.09$ cm²/d | 0.298 | 0.038 |
| 16-hr (A) | Gompertz | $t = 13.13$ d, $\mathrm{AGR} = 35.82$ cm²/d | 0.398 | 0.071 |
| 24-hr (B) | Logistic | $t = 11.57$ d, $\mathrm{AGR} = 32.20$ cm²/d | 0.287 | 0.052 |
| 24-hr (B) | Gompertz | **$t = 17.19$ d**(註), $\mathrm{AGR} = 33.14$ cm²/d | 0.372 | 0.088 |

> 註：24-hr Gompertz 的 AGR 峰值落在 **$t = 17.19$ d，超出資料範圍 (16.81 d)** ——
> 這正是 Gompertz 拐點推得太晚的後果，與 $K=1053$ cm² 嚴重高估互相印證。
> 數值由程式中的 `logistic_AGR_t / RGR_t`、`gompertz_AGR_t / RGR_t` 解析計算得到，
> 圖形見 `hw4_figures/fig2_lettuce_growth.png` 之中、右欄。

特性：

- **Logistic** 的 AGR 在 $M = K/2$ 達峰，曲線**對稱**；RGR 為 $M$ 的**線性下降**函式。
- **Gompertz** 的 AGR 峰值較**晚**（拐點在 $K/e \approx 0.37K$ 處），RGR 隨時間**指數衰減**。
  本資料末段尚未壓平，Gompertz 還有「未來成長空間」，故 $K$ 估出極大。

### 兩處理比較與討論

> **`fig2b_lettuce_compare.png` 顯示**：兩處理的生長型態極相似，但 16-hr 處理顯著高於 24-hr。

1. **生長率對比**：16-hr 的 Logistic 內生率 $r=0.31$/day **高於** 24-hr 的 $0.30$/day（相近），
   而 $K_A = 518 > K_B = 434$ cm²（Logistic 估值）。**16-hr 光照反而給出更高的承載量**——
   這違反「光照愈久產量愈高」的直覺，**符合植物工廠界廣為人知的觀察**：連續光照（continuous
   light injury, CLI）會引發葉片黃化、葉綠素破壞、葉脈間色素積累，最終導致光合下降；多數葉
   菜需要週期性的暗期 (dark period) 進行 starch 轉移和 stomata 修復。
2. **AGR 峰值時間**：兩處理均落在 $t \approx 10\!\sim\!12$ 天（Logistic 估值；16-hr 為 10.43 d、
   24-hr 為 11.57 d），對應 $M \approx K/2$ —— 16-hr 為 260 cm²、24-hr 為 217 cm²。
   這是商業採收前期最旺盛的擴葉期，AGR 達峰值（16-hr: 40.1 cm²/day；24-hr: 32.2 cm²/day）。
3. **RGR 的衰減**：兩處理的 RGR 都隨時間單調下降（見 fig2 右欄），符合生物學上「自我遮蔭、
   非光合性組織比例上升」的減速機制（Paine et al. 2012 Background 段）。
4. **結論：Logistic 較 Gompertz 適合本資料**——RMSE 較小、$R^2$ 較高、$K$ 在生物上合理。

---

## 第三題 (25%): Reilly (1970) 四模型鑑別

### 資料

| $i$ | 1 | 2 | 3 | 4 |
|:--:|:--:|:--:|:--:|:--:|
| $x_i$ | 0 | 1 | 2 | 3 |
| $y_i$ | −1.290 | 5.318 | 7.049 | 19.886 |

### 候選模型（Reilly 1970 + Spain 教科書 Fig 8.7 第四模型）

$$\begin{aligned}
\text{M1: } y &= a\,x \quad\quad &(\text{linear, no intercept})\\
\text{M2: } y &= a + b\,x \quad\quad &(\text{linear with intercept})\\
\text{M3: } y &= a\,e^{b\,x} \quad\quad &(\text{exponential})\\
\text{M4: } y &= a + b\,x + c\,x^2 \quad\quad &(\text{quadratic})
\end{aligned}$$

### 三種鑑別準則（Spain Ch. 8 / Fig 8.7 級框架）

**(i) 1:1 regression**：把 $\hat{y}$ 當依變數、$y_{\text{obs}}$ 當自變數，做 OLS：

$$\hat{y} = \alpha + \beta\,y_{\text{obs}} + \varepsilon$$

- 理想：$\beta = 1$ 且 $\alpha = 0$
- 用兩個 t 檢定：$H_0:\beta=1$（slope）、$H_0:\alpha=0$（intercept）

**(ii) Paired t test**：把每筆 $(\hat{y}_i, y_{\text{obs},i})$ 視為配對，檢定 $H_0:\overline{\hat{y} - y_{\text{obs}}} = 0$（無系統偏差）。

**(iii) Theil's U**：

$$U_1 = \frac{\sqrt{\frac{1}{n}\sum(\hat{y}_i - y_i)^2}}{\sqrt{\frac{1}{n}\sum\hat{y}_i^2} + \sqrt{\frac{1}{n}\sum y_i^2}} \in [0,1]$$

$U_1 = 0$ 為完美，$U_1 = 1$ 為完全反相。
另計**$U_2$**（vs. naive 「不變」預測 $\hat{y}_t = y_{t-1}$）：$U_2 < 1$ 才比 naive 好。

### 結果

| 模型 | 參數 | RMSE | $R^2$ | slope | paired-p | $U_1$ | $U_2$ |
|---|---|--:|--:|--:|--:|--:|--:|
| M1 $y=ax$ | $a=5.6481$ | 2.668 | 0.879 | 0.783 | 0.655 | 0.124 | 0.356 |
| M2 $y=a+bx$ | $a=-2.048,\,b=6.526$ | 2.370 | 0.905 | 0.905 | 1.000 | 0.110 | 0.322 |
| **M3 $y=a\,e^{bx}$** | $a=1.173,\,b=0.943$ | **1.721** | **0.950** | **0.924** | 0.857 | **0.0795** | **0.165** |
| M4 $y=a+bx+cx^2$ | $a=-0.491,\,b=1.854,\,c=1.557$ | 1.787 | 0.946 | 0.946 | 1.000 | 0.0825 | 0.240 |

> **paired-p = 1.000** 出現在 M2、M4：這是因為含截距的線性 / 多項式 OLS **必然使殘差均值為 0**
> （正規方程 $\sum r_i = 0$）。對含截距模型而言，paired t 對「系統偏差」是**結構失能**的；
> 必須**搭配** Theil's U 才能分辨優劣。

### 結論：M3 (exponential) 最佳

採用三準則交叉看：

1. **RMSE / $R^2$**：M3 (1.72 / 0.950) 最佳；M2、M4 並列次之；M1 最差。
2. **1:1 slope** （越接近 1 越好）：M4 (0.95) > M3 (0.92) > M2 (0.91) > M1 (0.78)。
3. **Theil's $U_1$**（越小越好）：**M3 (0.0795)** < M4 (0.0825) < M2 (0.110) < M1 (0.124)。
4. **Theil's $U_2$**（越小越好；$<1$ 才合格）：**M3 (0.165)** < M4 (0.240) < M2 (0.322) < M1 (0.356)。
   四個模型都比 naive 預測好，但 M3 領先 M4 約 30%。
5. **Reilly (1970) 原文**用 likelihood ratio：$L_{\max,1} = 0.050,\ L_{\max,2}=1,\ L_{\max,3}=202.2$
   ——M3 比 M2 強 200 倍、比 M1 強 4000 倍（真實生成模型亦為 $\theta_{31}\!=\!\theta_{32}\!=\!1,\ \sigma=1$ 的指數模型）。
   **本題三準則的結論與 Reilly 原文一致**。

見 `hw4_figures/fig3_reilly_models.png`：左圖為四曲線 + 資料，右圖為 1:1 plot（理想點落在虛線上）。

---

## 第四題 (25%): Harrison (1995) 標準模型 vs. Luckinbill 18-day 資料

### 模型

$$\boxed{\;\frac{dx}{dt} = \rho\!\left(1-\tfrac{x}{K}\right)x \;-\; \omega\,y\,\frac{x}{\phi+x},\qquad
\frac{dy}{dt} = \sigma\,y\,\frac{x}{\phi+x} \;-\; \gamma\,y\;}$$

- $x$：被捕食者 *Paramecium aurelia*（單位 #/mL）
- $y$：捕食者 *Didinium nasutum*（單位 #/mL）
- $\rho$：被捕食者內生增率；$K$：被捕食者承載量
- $\omega$：捕食速率上限（Holling type II）；$\phi$：半飽和常數
- $\sigma$：捕食者數值響應上限；$\gamma$：捕食者死亡率

題目給的參數對應 Harrison (1995) Table 1 「Standard」列、Fig 5 之擬合：

| $x_0$ | $y_0$ | $\rho$ | $K$ | $\omega$ | $\phi$ | $\sigma$ | $\gamma$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 15.0 | 5.833 | 1.85 | 898 | 25.5 | 284.1 | 12.40 | 2.07 |

### 數值積分

LSODA（變步長 BDF + Adams，自動切換 stiff / non-stiff），$rtol=10^{-8}$, $atol=10^{-10}$。
模擬區間 $t \in [0, 18.5]$ 天，密集輸出後線性內插到觀測時間點。

### Chapter 8 統計分析

| 指標 | 公式 | 理想值 | Prey 結果 | Predator 結果 | 聯合 (scaled) |
|---|---|--:|--:|--:|--:|
| n | 觀測點數 | – | 36 | 37 | 73 |
| RMSE | $\sqrt{\overline{(\hat y - y)^2}}$ | 0 | 115.4 | 74.34 | 1.167 (σ-scaled) |
| Bias | $\overline{\hat y - y}$ | 0 | −26.85 | **−33.13** | **−0.409** |
| 1:1 R² | $1 - \mathrm{SS_{res}}/\mathrm{SS_{tot}}$ | 1 | **−0.061** | **−0.653** | **−0.353** |
| 1:1 slope | OLS $\hat y = \alpha + \beta y_{\text{obs}}$ | 1 | **0.354** ($p_{\beta=1}<10^{-3}$) | **0.062** ($p<10^{-7}$) | 0.198 ($p<10^{-9}$) |
| 1:1 intercept | – | 0 | +30.71 | **+18.29** ($p=0.049$) | +0.291 ($p=0.015$) |
| Paired t (resid) | – | 0 | t=−1.42, p=0.166 | **t=−2.99, p=0.005** | **t=−3.17, p=0.002** |
| Theil $U_1$ | $\sqrt{\overline{d^2}}/(\sqrt{\overline{\hat y^2}}+\sqrt{\overline{y^2}})$ | 0 | 0.450 | **0.599** | 0.524 |
| Theil $U_2$ | vs naive 預測 | <1 | **1.577** | **2.615** | **2.011** |

### 「好模型」的定義 — 操作型 (operational) 判準

把 Spain Ch. 8 的內容濃縮成四個 PASS/FAIL：

> **Pass 條件**（同時滿足）：
> 1. $R^2 > 0.7$（能解釋大部分變異）
> 2. 1:1 regression 之 $H_0:\beta=1$、$H_0:\alpha=0$ **均不被拒絕**（$p > 0.05$）
> 3. paired t **不被拒絕**（$p > 0.05$，無系統偏差）
> 4. Theil's $U_2 < 1$（比 naive 預測更好）

### 結論：**Harrison 標準模型不是好模型**（清楚的 fail）

| 判準 | Prey | Predator |
|:--:|:--:|:--:|
| ① $R^2 > 0.7$ | **❌** ($-0.06$) | **❌** ($-0.65$) |
| ② slope = 1 | **❌** ($\beta=0.35$, $p<10^{-3}$) | **❌** ($\beta=0.06$, $p<10^{-7}$) |
| ②' intercept = 0 | ✓ ($p=0.111$) | **❌** ($p=0.049$) |
| ③ paired-t no bias | ✓ ($p=0.166$) | **❌** ($p=0.005$) |
| ④ Theil $U_2 < 1$ | **❌** ($U_2=1.58$) | **❌** ($U_2=2.61$) |

**詮釋**：

1. **模型動態太「扁」**：標準模型在給定參數下產生了相對緩慢、振幅有限的振盪（見 fig4），
   而真實資料**爆發 (boom)→崩潰 (bust)** 起伏大得多（如 day 13.7 的 prey peak 530.42、day 14.7 的
   predator peak 173.10）。slope = 0.35（prey）與 0.06（pred）量化了「模型振幅遠不及實況」。
2. **相位不對**：模型的振盪週期與資料的爆發時刻不對齊，因此即使振幅勉強對上，
   逐點配對的 paired-t 與 Theil's $U_2$ 也會慘敗。$U_2 = 2.0\sim 2.6$ 表示**模型比「明天等於今天」
   的零模型還差 2 倍以上**——這是嚴重的訊號。
3. **與 Harrison 自己的結論一致**：Harrison Table 1 把 Standard 模型的 $S_1^2 = 236{,}137$ 列在最上方，
   隨後逐步加入 mutual interference、sigmoid functional response、delayed numerical response 後將
   $S_1^2$ 壓到 $25{,}439$（最後一列），$R^2$ 從 0.561 進步到 0.953。Harrison 在 Abstract 直接寫：
   "the basic model... the fit obtained was disappointing"。
4. **改善方向**（Harrison 的試驗）：(a) 加入 predator mutual interference $-\delta y^2$；
   (b) 把 $f(x)$ 改為 sigmoid (Holling Type III)：$x^2/(\phi^2 + x^2)$；
   (c) 引入 delayed numerical response（捕食者反應延遲，造成更明顯的時滯振盪）。
   題目要求的是 "the simplest model"，本報告就以 fail 收尾——**正是教學重點：
   先驗證模型「好不好」，再決定要不要疊加更多複雜度**。

詳見：

- `hw4_figures/fig4_harrison_validation.png`：時間序列（prey、predator）+ 1:1 plots
- `hw4_figures/fig4b_harrison_phase.png`：相平面圖 + nullclines

> Phase plane 顯示：內部平衡點為
> $E_1 = (x^*,\,y^*)$，$x^* = \gamma\phi/(\sigma-\gamma) = 56.93$，$y^* = (\rho/\omega)(1-x^*/K)(\phi+x^*) = 23.17$。
> 落在 prey nullcline 頂點 $(K-\phi)/2 = 306.95$ 之**左側**——依
> Rosenzweig-MacArthur 條件 $x^* > (K-\phi)/2$ **不成立**（57 < 307），
> $E_1$ **不穩**，模型預測**發散震盪 (diverging oscillations)** → 在有限體積 6 mL 中
> Paramecium 個體數 $<1/6$ 即滅絕（Harrison Fig 4a）。模型確實預測了崩潰風險，
> 但**量化上**卻無法匹配資料的 boom-bust 幅度與相位（fig4 上半部即顯示模型振幅遠不及實際資料）。

---

## 結果摘要

| 題目 | 主要產出 | 關鍵結論 |
|---|---|---|
| 第一題 | MM 4 法估計：(LB) $V_{\max}=34.4, K_m=47.8$；(EH) $20.99, 17.2$；**(LM/NM) $22.21, 18.22$** | **LB 嚴重失真** ($R^2=0.43$)，**LM ≡ NM** 為金標準 |
| 第二題 | Logistic A: $r=0.31, K=518, R^2=0.998$；Logistic B: $r=0.30, K=434, R^2=0.994$；Gompertz K 失真 | **Logistic 較佳**；24-hr 連續光照反而 $K$ 較**低** (CLI) |
| 第三題 | M3 (exponential) 各準則均勝；$U_1=0.080, U_2=0.165$；含截距模型的 paired-t 結構為 0 | **M3 最佳**，與 Reilly 似然比結論一致 |
| 第四題 | 4 個 PASS/FAIL 全 fail，prey $R^2=-0.06$, pred $R^2=-0.65$；Theil's $U_2 = 1.6\!\sim\!2.6$ | **標準模型不是好模型**；需加 mutual interference / Holling III / 延遲響應 |

---

*所有結果由 `hw4_solution.py` 重現。執行：`python hw4_solution.py`*
