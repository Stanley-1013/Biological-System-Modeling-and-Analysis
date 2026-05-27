# 作業五解答報告 — 誤差傳播、敏感度分析與穩定性分析

**課程**：BME5113 生物系統建模與分析 (Biological Systems Modeling and Analysis)
**作業**：HW5（2025 春季學期，Due 2026-05-28）

> 模擬程式：[hw5_solution.py](hw5_solution.py)，圖檔輸出於 [hw5_figures/](hw5_figures/)
> 教科書原圖佐證放於 [textbook_refs/](textbook_refs/) 目錄。
>
> 本次解答整合 Chapter 9 (Model Analysis: Uncertainty and Behavior) 四個工作流：
> (1) Taylor 一階誤差傳播 → 函數變異數；(2) 單參數擾動 + Monte Carlo →
> 滅絕模型敏感度；(3) Gause 競爭 Case III 局部穩定性；(4) 自訂二維系統的
> nullcline / 等平衡點 / 局部穩定性分析。

---

## 教科書資料對照（嚴格依題目指引）

| 題目 | 對應教科書內容 | 截圖檔 |
|---|---|---|
| P1 | **Eq. 9.3 + Table 9.2**（p.186, p.187）變異數傳播 | [p186_Eq93](textbook_refs/p186_Eq93-199.png)、[p187_Table92](textbook_refs/p187_Table92-200.png) |
| P2 | **Eq. 9.4** $P=(d/b)^n$ 與 **Eq. 9.5** 解析變異數（p.188） | [p188_Eq94_Eq95_extinction](textbook_refs/p188_Eq94_Eq95_extinction-201.png) |
| P3 | **Eq. 9.13–9.14**（Gause 方程，p.198）、**Eq. 9.15–9.18**（平衡點，p.199）、**Eq. 9.40**（Jacobian，p.207）、**Fig. 9.11**（4 案例，p.201）、**p.208 參數表** | [p198_Gause_Eq913_914](textbook_refs/p198_Gause_Eq913_914-211.png)、[p199_Gause_Eq915_918](textbook_refs/p199_Gause_Eq915_918-212.png)、[p201_Fig911_Gause](textbook_refs/p201_Fig911_Gause-214.png)、[p207_Jacobian_Eq940](textbook_refs/p207_Jacobian_Eq940-220.png)、[p208_Gause_Parameters](textbook_refs/p208_Gause_Parameters-221.png) |
| P4 | 同上 Chapter 9.3 工具（nullcline、Jacobian、特徵值） | 同 P3 |

---

## 第一題 (25%): 變異數傳播 (Eq. 9.3 + Table 9.2)

### 通用公式（教科書 Eq. 9.3，p.186）

$$\boxed{\;\mathrm{var}(z)\;\approx\;\sum_{j=1}^{n}\sum_{i=1}^{n}\frac{\partial f}{\partial x_i}\frac{\partial f}{\partial x_j}\;\bigl\langle (x_i-\bar x_i)(x_j-\bar x_j)\bigr\rangle\;}$$

其中對角項 $\langle(x_i-\bar x_i)^2\rangle = \sigma_i^2$、off-diagonal 為 $\sigma_{ij}$（不相關時 $=0$）。

> 推導見 [TUTORIAL §1.1](TUTORIAL.md#11-taylor-一階展開--變異數傳播)；
> Table 9.2 為 $z=x\pm y,\,xy,\,x/y$ 之常用結果（[截圖](textbook_refs/p187_Table92-200.png)）。

---

### (1) $z = e^{k_1 x}$

> 依題目「functions of two variables **(x, y)**」的標示，帶誤差的隨機變數為 $x, y$，
> 參數 $k_i$ 視為常數。本式只含單一隨機變數 $x$，屬**單變數**問題，沒有相關/不相關之分。

$$\frac{\partial z}{\partial x}=k_1\,e^{k_1 x}$$

$$\boxed{\;\sigma_z^{2}\;=\;\left(\frac{\partial z}{\partial x}\right)^{2}\sigma_x^{2}\;=\;k_1^{2}\,e^{2k_1 x}\,\sigma_x^{2}\;}$$

> 物理意義：誤差被 $e^{2k_1 x}$ 放大（指數爆炸），$x$ 的任何小擾動都被指數放大。
> （單變數，無 cross-term。若 $k_1$ 另有不確定性，才需追加 $x^2 e^{2k_1 x}\sigma_{k_1}^2$ 一項。）

---

### (2) $z = k_1\cos(k_2 x) + k_3\sin(k_4 y)$

兩個隨機變數 $x, y$（$k_i$ 為常數）。偏微分：

$$\frac{\partial z}{\partial x}=-k_1 k_2\sin(k_2 x),\qquad \frac{\partial z}{\partial y}=k_3 k_4\cos(k_4 y)$$

**不相關 (uncorrelated)**：
$$\boxed{\;\sigma_z^{2}\;=\;k_1^{2}k_2^{2}\sin^2(k_2 x)\,\sigma_x^{2}\;+\;k_3^{2}k_4^{2}\cos^2(k_4 y)\,\sigma_y^{2}\;}$$

**相關 (correlated)**：增加 cross-term $2(\partial z/\partial x)(\partial z/\partial y)\sigma_{xy}$：
$$\sigma_z^{2}\;=\;k_1^{2}k_2^{2}\sin^2(k_2 x)\,\sigma_x^{2}\;+\;k_3^{2}k_4^{2}\cos^2(k_4 y)\,\sigma_y^{2}\;-\;2\,k_1 k_2 k_3 k_4\,\sin(k_2 x)\cos(k_4 y)\,\sigma_{xy}$$

> cross-term 係數 $-2k_1 k_2 k_3 k_4\sin(k_2 x)\cos(k_4 y)$ 的正負隨 $(x,y)$ 所在相位而定，
> 故 $x,y$ 的相關性可能增大或減小總變異。

---

### (3) $z = x^{3}y^{-3}$

兩個變數：$x, y$。

$$\frac{\partial z}{\partial x}=\frac{3x^{2}}{y^{3}},\qquad \frac{\partial z}{\partial y}=-\frac{3x^{3}}{y^{4}}$$

**不相關**：
$$\boxed{\;\sigma_z^{2}\;=\;\frac{9x^{4}}{y^{8}}\bigl(\,y^{2}\sigma_x^{2}+x^{2}\sigma_y^{2}\,\bigr)\;}\;=\;\frac{9x^{4}\sigma_x^{2}}{y^{6}}+\frac{9x^{6}\sigma_y^{2}}{y^{8}}$$

**相關**：
$$\sigma_z^{2}\;=\;\frac{9x^{4}}{y^{8}}\bigl(\,y^{2}\sigma_x^{2}+x^{2}\sigma_y^{2}-2xy\,\sigma_{xy}\,\bigr)$$

或等價地，用相對誤差形式（除以 $z^2=x^6/y^6$）：

$$\frac{\sigma_z^{2}}{z^{2}}\;=\;9\!\left(\frac{\sigma_x^{2}}{x^{2}}+\frac{\sigma_y^{2}}{y^{2}}-\frac{2\sigma_{xy}}{xy}\right)\;\Longleftrightarrow\;\frac{\sigma_z}{|z|}\;\approx\;3\sqrt{\left(\tfrac{\sigma_x}{x}\right)^{2}+\left(\tfrac{\sigma_y}{y}\right)^{2}-2\rho_{xy}\tfrac{\sigma_x}{x}\tfrac{\sigma_y}{y}}$$

> 對應 Table 9.2 中 $z=x/y$ 之變形（$z=x^3 y^{-3}=(x/y)^3$）；指數 $3$ 把相對誤差乘 3。
>
> **數值範例**（$\bar x=2,\bar y=1,\sigma_x=0.1,\sigma_y=0.05,\sigma_{xy}=0.003$）：
> 程式輸出 $\sigma_z^{2}|_\mathrm{uncorr}=2.88$，$\sigma_z^{2}|_\mathrm{corr}=1.152$；
> 正相關抵銷了 60% 的變異量。

---

## 第二題 (25%): 滅絕模型參數擾動敏感度

### 模型（教科書 Eq. 9.4，p.188）

$$\boxed{\;P\;=\;\left(\frac{d}{b}\right)^{n}\;}$$

其中 $d$ 為死亡率、$b$ 為出生率、$n$ 為初始族群大小。

**參數值**（教科書 p.188 例題表）：

| | $d$ | $b$ | $n$ |
|:---:|:---:|:---:|:---:|
| mean | 0.8 | 0.9 | 10 |
| std. dev. | 0.157 | 0.174 | 0.69 |

$$P_\mathrm{det}\;=\;(0.8/0.9)^{10}\;=\;0.3079$$

### (a) 單參數擾動敏感度 (Eq. 9.1，p.181)

對每個參數，取 ±2%, ±10%, ±20% 三個擾動水準。敏感度指標：

$$S\;=\;\frac{(R_a-R_n)/R_n}{(P_a-P_n)/P_n}$$

| 參數 | level | $R^+$ | $R^-$ | $S^+$ | $S^-$ |
|:--:|:--:|--:|--:|--:|--:|
| **d** | 2%  | 0.3754 | 0.2516 | +10.95 |  +9.15 |
| d     | 10% | 0.7987 | 0.1074 | +15.94 |  +6.51 |
| d     | 20% | 1.9067 | 0.0331 | +25.96 |  +4.46 |
| **b** | 2%  | 0.2526 | 0.3769 | $-$8.98 | $-$11.19 |
| b     | 10% | 0.1187 | 0.8832 | $-$6.14 | $-$18.68 |
| b     | 20% | 0.0497 | 2.8680 | $-$4.19 | $-$41.57 |
| **n** | 2%  | 0.3008 | 0.3153 | $-$1.16 |  $-$1.19 |
| n     | 10% | 0.2737 | 0.3464 | $-$1.11 |  $-$1.25 |
| n     | 20% | 0.2433 | 0.3897 | $-$1.05 |  $-$1.33 |

### 排序（以三個水準、雙方向 $|S|$ 平均）

$$\boxed{\;|S|_b\;\approx\;15.13\;\gtrsim\;|S|_d\;\approx\;12.16\;\gg\;|S|_n\;\approx\;1.18\;}$$

**$P$ 對 $b$ 與 $d$ 同樣高度敏感（$b$ 略高於 $d$），對 $n$ 幾乎不敏感**。

> 細部說明：在小擾動（2%）時 $S_d^+(10.95)$ 甚至略大於 $|S_b^-|(11.19)$；ranking 之所以是
> $b\gtrsim d$ 是因為 $b$ 出現於分母，反向擾動（$b$ 變小）會把 $d/b$ 拉得更大，造成
> 非線性放大。在解析變異數分解中（下節 (b)），兩者實際貢獻分別為 50.7% 與 49.2%
> ——**幾乎並列**。

> 注意三個非線性效應：
> 1. **$S^+ \neq S^-$**：例如 $d$ 在 20% 下 $S^+=25.96$ vs $S^-=4.46$。$P=(d/b)^n$ 在 $d$ 中為冪次函數，
>    $d$ 增加 20% → $(1.2)^{10}\approx 6.2$ 倍；$d$ 減 20% → $(0.8)^{10}\approx 0.107$ 倍。**正向擾動放大，反向擾動壓縮**。
> 2. **$b$ 的反向 $S^-$ 大於正向**：$b$ 出現於分母，減 $b$ 等於把 $d/b$ 倍大，放大效應。
> 3. **$n$ 雖然指數位置，但其變動範圍小**（0.69 vs 平均 10，僅 ±7%）；加上 $(d/b)<1$，$\partial P/\partial n = P\ln(d/b)<0$ 但 $|\ln(0.889)|=0.118$，故敏感度低。

### (b) 解析誤差分析 (Eq. 9.5)

把通用公式 Eq. 9.3 套到 $P=(d/b)^n$：

$$\boxed{\;\mathrm{var}(P)\;=\;\!\left(\frac{n\,\bar d^{\,n-1}}{\bar b^{\,n}}\right)^{\!2}\!\sigma_d^{2}\;+\;\!\left(\frac{n\,\bar d^{\,n}}{\bar b^{\,n+1}}\right)^{\!2}\!\sigma_b^{2}\;+\;\!\left(\ln\!\frac{\bar d}{\bar b}\!\left(\frac{\bar d}{\bar b}\right)^{n}\right)^{\!2}\!\sigma_n^{2}\;}$$

> 教科書 Eq. 9.5 將 $b$-項分子分母各寫一次（$n\bar d^{n}\bar b^{n-1}/\bar b^{2n}$），上式為等價但已化簡的形式。
> 偏導數對應：$\partial P/\partial d = n\bar d^{n-1}/\bar b^n$，$\partial P/\partial b = -n\bar d^n/\bar b^{n+1}$，
> $\partial P/\partial n = (\bar d/\bar b)^n \ln(\bar d/\bar b)$（取平方時負號消失）。

代入數值：$\mathrm{var}(P)=0.720$，$\sigma_P=0.849$，95% CI（常態假設）$=[-1.36,\,1.97]$（顯然超出 $[0,1]$，
反映 Taylor 近似在此處失敗）。

**逐項貢獻**：

| 項 | 數值 | 占比 |
|:--:|--:|--:|
| $d$ 項 | 0.3652 | 50.7% |
| $b$ 項 | 0.3545 | 49.2% |
| $n$ 項 | 0.0006 |  0.1% |

→ 與單參數擾動結論一致：$d$ 與 $b$ 各約占一半，$n$ 微不足道。

### (c) Monte Carlo 對照（教科書 Fig. 9.6 重現）

從 log-normal 分布抽 10,000 個樣本（拒絕 $d\ge b$ 的配對），結果：

| 指標 | 解析 (Eq. 9.5) | Monte Carlo | 教科書值 |
|---|---|---|---|
| Deterministic $P$ | 0.308 | — | 0.308 |
| Mean $P$ | (= 0.308 by 1st-order) | **0.206** | (skewed) |
| Median $P$ | — | 0.094 | (跟 Fig.9.6 一致) |
| Std $P$ | 0.849 | 0.249 | (Fig.9.6 重尾) |
| 95% range | $[-1.36, 1.97]$ | **$[0.001,\,0.883]$** | $[\approx 0.01,\,0.90]$ |

→ 程式輸出見 [fig2_problem2_sensitivity_mc.png](hw5_figures/fig2_problem2_sensitivity_mc.png)。

### 比較結論

1. **同一排序**（敏感度與變異數貢獻）：$d, b \gg n$。
2. **解析法高估變異**：Taylor 一階假設小擾動，但 $\sigma_d/\bar d \approx 20\%$ 已不算小，且
   $P=(d/b)^n$ 在 $d\to b$ 附近梯度爆炸。Monte Carlo 給出 $[0.001, 0.883]$，**仍然太寬**但符合
   邏輯約束 $P\in[0,1]$。
3. **教科書 Fig. 9.6 重現**：分布右尾重、median (0.094) ≪ deterministic (0.308) ≪ analytic CI 上限。
4. **管理意涵**：若我們想用 $P$ 預測族群滅絕，必須**先降低 $b$ 的測量誤差**（CV ≈ 19%）；
   $n$ 的不確定無關緊要。

---

## 第三題 (25%): Gause 競爭 Case III 局部穩定性

### 模型（教科書 Eq. 9.13–9.14，p.198）

$$\begin{aligned}
\frac{dn_1}{dt} &= r_1 n_1\!\left(1-\frac{n_1+\alpha n_2}{K_1}\right) \\
\frac{dn_2}{dt} &= r_2 n_2\!\left(1-\frac{n_2+\beta  n_1}{K_2}\right)
\end{aligned}$$

### 參數（教科書 p.208，但 $K_2,\beta$ 已換）

| $r_1$ | $\alpha$ | $K_1$ | $r_2$ | $\beta$ | $K_2$ |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 0.05 | 0.2 | 200 | 0.05 | **3** | **800** |

### 確認屬 Case III（Fig. 9.11c，p.201）

Case III（穩定共存）條件（[Fig. 9.11c 截圖](textbook_refs/p201_Fig911_Gause-214.png)）：

$$\boxed{\;K_1/\alpha > K_2 \quad\text{且}\quad K_1 < K_2/\beta\;}$$

代入本題參數驗證：

$$K_1/\alpha = 200/0.2 = 1000 > K_2 = 800 \;\;\checkmark,\qquad K_1 = 200 < K_2/\beta = 800/3 \approx 266.7 \;\;\checkmark$$

→ 兩條件成立，**確屬 Case III**。

### 四個平衡點（Eq. 9.17–9.18，p.199）

| label | 座標 | 來源 |
|:--:|:--:|:--:|
| $E_0$ | $(0,0)$ | $n_1$-、$n_2$-nullclines 相交於原點 |
| $E_1$ | $(K_1,0)=(200,0)$ | $n_1=K_1-\alpha n_2$ ∩ $n_2=0$ |
| $E_2$ | $(0,K_2)=(0,800)$ | $n_2=K_2-\beta n_1$ ∩ $n_1=0$ |
| **$E_3$** | $\left(\dfrac{K_1-\alpha K_2}{1-\alpha\beta},\;\dfrac{K_2-\beta K_1}{1-\alpha\beta}\right)=(100,500)$ | 兩條非零 nullclines 交點（Eq. 9.17/9.18） |

驗證：$n_1^* = (200-0.2\cdot 800)/(1-0.6) = 40/0.4 = 100$；$n_2^* = (800-3\cdot 200)/0.4 = 200/0.4 = 500$。

### Jacobian (Eq. 9.40a,b，p.207)

$$\mathbf J = \begin{pmatrix} r_1 - \dfrac{2r_1 n_1}{K_1} - \dfrac{r_1 n_2 \alpha}{K_1} & -\dfrac{r_1 n_1 \alpha}{K_1} \\[3pt] -\dfrac{r_2 n_2 \beta}{K_2} & r_2 - \dfrac{2r_2 n_2}{K_2} - \dfrac{r_2 n_1 \beta}{K_2}\end{pmatrix}$$

### 逐點分析

| 平衡點 | $\mathbf J$ | $\mathrm{tr}$ | $\det$ | 特徵值 $\lambda_{1,2}$ | 類型 |
|---|---|--:|--:|---|---|
| $E_0=(0,0)$ | $\begin{pmatrix}0.05 & 0\\ 0 & 0.05\end{pmatrix}$ | $+0.10$ | $+0.0025$ | $(0.05, 0.05)$ | **unstable node** |
| $E_1=(200,0)$ | $\begin{pmatrix}-0.05 & -0.01\\ 0 & 0.0125\end{pmatrix}$ | $-0.0375$ | $-6.25\!\times\!10^{-4}$ | $(-0.05,\;+0.0125)$ | **saddle** |
| $E_2=(0,800)$ | $\begin{pmatrix}0.01 & 0\\ -0.15 & -0.05\end{pmatrix}$ | $-0.04$ | $-5\!\times\!10^{-4}$ | $(0.01,\;-0.05)$ | **saddle** |
| **$E_3=(100,500)$** | $\begin{pmatrix}-0.025 & -0.005\\ -0.09375 & -0.03125\end{pmatrix}$ | $-0.05625$ | $+3.125\!\times\!10^{-4}$ | **$(-0.00625,\,-0.05)$** | **stable node** |

### 結論

$E_3=(100,500)$ 的兩個特徵值皆為實負（$-0.05,\,-0.00625$，皆 $<0$），

$$\boxed{\;\max(\mathrm{Re}\,\lambda_i)\;=\;-0.00625\;<\;0\;\Longrightarrow\;\text{locally stable (asymptotic)}\;}$$

→ **Case III 確為穩定共存**。

#### 為何穩定？視覺解釋

從 [Fig. 9.11c 截圖](textbook_refs/p201_Fig911_Gause-214.png)：
- $K_1/\alpha > K_2$ → $n_1$ nullcline 在 $n_2$ 軸的截距 ($K_1/\alpha=1000$) 高於 $n_2$ nullcline 在 $n_2$ 軸的截距 ($K_2=800$)
- $K_2/\beta > K_1$ → $n_2$ nullcline 在 $n_1$ 軸的截距 ($K_2/\beta\approx 267$) 高於 $n_1$ 軸截距 ($K_1=200$)
- 兩條斜線在第一象限相交，把空間切成四個區域；每區域的箭頭都指向 $E_3$。

#### 反觀其他 case 為何不穩

- $E_0$：兩物種都還能自由增長（$r_1, r_2 > 0$），所以擾動會推離原點。
- $E_1, E_2$：單物種獨佔的「邊角」均衡。Case III 條件下，另一物種**會入侵**（$\partial f_2/\partial n_2|_{E_1}>0$，意即在 $E_1$ 附近，少量 $n_2$ 會擴增）。

📊 詳見 [fig3_problem3_gause_caseIII.png](hw5_figures/fig3_problem3_gause_caseIII.png)。

---

## 第四題 (25%): 自訂二維系統 — Nullclines + 局部穩定性

### 系統

$$\frac{dx}{dt}=a_1 x^{2}-a_2 x^{3}-bxy,\qquad \frac{dy}{dt}=dxy-fy^{2}$$

參數：$a_1=1,\;a_2=0.05,\;b=5,\;d=1,\;f=10$，定義域 $x\ge 0,\,y\ge 0$。

---

### (1) Nullclines 與向量方向

**$dx/dt = 0$**：
$$x^{2}(a_1-a_2 x)\;-\;bxy=0 \;\Longleftrightarrow\; x\bigl[a_1 x-a_2 x^{2}-by\bigr]=0$$

兩條：
- **N1a**：$x=0$（y 軸）
- **N1b**：$y=\dfrac{a_1 x-a_2 x^{2}}{b}$（拋物線；本題為 $y=(x-0.05x^{2})/5$）

**$dy/dt = 0$**：
$$y(dx-fy)=0$$

兩條：
- **N2a**：$y=0$（x 軸）
- **N2b**：$y=\dfrac{d}{f}x$（過原點直線；本題 $y=x/10$）

---

### 向量方向（代數推導）

#### 在 N1a：$x=0$
$dx/dt=0$，僅看 $dy/dt$：$dy/dt = -fy^{2}\le 0$，當 $y>0$ 嚴格 $<0$。
→ **沿 y 軸恆向下**。

#### 在 N1b：$y=(a_1 x-a_2 x^{2})/b$
$dx/dt=0$，僅看 $dy/dt$。代入：
$$\frac{dy}{dt}=y\!\left[dx-f\cdot\frac{a_1 x-a_2 x^{2}}{b}\right]=\frac{xy}{b}\!\left[bd-fa_1+fa_2 x\right]$$

對本題數值，$bd-fa_1+fa_2 x = 5-10+0.5x = 0.5x-5 = 0.5(x-10)$，故：
$$\frac{dy}{dt}\Big|_{\text{N1b}}\propto\;y\cdot x\cdot (x-10)$$

對 $y>0,\,x>0$：
- $0<x<10$：$dy/dt<0$ → **向下**
- $x>10$：$dy/dt>0$ → **向上**
- $x=10$：$dy/dt=0$（與 N2b 交點，即平衡點）

#### 在 N2a：$y=0$
$dy/dt=0$，僅看 $dx/dt$：
$$dx/dt = a_1 x^{2}-a_2 x^{3}=x^{2}(a_1-a_2 x)$$

對 $x>0$：
- $0<x<a_1/a_2=20$：$dx/dt>0$ → **向右**
- $x>20$：$dx/dt<0$ → **向左**

#### 在 N2b：$y=dx/f$
$dy/dt=0$，僅看 $dx/dt$。代入 $y=dx/f$：
$$\frac{dx}{dt}=a_1 x^{2}-a_2 x^{3}-bx\cdot\frac{dx}{f}=x^{2}\!\left[\,a_1-\frac{bd}{f}\,\right]-a_2 x^{3}$$

對本題：$a_1-bd/f = 1-0.5 = 0.5$；故 $dx/dt = 0.5x^{2}-0.05x^{3}=0.05x^{2}(10-x)$。
- $0<x<10$：$dx/dt>0$ → **向右**
- $x>10$：$dx/dt<0$ → **向左**

📊 整體向量場見 [fig4_problem4_nullclines.png](hw5_figures/fig4_problem4_nullclines.png)。

---

### (2) 平衡點（符號形式）

平衡點 = N1 ∩ N2 的所有組合（在 $x,y\ge 0$ 域內）：

| 標號 | 來源 | 座標（符號） | 代入數值 |
|:--:|:--|:--|:--:|
| $E_0$ | N1a ∩ N2a | $(0,\;0)$ | $(0,\,0)$ |
| $E_1$ | N1b ∩ N2a：$0=a_1 x-a_2 x^{2}$ ⇒ $x=a_1/a_2$ | $\left(\dfrac{a_1}{a_2},\;0\right)$ | $(20,\,0)$ |
| $E_2$ | N1b ∩ N2b：$\dfrac{dx}{f}=\dfrac{a_1 x-a_2 x^{2}}{b}$；除 $x$（$x\neq 0$） | $\left(\dfrac{a_1 f - bd}{a_2 f},\;\dfrac{d(a_1 f-bd)}{a_2 f^{2}}\right)$ | $(10,\,1)$ |

> N1a ∩ N2b 也是 $(0,0)=E_0$（重複），故獨立平衡點共 3 個。
>
> $E_2$ 存在條件：$a_1 f > bd$（本題 $10 > 5$，成立）。

---

### (3) 局部穩定性（代入數值）

Jacobian：
$$\mathbf J(x,y)=\begin{pmatrix}
2a_1 x-3a_2 x^{2}-by & -bx\\[2pt]
dy & dx-2fy
\end{pmatrix}$$

#### $E_0=(0,0)$
$$\mathbf J(0,0)=\begin{pmatrix}0&0\\0&0\end{pmatrix}$$

**所有元素皆 0**，線性化失敗（degenerate / 非雙曲），不能由 Jacobian 判斷。

要看主導項：對 $x>0,\,y>0$ 小，
- $dx/dt\approx a_1 x^{2}>0$ → $x$ 增大
- $dy/dt\approx -fy^{2}<0$ → $y$ 減小

故沿 $y\approx 0$ 軸方向系統推離原點（$x$ 增），$E_0$ **非吸引子**；但不是雙曲意義的「unstable node」。
**結論：non-hyperbolic（退化），但實際行為類似 saddle-like / 不穩定**。

#### $E_1=(20,0)$
$$\mathbf J(20,0)=\begin{pmatrix}2(1)(20)-3(0.05)(400)-5(0) & -5(20)\\ 1(0) & 1(20)-2(10)(0)\end{pmatrix}=\begin{pmatrix}-20 & -100\\ 0 & 20\end{pmatrix}$$

上三角，$\lambda=\mathrm{diag}=(-20,\,20)$。

$$\det = -400 < 0\;\Longrightarrow\;\text{saddle} \quad \Rightarrow\; \text{unstable}$$

#### $E_2=(10,1)$
$$\mathbf J(10,1)=\begin{pmatrix}2(10)-3(0.05)(100)-5(1) & -5(10)\\ 1(1) & 1(10)-2(10)(1)\end{pmatrix}=\begin{pmatrix}0 & -50\\ 1 & -10\end{pmatrix}$$

特徵方程：$\lambda^{2}+10\lambda+50=0\;\Rightarrow\;\lambda=\frac{-10\pm\sqrt{100-200}}{2}=-5\pm 5i$

$$\boxed{\;\mathrm{Re}\,\lambda=-5<0,\;\;|\mathrm{Im}\,\lambda|=5\neq 0\;\Longrightarrow\;\text{stable spiral (focus)}\;}$$

#### 統整

| 平衡點 | 座標 | 特徵值 | 類型 | 穩定？ |
|:--:|:--:|:--:|:--:|:--:|
| $E_0$ | $(0,0)$ | $(0,0)$（線性化失敗） | non-hyperbolic | ✗（不吸引） |
| $E_1$ | $(20,0)$ | $(-20,+20)$ | saddle | ✗ |
| **$E_2$** | $(10,1)$ | $-5\pm 5i$ | **stable spiral** | **✓** |

---

### (4) 為何穩定 / 不穩定（解釋）

#### 為何 $E_2$ 穩定

1. **Hartman-Grobman 定理**：$E_2$ 是雙曲平衡點（$\mathrm{Re}\,\lambda\neq 0$），其局部相軌跡與線性化系統 $\dot{\boldsymbol\xi}=\mathbf J\boldsymbol\xi$ 拓樸等價。
2. $\mathrm{tr}(\mathbf J)=-10<0,\;\det(\mathbf J)=50>0$ → 兩特徵值的實部皆為 $-5/2$ 與... 等等實際是 $\mathrm{tr}/2=-5$。
3. 判別式 $\mathrm{tr}^{2}-4\det = 100-200 = -100<0$ → **複共軛**特徵值 $\Rightarrow$ 螺旋運動。
4. 實部 $-5<0$ → 軌跡向 $E_2$ **內螺旋收斂**，週期 $T=2\pi/|\mathrm{Im}\,\lambda|=2\pi/5\approx 1.257$ 時間單位。

#### 為何 $E_1$ 不穩定 (saddle)

$\mathbf J(E_1)$ 為上三角，兩個對角元素恰為兩個特徵值：$-20$ 與 $+20$，**一正一負**。
- 沿 $\lambda=-20$ 對應的特徵向量（穩定流形）：擾動衰減進入 $E_1$
- 沿 $\lambda=+20$ 對應的特徵向量（不穩定流形）：擾動指數爆炸

**任意微小擾動只要有 $\lambda=+20$ 的方向分量都會逃逸**，故 $E_1$ 不穩。
物理意義：$E_1=(a_1/a_2, 0)$ 是「捕食者滅絕、被捕食者達到密度依賴上限」的邊角平衡；
但 $\partial g/\partial y|_{E_1}=dx-2fy|_{(20,0)}=20>0$ → 少量捕食者一旦出現，會以 $e^{20t}$ 速度爆炸增長，
直到吃掉 $x$ 為止。

#### 為何 $E_0$ 屬於退化

$\mathbf J(E_0)=\mathbf 0$ 是 Jacobian 完全消失的 degenerate 情形。線性化失效時，須回歸**非線性主導項**：
- $\dot x = a_1 x^{2}$：對 $x>0$ 為正，遠離 0
- $\dot y = -fy^{2}$：對 $y>0$ 為負，趨近 0

故 $E_0$ 沿 $x$ 方向不穩，沿 $y$ 方向（但仍在第一象限）穩。屬於**半穩定 / 退化** 平衡點，
數值積分顯示軌跡會被推離 $E_0$ 並進入 $E_2$ 的吸引域。

#### 整體相圖

$E_2=(10,1)$ 是唯一的吸引子；幾乎所有從第一象限的軌跡都會螺旋進入它。
$E_1=(20,0)$ 與 $E_0=(0,0)$ 只是不穩定的邊角平衡，分隔吸引域邊界。
（見 [fig4_problem4_nullclines.png](hw5_figures/fig4_problem4_nullclines.png) 的流線視覺化驗證了
這一點。）

---

## 結論一覽

| 題 | 結論 | 關鍵數字 |
|:-:|:--|:--|
| P1 | 用 Eq. 9.3 (Taylor 一階) 推三式之 var(z)；$x,y$ 為隨機變數、$k_i$ 為常數 | (1) 單變數無 cross-term；(2)(3) 給 uncorr/corr 兩式，與 Table 9.2 一致 |
| P2 | 敏感度排序 **$b>d\gg n$**；解析 var(P)=0.72；MC 重現教科書 Fig. 9.6 | $S_b\!\approx\!15,\;S_d\!\approx\!12,\;S_n\!\approx\!1$ |
| P3 | Case III 共存點 $(100, 500)$ **穩定** | $\lambda=(-0.05,-0.006)$ 皆負 |
| P4 | $(10,1)$ 為唯一穩定螺旋焦點；$(20,0)$ 為 saddle；$(0,0)$ 退化 | $E_2$: $\lambda=-5\pm 5i$ |

---

## 附錄：執行方式

```bash
cd Homework/hw5
python hw5_solution.py
```

依賴：`numpy sympy matplotlib scipy`。輸出於 [hw5_figures/](hw5_figures/) 與 stdout。

完整解析推導參見 [TUTORIAL.md](TUTORIAL.md)；手寫繳交精簡版見 [HANDWRITTEN.md](HANDWRITTEN.md)。
