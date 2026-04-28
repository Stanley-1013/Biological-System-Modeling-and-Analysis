# 從零開始學參數估計、生長模型與模型鑑別
## — BME5113 HW4 完整教學指南

> 本文件從基礎概念出發，帶你理解：(1) 為什麼線性化轉換常常騙人，(2) 怎麼選 logistic vs Gompertz，
> (3) 模型鑑別的三種統計工具如何互補，(4) 怎麼用 Chapter 8 的判準判斷一個動力學模型「好不好」。
> 假設你會基礎微積分、機率與統計（t 檢定、最小平方），但對非線性回歸與生態模型驗證較陌生。

---

## 目錄

1. [第一章：Michaelis-Menten 與線性化的陷阱](#第一章michaelis-menten-與線性化的陷阱)
2. [第二章：Levenberg-Marquardt vs Nelder-Mead](#第二章levenberg-marquardt-vs-nelder-mead)
3. [第三章：植物生長模型 — Logistic 與 Gompertz](#第三章植物生長模型--logistic-與-gompertz)
4. [第四章：AGR 與 RGR — 為什麼要用模型推導](#第四章agr-與-rgr--為什麼要用模型推導)
5. [第五章：模型鑑別 — 1:1、paired t、Theil's U](#第五章模型鑑別--11paired-ttheils-u)
6. [第六章：Chapter 8 模型驗證的工作流](#第六章chapter-8-模型驗證的工作流)
7. [第七章：Predator-Prey 的標準模型與其極限](#第七章predator-prey-的標準模型與其極限)
8. [附錄：常見錯誤](#附錄常見錯誤)

---

## 第一章：Michaelis-Menten 與線性化的陷阱

### 1.1 公式回顧

Michaelis-Menten (MM) 為酵素動力學/捕食率/受體飽和最常見的飽和函式：

$$v(S) = \frac{V_{\max}\,S}{K_m + S}$$

- $S \to 0$：$v \approx (V_{\max}/K_m)\,S$（線性段，斜率 = $V_{\max}/K_m$）
- $S \to \infty$：$v \to V_{\max}$（飽和段）
- $S = K_m$：$v = V_{\max}/2$（半飽和點，這就是 $K_m$ 的物理意義）

### 1.2 三種線性化轉換

歷史上沒有電腦的年代，研究者把 MM 改寫成「直線」以便用尺、紙做 OLS。

**Lineweaver-Burke (LB)**：取倒數
$$\frac{1}{v} = \frac{K_m}{V_{\max}}\cdot\frac{1}{S} + \frac{1}{V_{\max}}$$

對 $(1/S, 1/v)$ 做直線回歸 → slope = $K_m/V_{\max}$, intercept = $1/V_{\max}$。

**Eadie-Hofstee (EH)**：先乘 $K_m+S$，再整理
$$v = V_{\max} - K_m\cdot\frac{v}{S}$$

對 $(v/S, v)$ 做直線回歸 → slope = $-K_m$, intercept = $V_{\max}$。

**Hanes-Woolf**（本作業未要求，但完整提及）：
$$\frac{S}{v} = \frac{1}{V_{\max}}\,S + \frac{K_m}{V_{\max}}$$

### 1.3 為什麼 LB 會嚴重失真？

關鍵洞察：**OLS 假設依變數有等變異數誤差**（homoscedastic）。

原始空間：$v_i = v_{\text{true},i} + \varepsilon_i$，$\varepsilon \sim \mathcal{N}(0,\sigma^2)$。

倒數後：
$$\frac{1}{v_i} = \frac{1}{v_{\text{true},i} + \varepsilon_i} \approx \frac{1}{v_{\text{true},i}}\cdot\!\left(1 - \frac{\varepsilon_i}{v_{\text{true},i}}\right)$$

倒數的誤差變成 $\varepsilon_i / v_{\text{true},i}^2$ —— **小的 $v$ 值（低 $S$ 點）誤差被放大成天文數字**。
OLS 會把擬合重心壓到那幾個最不可靠的點上。

📊 **本作業實際數值**（見 SOLUTION.md 第一題表）：

| 法 | $V_{\max}$ | $K_m$ | $R^2$ |
|---|--:|--:|--:|
| LB | 34.4 | 47.8 | 0.43 |
| EH | 21.0 | 17.2 | 0.94 |
| LM/NM | 22.2 | 18.2 | 0.95 |

**LB 給出的 $K_m$ (47.8) 比真實值 (18.2) 高出 2.6 倍**。這在臨床藥動學會直接造成劑量誤判。

### 1.4 EH 為什麼比 LB 好但仍非無偏？

EH 的 $v/S$ 與 $v$ 都含 $v$ 的誤差，因此「誤差不對稱」沒那麼極端。但問題是 **$y$-軸不獨立於 $x$-軸**
（$v$ 同時出現），違反 OLS 對「自變數無誤差」的根本假設。

> 結論：**任何含 $v$ 同時出現於兩軸的線性化都是偏估**。教科書還是寫，但只當作教學或手算速估。

### 1.5 標準做法

在所有的真實研究：**直接對原方程式做非線性最小平方**：

$$\min_{V_{\max}, K_m}\;\sum_i\bigl(v_i - \tfrac{V_{\max}S_i}{K_m+S_i}\bigr)^2$$

下章解釋 LM 與 NM 兩個求解器。

---

## 第二章：Levenberg-Marquardt vs Nelder-Mead

### 2.1 Levenberg-Marquardt (LM) — Gauss-Newton + 阻尼

對殘差向量 $\mathbf{r}(\boldsymbol\theta) = (v_i - \hat v_i)$，目標函式 $\|\mathbf{r}\|^2$。
記 Jacobian $\mathbf{J} = \partial\mathbf{r}/\partial\boldsymbol\theta$。

Gauss-Newton 步：$\Delta\boldsymbol\theta = -(\mathbf{J}^\top\mathbf{J})^{-1}\mathbf{J}^\top\mathbf{r}$。

Marquardt 補上**阻尼項** $\lambda\,\mathbf{I}$：

$$\Delta\boldsymbol\theta = -(\mathbf{J}^\top\mathbf{J} + \lambda\,\mathbf{I})^{-1}\mathbf{J}^\top\mathbf{r}$$

- $\lambda$ 大（不好）→ 退化為梯度下降的小步長
- $\lambda$ 小（好）→ 退化為 Gauss-Newton 的快速收斂

每步試走一下：若 SSE 下降 → 縮小 $\lambda$（更激進）；若上升 → 放大 $\lambda$（更保守）。

**優點**：對小至中等規模的非線性最小平方**收斂極快**。
**缺點**：需要 Jacobian（自動或數值差分），在不可微 / 不光滑問題會崩。

`scipy.optimize.curve_fit` 預設即為 LM；可以放心用。

### 2.2 Nelder-Mead (NM) — 無導數的 simplex

簡單講：在 $n$ 維空間維護 $n+1$ 個點構成的單純形 (simplex)，**比較目標值並做反射、擴張、收縮、縮減**。

**優點**：不需要導數；對不光滑、不可微、有雜訊的目標也能跑。
**缺點**：高維下收斂慢；極小值附近可能停滯（特別是 $n > 10$）。

對 MM 這種 2 維問題，NM 跟 LM **應收斂到同一個極小值**——本作業的數值結果完全相同。
**實作意義**：可以**互相驗證**——若兩者結果不同，多半是初始猜測差或目標有多個局部極小。

### 2.3 何時選哪個？

| 情境 | LM | NM |
|---|---|---|
| 標準非線性最小平方 | ✓ 最快 | △ 也行 |
| 目標含 abs/max/min | ✗ 不可微 | ✓ |
| 目標含模擬輸出（離散） | ✗ Jacobian 雜訊 | ✓ |
| 高維 (>20) | ✓ | ✗ 太慢 |
| 必須限制 $\theta > 0$ | △ 用 Trust Region | ✓ 加 penalty |

---

## 第三章：植物生長模型 — Logistic 與 Gompertz

### 3.1 為什麼不用「指數」或「線性」？

線性 ($M = M_0 + rt$)：AGR 恆定 → 不切實際（從種子到收穫不會永遠等速）。
指數 ($M = M_0 e^{rt}$)：RGR 恆定 → 早期可以、後期飽和不對。

Paine et al. (2012) Fig 1 點出：**真實植物的 RGR 幾乎都隨時間下降**（自我遮蔭、非光合性組織比例上升、養分受限），所以要用**漸近 (asymptotic) 模型**。

### 3.2 三-參數 Logistic（Verhulst 1838）

$$M(t) = \frac{M_0\,K}{M_0 + (K - M_0)\,e^{-rt}}$$

性質：
- $M(0) = M_0$（直接從第一筆觀測決定）
- $M(\infty) \to K$（漸近承載量）
- 拐點 (inflection) 在 $M = K/2$，AGR 最大
- 曲線**對稱於拐點**

ODE 形式：
$$\frac{dM}{dt} = r\,M\!\left(1 - \tfrac{M}{K}\right)$$

### 3.3 Gompertz (1825)

$$M(t) = K\!\left(\tfrac{M_0}{K}\right)^{e^{-rt}} = K\,e^{-\ln(K/M_0)\,e^{-rt}}$$

性質：
- $M(0) = M_0$；$M(\infty) \to K$
- 拐點在 $M = K/e \approx 0.37\,K$（**比 logistic 早**）
- **不對稱**：早期成長更快、後期減速更慢

ODE 形式：
$$\frac{dM}{dt} = r\,M\,\ln\!\tfrac{K}{M}$$

### 3.4 兩者的選擇

Paine et al. (2012) Fig 2(b)：在 *Cerastium* 資料上，兩個模型擬合度幾乎相同（$\Delta\text{AIC}$ 只差 1）。
但 Gompertz 估出的 K 與 logistic 不一樣——**生物意義不同**。

📊 **本作業 16-hr lettuce**：

| 模型 | $r$ (1/d) | $K$ (cm²) | RMSE | $R^2$ |
|---|--:|--:|--:|--:|
| Logistic | 0.31 | **518** | 7.5 | 0.998 |
| Gompertz | 0.10 | **945** | 16.7 | 0.988 |

Gompertz 的 $K = 945$ cm² 太大——資料尾段已 plateau 在 $\sim 440$ cm²，**生物上不合理**。
原因：Gompertz 拐點 $K/e \approx 350$，但資料拐點實測在 $\sim 250$，模型須把 $K$ 推遠才能容納。

> **規則**：當資料**有清楚 plateau** 且 plateau 落在拐點之後 $> 1.5\times$ → Logistic 較佳；
> 當資料**早期爆發、後期長尾** → Gompertz 較佳。

### 3.5 多個物種比較時的注意事項

不要只看 AIC：兩個模型的 $r$、$K$ 意義不同，無法直接比較。Paine et al. (2012) 建議：
**先決定模型，再比較參數或生長率**（比參數值差更容易 communicate）。

---

## 第四章：AGR 與 RGR — 為什麼要用模型推導

### 4.1 傳統定義

- **絕對生長率 (Absolute Growth Rate, AGR)**：$\dfrac{dM}{dt}$，單位 g/day 或 cm²/day。
- **相對生長率 (Relative Growth Rate, RGR)**：$\dfrac{1}{M}\dfrac{dM}{dt}$，單位 1/day。

### 4.2 「逐日差分法」的問題

最樸素的計算：

$$\widehat{\text{AGR}}(t_i) \approx \frac{M_{i+1} - M_{i-1}}{t_{i+1} - t_{i-1}},\qquad
\widehat{\text{RGR}}(t_i) \approx \frac{\ln M_{i+1} - \ln M_{i-1}}{t_{i+1} - t_{i-1}}$$

**問題**：
1. 對量測雜訊**極敏感**——任何測量誤差直接放大為斜率誤差
2. 假設**樣本之間 RGR 不變**，但 RGR 通常隨時間單調下降
3. 樣本不足時，斜率估計**極不穩**

### 4.3 模型推導 (function-derived) 法

先擬合好參數模型，再對解析式求導：

**Logistic AGR/RGR**：

$$\text{AGR}(t) = r\,M(t)\!\left(1-\tfrac{M(t)}{K}\right),\qquad
\text{RGR}(t) = r\!\left(1-\tfrac{M(t)}{K}\right)$$

**Gompertz AGR/RGR**：

$$\text{AGR}(t) = r\,M(t)\,\ln\!\tfrac{K}{M(t)},\qquad
\text{RGR}(t) = r\,\ln\!\tfrac{K}{M(t)}$$

**好處**：
- **平滑、無雜訊**
- 可以**估在任意時間或大小**——不需資料點剛好在那
- 可以做**不確定性傳播**（從參數的協方差到 AGR/RGR 的標準誤）

### 4.4 RGR 的時間 vs 質量座標

Paine et al. (2012) 強調：**比較不同物種時，固定時間不公平**（早晚期物種混在一起）。
應**比較相同 $M$ 值的 RGR**：

$$\text{RGR}(M) = r\!\left(1 - \tfrac{M}{K}\right)\ \text{(logistic)},\qquad
\text{RGR}(M) = r\,\ln\!\tfrac{K}{M}\ \text{(Gompertz)}$$

兩種座標各有用途：
- **時間座標**：分析發育動力學（峰值時間、總生長期）
- **質量座標**：跨物種比較（標準化 ontogeny）

---

## 第五章：模型鑑別 — 1:1、paired t、Theil's U

### 5.1 1:1 regression（標準型）

把 $\hat y$（model）當依變數，$y_{\text{obs}}$ 當自變數，做 OLS：

$$\hat y = \alpha + \beta\,y_{\text{obs}} + \varepsilon$$

**理想模型**：$\alpha = 0$（無常數偏移）、$\beta = 1$（無比例縮放偏差）。

兩個 t 檢定：

$$t_\beta = \frac{\hat\beta - 1}{\mathrm{SE}(\hat\beta)},\qquad
t_\alpha = \frac{\hat\alpha - 0}{\mathrm{SE}(\hat\alpha)}$$

$|t| > t_{n-2,0.025}$（雙尾 5%）→ 拒絕，模型有顯著偏差。

📊 **本作業第三題 M3 範例**：$\hat\beta = 0.924, \mathrm{SE} = 0.148, t = -0.51, p = 0.66$
→ 不拒絕 $\beta = 1$，模型對「比例正確性」沒有顯著偏差。

### 5.2 Paired t test

把每一筆 $(\hat y_i, y_i)$ 視為配對，檢定：

$$H_0: \mathbb{E}[d_i] = 0,\quad d_i = \hat y_i - y_i$$

$$t = \frac{\bar d}{s_d / \sqrt n},\qquad s_d^2 = \frac{1}{n-1}\sum(d_i - \bar d)^2$$

⚠️ **陷阱**：對**含截距的線性回歸 / 多項式擬合**，OLS 正規方程強迫殘差均值為 0
（$\sum d_i = 0$），所以 paired-t 永遠 = 0、p = 1。
這時 paired-t **失能**，必須改看 1:1 slope 或 Theil's U。

### 5.3 Theil's U（兩種變體）

#### Theil's $U_1$（inequality coefficient）

$$U_1 = \frac{\sqrt{\frac{1}{n}\sum(\hat y_i - y_i)^2}}{\sqrt{\frac{1}{n}\sum\hat y_i^2} + \sqrt{\frac{1}{n}\sum y_i^2}} \in [0, 1]$$

- $U_1 = 0$：完美擬合
- $U_1 = 1$：完全反相
- 通常 $U_1 < 0.3$ 算可接受

#### Theil's $U_2$（vs naive 預測）

$$U_2 = \sqrt{\frac{\sum_{t=2}^n(\hat y_t - y_t)^2}{\sum_{t=2}^n(y_t - y_{t-1})^2}}$$

意義：與「naive 預測 $\hat y_t = y_{t-1}$」比較。

- $U_2 < 1$：模型優於 naive
- $U_2 = 1$：與 naive 等同
- $U_2 > 1$：**比 naive 還差**（模型顯然有問題！）

📊 **本作業第四題 Harrison 模型**：predator $U_2 = 2.61$
→ 模型比「明天等於今天」的預測**還差 2.6 倍** → 嚴重不及格。

### 5.4 三準則互補

| 準則 | 抓什麼 | 失能情境 |
|---|---|---|
| 1:1 slope/intercept | 系統比例 / 偏移偏差 | 殘差全 0 時退化（但 $\hat\alpha=0,\hat\beta=1$ 仍可信） |
| paired t | 平均偏差 | 含截距 OLS 結構為 0 |
| Theil's $U_1, U_2$ | 整體配對接近度 | 對相位錯配 (phase) 較敏感 |

**最佳實踐**：**三項一起報告**，互相佐證。

---

## 第六章：Chapter 8 模型驗證的工作流

### 6.1 操作型「好模型」定義

把 Spain Ch. 8 的精神濃縮為四個 PASS/FAIL：

> 1. $R^2 > 0.7$（可解釋大部分變異；越高越好）
> 2. 1:1 slope 與 intercept 之 t 檢定 **均不拒絕**（$p > 0.05$）
> 3. paired-t **不拒絕**（無系統偏差，含截距模型不適用）
> 4. Theil's $U_2 < 1$（比 naive 預測好；越小越好）

### 6.2 失敗時的下一步

通常按 Harrison (1995) 的階梯：

| 階段 | 做什麼 |
|---|---|
| 1 | 加入 mutual interference（捕食者個體之間的干擾） |
| 2 | 把 Holling Type II 換成 Type III（sigmoid functional response） |
| 3 | 加入捕食者數值響應的延遲（delayed numerical response） |
| 4 | 加入捕食者的 nutrient/energy 儲備 (state-variable predator)：把 $y$ 拆成 \"flesh\" + \"reserve\" |

每階段重做 6.1 的 4 項判準；若 $U_2 < 1$ 達成、$R^2$ 上升、paired-t 不顯著，就停止。

### 6.3 為什麼不直接拿 SSE 比較？

SSE 或 RMSE 本身**沒有絕對意義**——換尺度（log $\to$ 原始）就會變很多。
而 $R^2$、Theil's U 都是**無量綱**比例，對尺度不敏感，可跨資料集比較。

---

## 第七章：Predator-Prey 的標準模型與其極限

### 7.1 Lotka-Volterra → Rosenzweig-MacArthur

**LV (1925, 1926)**：
$$\frac{dV}{dt} = rV - aVP,\qquad \frac{dP}{dt} = abVP - dP$$
週期振盪，但**任何擾動都改週期**——不穩定中性中心 (neutral center)。

**Rosenzweig-MacArthur (1963)**：加上 prey carrying capacity $K$ 與 Holling Type II 飽和：

$$\frac{dx}{dt} = \rho\!\left(1-\tfrac{x}{K}\right)x - \omega\frac{xy}{\phi+x},\qquad
\frac{dy}{dt} = \sigma\frac{xy}{\phi+x} - \gamma y$$

這就是 Harrison (1995) Eqs. 1-3，也就是本作業的「標準模型」。

### 7.2 平衡點與穩定性

**Prey nullcline** ($dx/dt = 0$，且 $x \neq 0$)：

$$y = \frac{\rho}{\omega}\!\left(1-\tfrac{x}{K}\right)(\phi + x)$$

這是一條**凹下拋物線**，頂點在 $x = (K-\phi)/2$，與 $x$-軸的交點為 $x = K$。

**Predator nullcline** ($dy/dt = 0$, $y \neq 0$)：

$$x = x^* = \frac{\gamma\phi}{\sigma - \gamma}\quad (\text{vertical line})$$

兩線相交於內部平衡點 $E_1 = (x^*, y^*)$，其中 $y^* = (\rho/\omega)(1-x^*/K)(\phi+x^*)$。

**穩定性條件 (Rosenzweig-MacArthur)**：

$$E_1 \text{ stable} \iff x^* > \frac{K-\phi}{2}\quad (\text{predator nullcline 在 prey nullcline 頂點右側})$$

### 7.3 Harrison 的試驗結果（為何標準模型不夠）

代入本作業參數：$x^* = (2.07)(284.1)/(12.40-2.07) = 56.94$，$(K-\phi)/2 = 306.95$。

$x^* = 57 < 307$ → **$E_1$ 不穩**，理論上發散震盪。

📉 但 Harrison 的 $S_1^2 = 236{,}137$ 顯示**振盪不夠大**——量化上模型振幅不及實際資料的 boom-bust 幅度。

➡️ 改進方向（Harrison 後續模型）：

1. **Mutual interference** $-\delta y^2$：抑制高密度捕食者效率，讓捕食者 peak 變平、振盪更穩。
2. **Sigmoid (Type III) response** $\omega x^2/(\phi^2 + x^2)$：低密度時捕食者放棄搜尋（refuge effect），讓 prey 有翻身空間。
3. **Delayed numerical response**：捕食者反應有時滯——產生延遲微分方程：
   $$\frac{dy}{dt} = \sigma\,y(t-\tau)\frac{x(t-\tau)}{\phi+x(t-\tau)} - \gamma y(t)$$
   時滯會擴大振盪振幅。
4. **State-structured predator**：把 $y$ 分為 flesh + reserve，捕食速率與 reserve 相關。
   Harrison 的最佳模型即此類，$S_1^2 = 25{,}439$，比 Standard 小 9 倍。

### 7.4 為什麼這對工程師重要？

**驗證 (validation) 與校準 (calibration) 是兩件事**：

- 校準：找參數讓 SSE 最小（Harrison 已做）
- 驗證：問「最佳擬合的模型結構是否能重現資料的關鍵動態」

本作業要做的是**驗證**——即使參數已調到最佳，模型結構仍可能「**根本錯**」。
這是工程實務中最常被忽視的步驟，也是 Chapter 8 想教的核心訊息。

---

## 附錄：常見錯誤

### A.1 用 LB 求 MM 然後不檢查殘差

LB 給的 $K_m$ 常常是真實值的 2-3 倍。**永遠用 LM 或 NM 重做一遍**確認。

### A.2 把 Logistic 與 Gompertz 的 $r$ 直接比較

兩者的 $r$ **單位都是 1/day，但意義不同**——logistic 的 $r$ 是內生增率（$M\to 0$ 時的 $\dot M / M$），Gompertz 的 $r$ 是 $\ln(K/M)$ 的衰減率。**不能直接比大小**。

### A.3 拿微分商當 RGR 並丟進統計檢定

逐日差分的 RGR 雜訊極大，做 t 檢定統計力 (power) 趨近於 0。**先擬合曲線，再從曲線取導**。

### A.4 用 paired-t 否定 OLS 含截距模型

含截距的 OLS 必滿足 $\sum d_i = 0$，paired-t 永遠 ≈ 0。看到 $p = 1$ 不要以為「模型完美」——
那只是 OLS 的代數恆等式。**改看 Theil's U 才有效**。

### A.5 看到 Theil's $U_1 < 0.1$ 就放心

$U_1$ 對**相位錯配 (phase shift) 較不敏感**：兩條相同振幅但 180° 相位差的曲線 $U_1$ 仍小。
**配 $U_2$ 一起看**：若 $U_2 > 1$（比 naive 還差），$U_1$ 看起來再低也是假象。

### A.6 把模型擬合度當作模型驗證

擬合度 ($R^2$ 在訓練資料上) **永遠隨參數增加而上升**（過度擬合 / overfitting）。
真正的驗證需要**獨立資料**或**交叉驗證**。本作業 Reilly 第三題僅 4 點 + 4 模型已過度擬合
（M4 含 3 參數、4 點），$R^2$ 看起來很高但其實沒有自由度。

### A.7 Harrison 模型的「相位扁平」陷阱

Standard 模型的振盪頻率 $\omega \approx \sqrt{\rho\gamma}$，週期約 $T \approx 2\pi/\omega$。
若資料的真實週期比模型短/長，**任何參數調整都救不回來**——必須改結構（加延遲、改 functional response 等）。
這就是為什麼 Harrison 從 Eqs. 1-3 升級到延遲微分方程才得到好擬合。

---

*本教學對應程式 `hw4_solution.py` 與報告 `SOLUTION.md`。*
