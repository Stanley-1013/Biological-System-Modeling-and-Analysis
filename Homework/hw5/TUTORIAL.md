# 從零開始學誤差傳播、敏感度分析與穩定性分析
## — BME5113 HW5 完整教學指南

> 本文件從基礎概念出發，帶你理解：(1) 為什麼 Taylor 一階就能算變異數，(2) 單參數擾動 vs Monte Carlo
> 的優缺，(3) 怎麼用 Jacobian + 特徵值判斷穩定性，(4) Gause 競爭與一般 2-D 系統的 nullcline 分析。
> 預設你會基礎微積分、線代（特徵值）、機率（變異數、共變異），但對誤差傳播與相平面分析較陌生。

---

## 目錄

1. [第一章：Taylor 一階展開 → 變異數傳播](#第一章taylor-一階展開--變異數傳播)
2. [第二章：Table 9.2 速查表怎麼推](#第二章table-92-速查表怎麼推)
3. [第三章：單參數擾動敏感度 (Eq. 9.1)](#第三章單參數擾動敏感度-eq-91)
4. [第四章：解析誤差分析 vs Monte Carlo](#第四章解析誤差分析-vs-monte-carlo)
5. [第五章：nullcline 與相平面](#第五章nullcline-與相平面)
6. [第六章：Jacobian + 特徵值 = 局部穩定性](#第六章jacobian--特徵值--局部穩定性)
7. [第七章：Gause 競爭模型的四種 case](#第七章gause-競爭模型的四種-case)
8. [附錄：常見錯誤與陷阱](#附錄常見錯誤與陷阱)

---

## 第一章：Taylor 一階展開 → 變異數傳播

### 1.1 為什麼需要

實驗中我們量到 $\bar x \pm \sigma_x$、$\bar y \pm \sigma_y$，但模型輸出是 $z = f(x, y)$。
問題：$\sigma_z$ 多少？這就是**誤差傳播 (error propagation)** 問題。

### 1.2 Taylor 一階（Eq. 9.2，p.185）

對一個變數的單值函數 $f(x)$，在 $x=a$ 處展開：
$$f(x) = f(a) + f'(a)(x-a) + \frac{f''(a)}{2!}(x-a)^{2} + \cdots$$

對「小擾動」假設，**只保留一階項**：
$$f(x) \approx f(a) + f'(a)(x-a)$$

對多變數 $f(x_1, \ldots, x_n)$，類比擴展：
$$f(\mathbf x) \approx f(\bar{\mathbf x}) + \sum_i \frac{\partial f}{\partial x_i}\bigg|_{\bar{\mathbf x}}(x_i - \bar x_i)$$

### 1.3 從 Taylor 到變異數

定義：$\mathrm{var}(z) = \langle (z - \bar z)^{2}\rangle$，其中 $\bar z = \langle z\rangle = f(\bar{\mathbf x})$（取 first-order）。

把 Taylor 展開代入：
$$z - \bar z \approx \sum_i \frac{\partial f}{\partial x_i}(x_i - \bar x_i)$$

平方並取期望：
$$\langle(z-\bar z)^{2}\rangle = \sum_i \sum_j \frac{\partial f}{\partial x_i}\frac{\partial f}{\partial x_j}\bigl\langle (x_i-\bar x_i)(x_j-\bar x_j)\bigr\rangle$$

這就是教科書 **Eq. 9.3**（p.186）：

$$\boxed{\;\mathrm{var}(z) \approx \sum_j \sum_i \frac{\partial f}{\partial x_i}\frac{\partial f}{\partial x_j}\sigma_{ij}\;}$$

其中 $\sigma_{ii}=\sigma_i^{2}$（變異數）、$\sigma_{ij}=\langle(x_i-\bar x_i)(x_j-\bar x_j)\rangle$（共變異數）。

### 1.4 兩個極端

- **完全不相關**（$\sigma_{ij}=0$ for $i\neq j$）：

  $$\mathrm{var}(z) \approx \sum_i \left(\frac{\partial f}{\partial x_i}\right)^{2}\sigma_i^{2}$$

- **完全相關**（$\sigma_{ij}=\sigma_i\sigma_j$）：和的根號（不會抵消）。

### 1.5 「相對誤差」捷徑

對乘除型 $z=x^{p}y^{q}$，取對數：$\ln z = p\ln x + q\ln y$，微分：

$$\frac{dz}{z} = p\frac{dx}{x} + q\frac{dy}{y}$$

不相關時：
$$\left(\frac{\sigma_z}{z}\right)^{2} \approx p^{2}\left(\frac{\sigma_x}{x}\right)^{2} + q^{2}\left(\frac{\sigma_y}{y}\right)^{2}$$

→ **HW5 Problem 1(3) $z=x^{3}y^{-3}$** 的捷徑：$\sigma_z/z \approx 3\sqrt{(\sigma_x/x)^{2}+(\sigma_y/y)^{2}}$（不相關）。

---

## 第二章：Table 9.2 速查表怎麼推

教科書 Table 9.2（p.187，[截圖](textbook_refs/p187_Table92-200.png)）給了 4 個經典結果：

| Function | Uncorrelated | Correlated |
|---|---|---|
| $z=x+y$ | $\sigma_z^{2}=\sigma_x^{2}+\sigma_y^{2}$ | $+ 2\sigma_{xy}$ |
| $z=x-y$ | $\sigma_z^{2}=\sigma_x^{2}+\sigma_y^{2}$ | $- 2\sigma_{xy}$ |
| $z=xy$ | $\sigma_z^{2}=\bar y^{2}\sigma_x^{2}+\bar x^{2}\sigma_y^{2}$ | $+ 2\bar x\bar y\,\sigma_{xy}$ |
| $z=x/y$ | $\sigma_z^{2}=\dfrac{1}{\bar y^{2}}\sigma_x^{2}+\dfrac{\bar x^{2}}{\bar y^{4}}\sigma_y^{2}$ | $- \dfrac{2\bar x}{\bar y^{3}}\sigma_{xy}$ |

每一條都是 Eq. 9.3 直接代偏導數的結果。例如 $z=xy$：
$\partial z/\partial x = y,\;\partial z/\partial y = x$，

→ $\sigma_z^{2} = y^{2}\sigma_x^{2} + x^{2}\sigma_y^{2} + 2xy\,\sigma_{xy}$（在 $\bar x, \bar y$ 處估）。

對 HW5 三題：

> 注意：題目以「**(x, y)**」標示隨機變數，故 $x,y$ 帶誤差、$k_i$ 視為常數。

| 題目 | 屬於 Table 9.2 哪類？ | 額外步驟 |
|:-:|:--|:--|
| (1) $z=e^{k_1 x}$ | 不在表內 | **單變數 $x$**（$k_1$ 常數）；直接微分，指數放大誤差，無 corr/uncorr |
| (2) $z=k_1\cos(k_2 x)+k_3\sin(k_4 y)$ | 可看成 $u+v$（u=$k_1\cos$, v=$k_3\sin$），先各自展再加 | 兩變數 $x,y$（$k_i$ 常數）；只有 $(x,y)$ 一組 cross-term |
| (3) $z=x^{3}y^{-3}$ | $z=xy^{-3}$ 的擴展 → 用 1.5 節對數法捷徑 | $\sigma_z/z = 3\sigma_x/x \oplus 3\sigma_y/y$ |

---

## 第三章：單參數擾動敏感度 (Eq. 9.1)

### 3.1 為何需要

誤差傳播告訴你「σ_z 多少」；敏感度問你「**哪個參數對 z 影響最大**」。
這對：
- **實驗設計**：把錢花在量哪個參數最有用
- **模型簡化**：對 z 不敏感的參數可以固定
- **管理決策**：知道調哪個 knob 最有效

### 3.2 公式 (Eq. 9.1，p.181)

$$\boxed{\;S = \frac{\Delta R/R_n}{\Delta P/P_n} = \frac{(R_a-R_n)/R_n}{(P_a-P_n)/P_n}\;}$$

- $R_n, P_n$：nominal（基準）回應與參數
- $R_a, P_a$：altered（擾動後）回應與參數
- $|S|$ 大 → 敏感；$S$ 正負表示同向或反向

注意 $S$ 是**無量綱**（相對於相對），可以跨參數比較。

### 3.3 為何要多取幾個 $\Delta P$？

對非線性模型：
1. $S$ **不是常數**——它依擾動量 $\Delta P$ 而變
2. 大擾動會曝光非線性效應（例如 $P=(d/b)^n$ 中冪次$n$ 放大效應）
3. 慣例：取 ±2%, ±10%, ±20% 三個水準

### 3.4 HW5 P2 的結果解讀

詳見 [SOLUTION.md §第二題](SOLUTION.md#第二題-25-滅絕模型參數擾動敏感度)。

關鍵觀察：
- $S^+ \neq S^-$（非線性印證）。對 $d$ 而言，$S^+=10.95\to 25.96$（在 2%→20% 區間單調增），
  $S^- = 9.15\to 4.46$（單調減）。這是因為 $(1+x)^{10}$ 對 $x$ 是 convex 函數。
- $|S_b|$ 略大於 $|S_d|$，因為 $b$ 在分母：$\partial P/\partial b = -n d^n/b^{n+1}$ 比 $\partial P/\partial d = n d^{n-1}/b^n$ 多一個 $1/b$ 因子。
- $|S_n|\approx 1$ 看似不小，但 $n$ 的 CV 只有 6.9%，所以總變異數貢獻才 0.1%。

### 3.5 排序的兩種方式

1. **依 $|S|$ 排**：強度排序，回答「動 1% 會變多少」
2. **依變異數貢獻排**（$(\partial f/\partial x_i)^2 \sigma_i^2$）：考慮量到的不確定範圍，回答「實際誤差影響」

兩者可能不同：高敏感度但量得很準 → 影響其實小。HW5 P2 中兩種排序剛好都是 $b\sim d\gg n$。

---

## 第四章：解析誤差分析 vs Monte Carlo

### 4.1 解析法的優缺

**優點**：
- 一發到位（無需重複跑）
- 給出 closed-form，便於敏感度分解
- 對「小擾動」極快極準

**缺點**：
- 要求模型有解析式（多數動力 ODE 沒有！只能對 closed-form 子模做）
- 小擾動假設破裂時失靈（教科書 HW5 P2 就是個例子：$\sigma_d/\bar d \approx 20\%$ 已不算小）
- 不能處理非常態分布或有界（如 $P\in[0,1]$）的情形

### 4.2 Monte Carlo 法的優缺

**優點**：
- 對任何複雜模型都行（黑盒就行）
- 可指定任意輸入分布（log-normal、uniform、empirical...）
- 自然產生分布形狀（可看 median, percentile, skew）
- 可處理約束（拒絕採樣，如 $d<b$）

**缺點**：
- 慢（$\propto N$），$N$ 通常 $10^4 \sim 10^6$
- 統計誤差 $\propto 1/\sqrt{N}$，要更準需更多次
- 結果是估計，每次跑不同（除非固定 seed）

### 4.3 為什麼 HW5 P2 兩法給出不同答案？

教科書 p.190 明確指出：

> the distribution is far from normal, contrary to the assumption of the above analytical error analysis

具體：
- 解析法給 mean=0.308，std=0.849，95% CI=[$-$1.36, 1.97]——上下都超出邏輯區間 $[0,1]$
- MC 給 mean=0.206，median=0.094，95%=[0.001, 0.883]——分布**右偏**

差異來源：
1. **bound**：$P\in[0,1]$，常態假設不成立
2. **冪次非線性**：$(d/b)^{10}$ 對小 $d/b$ 接近 0、對 $d/b\to 1$ 趨於 1，極不對稱
3. **拒絕採樣使分布變形**：丟棄 $d\ge b$ 改變了邊際分布

MC 的結論：$P$ 真的不確定（介於 0 到 0.88 都可能），**deterministic 計算的 0.308 並無實質意義**。
這正是 Chapter 9 的核心訊息：**參數不確定時，預測本身就是分布而非單點**。

### 4.4 Latin Hypercube Sampling (LHS) 補充

教科書 §10.3 提到 LHS 是分層隨機抽樣的進階版，能用較少樣本逼近 MC 結果。
本作業未要求，但實務上若 $N$ 受限（如複雜 ODE 每次模擬要分鐘級），用 LHS 比純 MC 效率高 10×。

---

## 第五章：nullcline 與相平面

### 5.1 為什麼研究 nullcline

對 2-D 系統 $\dot x = f(x,y),\;\dot y = g(x,y)$：
- **x-nullcline**：$f(x,y)=0$ 的曲線集合（在這條曲線上，$x$ 不變化）
- **y-nullcline**：$g(x,y)=0$（在這條曲線上，$y$ 不變化）

**兩條 nullcline 的交點 = 平衡點**（兩個導數都為 0）。

### 5.2 nullcline 把空間切成 region

每個 region 內 $\dot x$ 與 $\dot y$ 的符號不變 → 可以畫定性流向箭頭。
- 越過 x-nullcline：$\dot x$ 變號（軌跡水平方向反轉）
- 越過 y-nullcline：$\dot y$ 變號（軌跡垂直方向反轉）

→ **不用解 ODE，就能勾勒整體流動結構**！

### 5.3 HW5 P4 的 nullcline 例子

$\dot x = a_1 x^{2}-a_2 x^{3}-bxy = 0 \Rightarrow x=0$ 或 $y = (a_1 x-a_2 x^{2})/b$

把它寫成 $x$ 的函數時是**拋物線**，頂點在 $x=a_1/(2a_2)$，零點在 $0$ 和 $a_1/a_2$。

$\dot y = dxy - fy^{2} = 0 \Rightarrow y=0$ 或 $y=dx/f$

線性，過原點，斜率 $d/f$。

→ 兩條非平凡 nullcline 都過原點，且都不是 axis-aligned。交點即平衡點。

### 5.4 在 nullcline 上的「另一個」變化率

例如在 x-nullcline 上 $\dot x=0$，這時候系統**僅沿 y 方向移動**——所以箭頭垂直。
其方向由 $\dot y$ 的符號決定。HW5 P4 §(1) 的代數推導正是在做這件事。

---

## 第六章：Jacobian + 特徵值 = 局部穩定性

### 6.1 從非線性到線性的橋

對非線性系統 $\dot{\mathbf x}=\mathbf F(\mathbf x)$，在平衡點 $\mathbf x^*$（$\mathbf F(\mathbf x^*)=\mathbf 0$）附近設 $\mathbf x = \mathbf x^* + \boldsymbol\xi$：

$$\dot{\boldsymbol\xi} = \mathbf F(\mathbf x^*+\boldsymbol\xi) \approx \mathbf F(\mathbf x^*) + \mathbf J(\mathbf x^*)\boldsymbol\xi = \mathbf J\boldsymbol\xi$$

這是**線性化**（Eq. 9.37–9.39，p.206–207）。Jacobian：

$$\mathbf J = \begin{pmatrix}\partial f/\partial x & \partial f/\partial y \\ \partial g/\partial x & \partial g/\partial y\end{pmatrix}\bigg|_{\mathbf x^*}$$

### 6.2 特徵值告訴你什麼

線性化系統 $\dot{\boldsymbol\xi}=\mathbf J\boldsymbol\xi$ 的解是 $\boldsymbol\xi(t)=\sum c_i \mathbf v_i e^{\lambda_i t}$。
所以**穩定 ⟺ 所有 $\lambda_i$ 實部 $<0$**：

$$\boxed{\;\max(\mathrm{Re}\,\lambda_i)<0\;\Longleftrightarrow\;\text{locally asymptotic stable}\;}$$

### 6.3 2×2 系統的速查（trace–det）

對 $\mathbf J = \begin{pmatrix}a&b\\c&d\end{pmatrix}$，$\mathrm{tr}=a+d,\;\det=ad-bc$，

特徵值 $\lambda = \frac{1}{2}\!\left[\mathrm{tr}\pm\sqrt{\mathrm{tr}^{2}-4\det}\,\right]$

- $\det < 0$：兩個實特徵值一正一負 → **saddle** (永遠不穩)
- $\det > 0$ 且 $\mathrm{tr}<0$ 且 $\mathrm{tr}^{2}\ge 4\det$：兩實負 → **stable node**
- $\det > 0$ 且 $\mathrm{tr}<0$ 且 $\mathrm{tr}^{2}< 4\det$：複共軛，實部負 → **stable spiral (focus)**
- $\det > 0$ 且 $\mathrm{tr}>0$：unstable 對應版（node / spiral）
- $\mathrm{tr}=0,\;\det>0$：純虛 → **center**（線性中性穩定；非線性可能略偏）

### 6.4 Hartman-Grobman 定理

只要平衡點是**雙曲**（$\mathrm{Re}\,\lambda_i \neq 0$ for all $i$），線性化與非線性局部相軌跡**拓撲等價**。
所以 Jacobian 分析有效。

**例外**：HW5 P4 的 $E_0=(0,0)$，Jacobian 全 0 → 不雙曲 → 線性化失效，要看高階項或數值。

### 6.5 Routh-Hurwitz 捷徑（p.209）

對 $\lambda^{2}+a_1\lambda+a_2=0$（m=2），穩定 ⟺ **$a_1>0$ 且 $a_2>0$**。
不需算特徵值，只看係數正負就好。HW5 P3 $E_3$：$a_1=0.05625>0,\;a_2=3.125\times10^{-4}>0$ → 穩定。✓

---

## 第七章：Gause 競爭模型的四種 case

### 7.1 方程式

$$\begin{aligned}
\dot n_1 &= r_1 n_1\!\left(1 - \frac{n_1 + \alpha n_2}{K_1}\right) \\
\dot n_2 &= r_2 n_2\!\left(1 - \frac{n_2 + \beta  n_1}{K_2}\right)
\end{aligned}$$

- $\alpha$：species 2 對 species 1 的競爭壓力（每多 1 個 n2 相當於 α 個 n1 占資源）
- $\beta$：species 1 對 species 2 的競爭壓力
- $K_i$：物種 $i$ 單獨存在時的承載量

### 7.2 四個非零 nullcline 截距（教科書 Fig. 9.11）

| nullcline | 與 $n_1$ 軸交 | 與 $n_2$ 軸交 |
|---|:--:|:--:|
| $n_1+\alpha n_2=K_1$ (for $\dot n_1=0$) | $K_1$ | $K_1/\alpha$ |
| $n_2+\beta n_1=K_2$ (for $\dot n_2=0$) | $K_2/\beta$ | $K_2$ |

### 7.3 四個 case 的條件（[Fig. 9.11 截圖](textbook_refs/p201_Fig911_Gause-214.png)）

| Case | $n_1$ 軸截距比 | $n_2$ 軸截距比 | 結局 |
|:--:|:--:|:--:|:--|
| I   | $K_1 > K_2/\beta$ | $K_1/\alpha > K_2$ | n1 wins (n2 滅) |
| II  | $K_1 < K_2/\beta$ | $K_1/\alpha < K_2$ | n2 wins (n1 滅) |
| **III** | $\mathbf{K_1 < K_2/\beta}$ | $\mathbf{K_1/\alpha > K_2}$ | **穩定共存** |
| IV  | $K_1 > K_2/\beta$ | $K_1/\alpha < K_2$ | 不穩定共存（鞍點），依初值決定誰勝 |

直觀：Case III 表示兩物種的「跨物種競爭壓力」都比「自身擁擠」弱（$\alpha\beta<1$），所以可以共存。

### 7.4 HW5 P3 為什麼是 Case III

題目給 $K_1=200,\alpha=0.2,K_2=800,\beta=3$：

$K_1=200$ vs $K_2/\beta=266.7$ → $K_1<K_2/\beta$ ✓
$K_1/\alpha=1000$ vs $K_2=800$ → $K_1/\alpha>K_2$ ✓

故為 Case III。共存點 $(n_1^*,n_2^*)=(100,500)$，Jacobian 特徵值 $\lambda=(-0.05,-0.006)$ 皆負 → 穩定。

### 7.5 為什麼 Case IV 不穩

書 p.208 用 $K_2=1100,\beta=6$ 演示 Case IV：共存點存在但特徵值有正實部 → 鞍點。
這是「**indeterminant exclusion**」：兩物種在某條 separatrix 兩側分屬不同的吸引域，由初始族群決定誰勝。

---

## 附錄：常見錯誤與陷阱

### A.1 誤差傳播

❌ 直接用平均值代入後再算 var（這只是 deterministic 值，不是 variance）
✓ 對函數**偏微分**再代均值，再乘 $\sigma^2$，才是 Eq. 9.3

❌ 把 σ_xy 寫成 $\sqrt{\sigma_x\sigma_y}$（誤把 covariance 當 std）
✓ $\sigma_{xy} = \rho_{xy}\,\sigma_x\sigma_y$，$\rho\in[-1,1]$

❌ 對 $z=x/y$ 的相對誤差寫成 $\sigma_x/x + \sigma_y/y$（線性錯誤）
✓ 不相關時是 **平方和開根** $(\sigma_z/z)^2 = (\sigma_x/x)^2 + (\sigma_y/y)^2$

### A.2 敏感度分析

❌ 只算 $S^+$ 不算 $S^-$（漏失非線性不對稱）
✓ 雙向都算，才能看 convex/concave

❌ 跨參數比較絕對 $\Delta R$（單位不一）
✓ 用 $S$（無量綱）才能比

### A.3 穩定性分析

❌ 看到「兩特徵值都負」就說穩定，沒檢查是否雙曲
✓ 確認 $\mathrm{Re}\,\lambda\neq 0$；若有 0 要看非線性

❌ Jacobian 算錯 row/column（轉置）
✓ 嚴格 $J_{ij}=\partial f_i/\partial x_j$（row=方程，column=變數）

❌ 只看 $E_3$ 穩定就說整個系統穩定
✓ Local stability 只說「附近」；要看全域得用 Lyapunov 或數值

### A.4 nullcline / 平衡點

❌ 沒做「零情況」($x=0$ 或 $y=0$) 帶出的平衡點
✓ 所有 nullclines（包含 trivial 的座標軸）都要算

❌ 把「兩條 N1 都過 (0,0)」誤算為兩個平衡點
✓ 平衡點是空間中的**點**，重複只算一次

---

## 程式碼導讀

[hw5_solution.py](hw5_solution.py) 結構：

```
problem1()  ← sympy 符號偏微分 + 變異數公式
problem2()  ← 三層: (a) Eq. 9.1 擾動表; (b) Eq. 9.5 解析 var; (c) MC
problem3()  ← gause_jacobian() 帶入四個平衡點 + numpy.linalg.eigvals
problem4()  ← sympy 解符號平衡點 + 數值 Jacobian + 流線圖
```

關鍵函式：
- `var_P_analytical(d, b, n, sd, sb, sn)`：Eq. 9.5 直接套用
- `gause_jacobian(n1, n2, ...)`：Eq. 9.40a/b
- `gause_rhs(t, state, ...)`：可餵給 scipy.integrate.solve_ivp 驗證軌跡

---

*完整推導與結果見 [SOLUTION.md](SOLUTION.md)；手寫繳交精簡版見 [HANDWRITTEN.md](HANDWRITTEN.md)。*
