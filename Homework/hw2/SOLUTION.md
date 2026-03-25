# 作業二解答報告 — 系統動態學與 Forrester 圖

**課程**：BME5113 生物系統建模與分析
**作業**：HW2

---

## 第一題 (25%): Lotka-Volterra Forrester 圖

### 模型方程式

$$V_{t+1} = V_t + rV_t - aV_tP_t$$

$$P_{t+1} = P_t + abV_tP_t - dP_t$$

### 守恆量分析（Conservation Analysis）

題目指定單位為 g C（碳質量），所有物質流（material flow）必須滿足質量守恆（mass balance）。逐項分析碳的來源與去向：

| 項 | 數學式 | 碳的來源 | 碳的去向 | 生物學意義 |
|---|--------|:-------:|:-------:|-----------|
| 獵物繁殖 | $rV$ | 外部環境 | $V$ | 碳經光合作用等途徑進入獵物族群 |
| 捕食消耗 | $aVP$ | $V$ | 分配（見下） | 碳從獵物轉出 |
| 捕食者同化 | $abVP$ | （來自捕食） | $P$ | 被消化吸收的碳轉為捕食者生物量 |
| 代謝損耗 | $a(1{-}b)VP$ | （來自捕食） | 外部環境 | 呼吸、排泄回到環境 |
| 捕食者死亡 | $dP$ | $P$ | 外部環境 | 屍體分解，碳回到環境 |

其中 $b$（conversion efficiency，轉化效率）是個無量綱分數（$0 < b < 1$），代表每吃進 1 g C 的獵物，有 $b$ g C 變成捕食者自己的肉，剩下 $(1-b)$ g C 以呼吸或排泄形式散失。

### Forrester 圖元件清單

**狀態變數 / 存量（Stocks）**

| 符號 | 名稱 | 單位 |
|:----:|------|:----:|
| $V$ | 獵物生物量 (prey biomass) | g C |
| $P$ | 捕食者生物量 (predator biomass) | g C |

**物質流（Material Flows）**

| 編號 | 名稱 | 數學式 | 方向 | 單位 |
|:----:|------|--------|------|:----:|
| F1 | 獵物繁殖 (prey birth) | $rV$ | 外部 → $V$ | g C / time |
| F2 | 捕食 (predation) | $aVP$ | $V$ → 分配點 | g C / time |
| F3 | 同化 (assimilation) | $abVP$ | 分配點 → $P$ | g C / time |
| F4 | 代謝損耗 (metabolic loss) | $a(1{-}b)VP$ | 分配點 → 外部 | g C / time |
| F5 | 捕食者死亡 (predator death) | $dP$ | $P$ → 外部 | g C / time |

**資訊連結（Information Links，虛線箭頭）**

| 從 | 到 | 說明 |
|:--:|:--:|------|
| $V$ | F1 閥 | $V$ 的值決定繁殖流量 $rV$ |
| $V$, $P$ | F2 閥 | 兩者共同決定捕食流量 $aVP$ |
| $P$ | F5 閥 | $P$ 的值決定死亡流量 $dP$ |

### Forrester 圖

見 `hw2_figures/fig1_lotka_volterra.png`。

圖中矩形 = 存量（stock），粗箭頭 = 物質流（material flow），虛線箭頭 = 資訊連結（information link），灰色圓 = 外部源 / 匯（source / sink）。

---

## 第二題 (25%): 樹木碳水動態 Forrester 圖

### 系統概述

模擬一棵中緯度（mid-latitude）樹木在四個月生長季（growing season）中的碳（carbon）與水（water）動態。時間步長為一小時。

### 狀態變數（Stocks）

| 符號 | 名稱 | 單位 | 位置 |
|:----:|------|:----:|:----:|
| $W_r$ | 根部水分 (root water) | g H₂O | 根 |
| $W_l$ | 葉部水分 (leaf water) | g H₂O | 葉 |
| $C_l$ | 葉部糖分 (leaf sugar/carbon) | g C | 葉 |
| $C_r$ | 根部糖分 (root sugar/carbon) | g C | 根 |

### 物質流（Material Flows）

**水循環（Water Cycle）**

| 編號 | 名稱 | 方向 | 驅動因子 |
|:----:|------|------|---------|
| W1 | 根部吸水 (root uptake) | 土壤 → $W_r$ | 土壤含水量、根系面積 |
| W2 | 木質部輸送 (xylem transport) | $W_r$ → $W_l$ | 水勢梯度（water potential gradient） |
| W3 | 蒸散作用 (transpiration) | $W_l$ → 大氣 | 氣孔導度 $g_s$、飽和蒸氣壓差 VPD |

**碳循環（Carbon Cycle）**

| 編號 | 名稱 | 方向 | 驅動因子 |
|:----:|------|------|---------|
| C1 | 光合作用 (photosynthesis) | 大氣 CO₂ → $C_l$ | 光照、CO₂ 濃度、$g_s$ |
| C2 | 韌皮部輸送 (phloem transport) | $C_l$ → $C_r$ | 糖濃度梯度 |
| C3 | 葉呼吸 (leaf respiration) | $C_l$ → 大氣 CO₂ | 溫度、$C_l$ |
| C4 | 根呼吸 (root respiration) | $C_r$ → 大氣 CO₂ | 溫度、$C_r$、O₂ |

### 輔助變數（Auxiliary Variables）

| 符號 | 名稱 | 依賴關係 |
|:----:|------|---------|
| $g_s$ | 氣孔導度 (stomatal conductance) | $g_s = f(W_l)$：葉水分高 → $g_s$ 大；葉水分低 → $g_s$ 小 |
| $A$ | 光合速率 (photosynthesis rate) | $A = f(\text{light}, \text{CO}_2, g_s)$ |
| $T_r$ | 蒸散速率 (transpiration rate) | $T_r = f(g_s, \text{VPD})$ |
| $R_l$ | 葉呼吸速率 (leaf respiration rate) | $R_l = f(\text{temp}, C_l)$ |
| $R_r$ | 根呼吸速率 (root respiration rate) | $R_r = f(\text{temp}, C_r)$ |

> **圖中呈現說明**：Forrester 圖中顯式繪製 $g_s$（氣孔導度）為輔助變數圓形，其餘輔助變數（$A$, $T_r$, $R_l$, $R_r$）隱含在各閥門的控制邏輯中，以保持圖面清晰。

### 外部驅動變數（Exogenous Drivers）

| 變數 | 說明 | 時間尺度 |
|------|------|---------|
| 太陽輻射 (solar radiation) | 光合作用的能量來源 | 日週期 + 季節變化 |
| 光週期 (photoperiod) | 每日日照時數 | 季節（4 個月內顯著改變） |
| 降水量 (precipitation) | 補充土壤水分 | 隨機，季節性趨勢 |
| 氣溫 (temperature) | 影響代謝速率 | 日週期 + 季節 |
| 大氣 CO₂ 濃度 | 光合作用原料 | 近似常數 |

### 關鍵回饋迴路（Feedback Loops）

**氣孔負回饋（Stomatal Negative Feedback）**

這是整個系統中最重要的調控機制：

1. $W_l$ 升高 → $g_s$ 增大 → 蒸散量增加 → $W_l$ 降低（**負回饋**，自我調節）
2. $W_l$ 升高 → $g_s$ 增大 → CO₂ 進入量增加 → 光合速率上升 → $C_l$ 增加

題目描述的兩種情境：
- 葉水分低：氣孔關閉 → 蒸散少（保水）、CO₂ 進入少 → 光合減弱
- 葉水分高：氣孔開啟 → 蒸散多（失水快）、CO₂ 進入多 → 光合旺盛

### Forrester 圖

見 `hw2_figures/fig2_tree_dynamics.png`。

---

## 第三題 (25%): 食物網 Forrester 圖與微分方程式

### 系統假設

| 成分 | 成長 / 消費 | 死亡 |
|------|------------|------|
| $x$（獵物 prey） | 密度依賴成長 (density-dependent growth) | 被 $y$ 和 $z$ 捕食 |
| $y$（捕食者 1, predator 1） | 捕食 $x$，飽和回饋 (saturation feedback) | 常數每人死亡率 (constant per capita) |
| $z$（捕食者 2, predator 2） | 捕食 $x$，固定比例 (fixed fraction) | 負指數每人死亡率 (negative exponential) |

### 功能形式詳解（Functional Forms）

**密度依賴成長（Logistic Growth）**

$$g(x) = rx\!\left(1 - \frac{x}{K}\right)$$

- $r$：獵物內在增長率（intrinsic growth rate）[1/time]
- $K$：環境承載量（carrying capacity）[g C]
- 當 $x$ 小：近似指數增長 $\approx rx$
- 當 $x = K$：淨增長為零
- 當 $x > K$：淨增長為負（過度擁擠）

**飽和回饋（Holling Type II Functional Response）**

每單位 $y$ 對 $x$ 的消費率：

$$h_1(x) = \frac{ax}{h + x}$$

- $a$：最大消費率（maximum consumption rate）[g C / (g C · time)]
- $h$：半飽和常數（half-saturation constant）[g C]，即消費率達一半最大值時的獵物量
- $x \ll h$ 時：$h_1 \approx (a/h)x$（近似線性）
- $x \gg h$ 時：$h_1 \to a$（飽和，再多獵物也吃不了更多——處理時間限制）

**固定比例（Type I / Linear Functional Response）**

每單位 $z$ 對 $x$ 的消費率：

$$h_2(x) = cx$$

- $c$：消費係數 [1/(g C · time)]

**常數死亡率（Constant Per Capita Death Rate）**

$$\mu_y = d_1 \quad [\text{1/time}]$$

每單位時間有固定比例的 $y$ 死亡。

**負指數死亡率（Negative Exponential Per Capita Death Rate）**

$$\mu_z(z) = d_0 \cdot e^{-\gamma z}$$

- $d_0$：基線死亡率 [1/time]（$z \to 0$ 時的死亡率）
- $\gamma$：群聚效應參數 [1/(g C)]
- $z$ 小：$\mu_z \approx d_0$（族群稀少，死亡率高——Allee effect，如找不到配偶）
- $z$ 大：$\mu_z \to 0$（族群充裕，群體中存活率提高——safety in numbers）

### 微分方程式

$$\boxed{\frac{dx}{dt} = rx\!\left(1 - \frac{x}{K}\right) - \frac{ax}{h+x}\,y - cxz}$$

$$\boxed{\frac{dy}{dt} = e_1 \cdot \frac{ax}{h+x}\,y - d_1\,y}$$

$$\boxed{\frac{dz}{dt} = e_2 \cdot cx\,z - d_0\,e^{-\gamma z}\,z}$$

其中 $e_1, e_2$ 為轉化效率（conversion efficiency），$0 < e < 1$，表示每消費 1 g C 獵物有多少轉化為捕食者生物量。

### 碳守恆分析

| 流 | 數學式 | 方向 |
|---|--------|------|
| 獵物成長 | $rx(1 - x/K)$ | 外部 → $x$ |
| $y$ 捕食 | $[ax/(h{+}x)] \cdot y$ | $x$ → 分配 |
| $y$ 同化 | $e_1 [ax/(h{+}x)] y$ | → $y$ |
| $y$ 代謝損耗 | $(1{-}e_1)[ax/(h{+}x)] y$ | → 外部 |
| $z$ 捕食 | $cxz$ | $x$ → 分配 |
| $z$ 同化 | $e_2 cxz$ | → $z$ |
| $z$ 代謝損耗 | $(1{-}e_2)cxz$ | → 外部 |
| $y$ 死亡 | $d_1 y$ | $y$ → 外部 |
| $z$ 死亡 | $d_0 e^{-\gamma z} z$ | $z$ → 外部 |

### Forrester 圖

見 `hw2_figures/fig3_foodweb.png`。

---

## 第四題 (25%): 免疫系統微分方程式

### 變數定義

| 符號 | 名稱 | 單位 |
|:----:|------|:----:|
| $H$ | 健康細胞 (healthy cells) | cells |
| $C$ | 癌細胞 (cancer cells) | cells |
| $M$ | 白血球 M (white blood cell type M) | cells |
| $K$ | 白血球 K (white blood cell type K) | cells |

### 各過程的數學描述

**健康細胞 $H$**

- 自我抑制成長（self-inhibition）：$r_H H(1 - H/T)$
  - 無癌細胞干擾時，$H$ 以邏輯斯成長趨向穩態 $T$
- 被癌細胞殺傷：$-\alpha CH$
  - 質量作用（mass action）：殺傷率正比於 $C$ 和 $H$ 的接觸頻率

**癌細胞 $C$**

- 增殖：$r_C C$（指數增長）
- 被免疫系統殺傷：$-\beta MKC$
  - 題目指定「M 和 K 都必須參與才能成功殺傷」
  - 三體質量作用（three-body mass action）：需要 M、K、C 三者同時碰面

**白血球 $M$**

- 受癌細胞刺激分裂：$\sigma_M CM$
  - 「分裂速率正比於癌細胞數」→ 每人分裂速率 $= \sigma_M C$
- 無癌時指數衰減至基線 $M_0$：$-\delta_M(M - M_0)$
  - 當 $C = 0$ 時 $dM/dt = -\delta_M(M - M_0)$，解為 $M(t) = M_0 + (M(0) - M_0)e^{-\delta_M t}$
  - $M$ 指數衰減至非零基線 $M_0$，符合題意

**白血球 $K$**

結構同 $M$，參數獨立。

### 四條微分方程式

$$\boxed{\frac{dH}{dt} = r_H H\!\left(1 - \frac{H}{T}\right) - \alpha\, C\, H}$$

$$\boxed{\frac{dC}{dt} = r_C\, C - \beta\, M\, K\, C}$$

$$\boxed{\frac{dM}{dt} = \sigma_M\, C\, M - \delta_M\,(M - M_0)}$$

$$\boxed{\frac{dK}{dt} = \sigma_K\, C\, K - \delta_K\,(K - K_0)}$$

### 單位驗證（Dimensional Analysis）

設所有狀態變數單位為 [cells]，時間單位為 [time]。每條方程式的左邊為 [cells/time]，逐項驗證右邊：

**方程式 1：$dH/dt$**

| 項 | 展開 | 參數單位推導 | 結果 |
|---|------|-------------|:----:|
| $r_H H(1{-}H/T)$ | $[r_H] \cdot [\text{cells}] \cdot [\text{無量綱}]$ | $[r_H]$ = 1/time | cells/time ✓ |
| $\alpha CH$ | $[\alpha] \cdot [\text{cells}]^2$ | $[\alpha]$ = 1/(cells·time) | cells/time ✓ |

**方程式 2：$dC/dt$**

| 項 | 展開 | 參數單位推導 | 結果 |
|---|------|-------------|:----:|
| $r_C C$ | $[r_C] \cdot [\text{cells}]$ | $[r_C]$ = 1/time | cells/time ✓ |
| $\beta MKC$ | $[\beta] \cdot [\text{cells}]^3$ | $[\beta]$ = 1/(cells²·time) | cells/time ✓ |

**方程式 3：$dM/dt$**

| 項 | 展開 | 參數單位推導 | 結果 |
|---|------|-------------|:----:|
| $\sigma_M CM$ | $[\sigma_M] \cdot [\text{cells}]^2$ | $[\sigma_M]$ = 1/(cells·time) | cells/time ✓ |
| $\delta_M(M{-}M_0)$ | $[\delta_M] \cdot [\text{cells}]$ | $[\delta_M]$ = 1/time, $[M_0]$ = cells | cells/time ✓ |

**方程式 4：$dK/dt$**

結構同方程式 3。$[\sigma_K]$ = 1/(cells·time)，$[\delta_K]$ = 1/time，$[K_0]$ = cells。✓

### 參數單位匯總

| 參數 | 單位 | 說明 |
|:----:|:----:|------|
| $r_H$ | 1/time | 健康細胞內在成長率 (intrinsic growth rate) |
| $T$ | cells | 健康細胞穩態數量 (homeostatic level) |
| $\alpha$ | 1/(cells·time) | 癌細胞殺傷健康細胞的速率常數 (kill rate constant) |
| $r_C$ | 1/time | 癌細胞增長率 (cancer growth rate) |
| $\beta$ | 1/(cells²·time) | 免疫殺傷速率常數，需 M 和 K 同時作用 |
| $\sigma_M, \sigma_K$ | 1/(cells·time) | 白血球增殖的響應率 (immune response rate) |
| $\delta_M, \delta_K$ | 1/time | 白血球衰減率 (decay rate) |
| $M_0, K_0$ | cells | 白血球基線水準 (baseline level) |

---

## 結果摘要

| 題目 | 主要產出 |
|------|---------|
| 第一題 | Lotka-Volterra Forrester 圖（碳守恆，5 條物質流） |
| 第二題 | 樹木碳水動態 Forrester 圖（4 stocks, 7 flows, 氣孔回饋） |
| 第三題 | 食物網 Forrester 圖 + 3 條 ODE（飽和回饋 + 負指數死亡率） |
| 第四題 | 免疫系統 4 條 ODE + 完整單位驗證（三體質量作用） |

---

*本報告所有 Forrester 圖由 `hw2_solution.py` 產生，輸出於 `hw2_figures/` 目錄。*
