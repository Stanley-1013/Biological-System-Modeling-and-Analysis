# 從零開始學島嶼生物地理學建模
## — BME5113 HW1 完整教學指南

> 本文件從基礎概念出發，逐步帶你理解這次作業所需的所有知識與技能。
> 假設你具備基礎微積分能力（知道導數是什麼），但對生態建模完全陌生。
> 每一章都會先給你直覺，再給數學，最後給程式碼。

---

## 目錄

1. [第一章：什麼是島嶼生物地理學？](#第一章什麼是島嶼生物地理學)
2. [第二章：線性迴歸基礎](#第二章線性迴歸基礎)
3. [第三章：微分方程式入門](#第三章微分方程式入門)
4. [第四章：有限差分法（數值模擬）](#第四章有限差分法數值模擬)
5. [第五章：Python 程式設計實作](#第五章python-程式設計實作)
6. [第六章：進階模型——非線性函數](#第六章進階模型非線性函數)
7. [第七章：島嶼面積效應](#第七章島嶼面積效應)
8. [附錄一：作業解題流程圖](#附錄一作業解題流程圖)
9. [附錄二：常見錯誤與除錯指南](#附錄二常見錯誤與除錯指南)

---

## 第一章：什麼是島嶼生物地理學？

### 1.1 從一場火山噴發說起

1883 年 8 月，印尼喀拉喀托火山（Krakatau）爆發，是人類歷史上最強烈的火山爆發之一。爆炸聲音傳遍 5000 公里外，海嘯奪走 3 萬多條人命。火山周邊的小島 Rakata 幾乎被完全摧毀——所有生物幾乎滅絕，植被化為烏有。

然而，有趣的故事從這裡才開始。

幾年後，科學家登島調查，發現已有蕨類、蜘蛛和鳥類回到島上。數十年間，生物多樣性逐漸恢復。生態學家因此有了一個難得的機會：**從零開始觀察一個島嶼上的物種如何累積**。這個自然實驗（natural experiment），直接啟發了後來的島嶼生物地理學理論。

**關鍵問題是**：這個島最終會有多少物種？物種數如何隨時間演變？什麼因素決定了最終的平衡？

### 1.2 MacArthur-Wilson 理論（1967）

美國生態學家 Robert MacArthur 與 E.O. Wilson 在 1967 年出版了《島嶼生物地理學》（*The Theory of Island Biogeography*），提出了一個優雅的理論框架。

**核心思想**：島嶼上的物種數量，由兩個相互抗衡的過程共同決定：

| 過程 | 說明 | 記號 |
|------|------|------|
| **移入率** (Immigration rate) | 大陸物種移入島嶼、成功定殖的速率 | $I(R)$ |
| **滅絕率** (Extinction rate) | 島嶼上已有物種走向局部滅絕的速率 | $E(R)$ |

其中 $R$ 是當前島嶼上的物種數目。

**這兩個速率如何隨 $R$ 變化？**

想像你站在一個剛恢復的空島上。一開始沒有任何生物，大陸上的任何物種都可以嘗試移入，移入成功的機會很大 → **移入率高**。當島上物種愈來愈多，可以「新進駐」的物種愈來愈少（因為大部分物種都已在島上了），而且每個新來者都需要在競爭激烈的環境中立足 → **移入率隨 $R$ 遞減**。

反過來，一個空島幾乎沒有物種，自然沒有什麼東西可以滅絕 → **滅絕率接近零**。但當物種數增加，個別物種的種群規模縮小（資源被更多物種瓜分），競爭壓力增大 → **滅絕率隨 $R$ 遞增**。

### 1.3 動態平衡的概念

將以上兩條曲線畫在同一張圖上：

```
速率
 ^
 |  I(R)：移入率（遞減曲線）
 |  \
 |   \        ← 在這個區域：I > E，物種在增加
 |    \
 |     \  ← R* 平衡點（兩線交叉）
 |      ×
 |       \    → 在這個區域：E > I，物種在減少
 |    ----\----  E(R)：滅絕率（遞增曲線）
 |   /     \
 |  /       \
 +--+--------+----> R（物種數）
    0       R*   P
```

兩條曲線的交點就是**動態平衡點**（dynamic equilibrium）$R^*$：

- 若目前物種數 $R < R^*$：$I(R) > E(R)$，移入大於滅絕，物種數增加，往 $R^*$ 靠近
- 若目前物種數 $R > R^*$：$E(R) > I(R)$，滅絕大於移入，物種數減少，往 $R^*$ 靠近
- 在 $R = R^*$：$I(R^*) = E(R^*)$，動態平衡，物種數穩定不變

這是一個**穩定均衡**（stable equilibrium）——就像鐘擺在最低點一樣，被擾動後會自動回來。

圖中 $P$ 是**大陸物種庫**（mainland pool），代表島嶼上的物種數達到大陸物種的總數時，再也沒有新物種可以移入，即 $I(P) = 0$。

### 1.4 現實世界的應用

MacArthur-Wilson 理論不只是學術玩具，它對自然保育有深遠影響：

- **棲地破碎化**（habitat fragmentation）：農田開發把森林切割成許多小「島嶼」，每塊面積縮小，物種平衡點 $R^*$ 降低，長期來看物種會慢慢滅絕
- **保護區設計**：理論支持設立大型連續保護區，而非散布的小塊保護地
- **島嶼復育**：了解移入率與滅絕率的機制，可以設計主動復育策略（如引進種群）

---

## 第二章：線性迴歸基礎（Linear Regression）

### 2.1 什麼是迴歸？

**問題情境**：我們有 Rakata 島的觀測資料——在不同物種數 $R$ 時，測量到的移入率 $I$ 和滅絕率 $E$：

| $R$（物種數）| $I$（移入率）| $E$（滅絕率）|
|:----------:|:----------:|:----------:|
| 0   | 8.00 | 0.00 |
| 36  | 3.00 | 0.05 |
| 80  | 5.00 | 0.10 |
| 155 | 6.50 | 0.50 |
| 210 | 4.00 | 1.75 |
| 240 | 2.50 | 1.75 |

這些點散佈在坐標圖上，不會完全對齊一條直線（因為有觀測誤差、和其他未納入的因素）。**線性迴歸**的任務是：找到一條「最能代表這些散點趨勢」的直線。

### 2.2 最小平方法的幾何直覺

設我們要找直線 $\hat{y} = a + bx$。對每一個觀測點 $(x_i, y_i)$，直線的預測值是 $\hat{y}_i = a + bx_i$，而**殘差**（residual）是實際值與預測值的差：

$$e_i = y_i - \hat{y}_i = y_i - (a + bx_i)$$

我們希望整體誤差盡可能小。不能直接加總殘差（正負會抵消），所以採用**殘差平方和**（RSS, Residual Sum of Squares）：

$$\text{RSS} = \sum_{i=1}^{n} e_i^2 = \sum_{i=1}^{n} (y_i - a - bx_i)^2$$

**最小平方法（Ordinary Least Squares, OLS）**的目標：找到使 RSS 最小的 $a$ 和 $b$。

### 2.3 從零推導正規方程式

要讓 $\text{RSS}$ 最小，對 $a$ 和 $b$ 各偏微分並令其等於零：

$$\frac{\partial \text{RSS}}{\partial a} = -2\sum_{i=1}^{n}(y_i - a - bx_i) = 0$$

$$\frac{\partial \text{RSS}}{\partial b} = -2\sum_{i=1}^{n} x_i(y_i - a - bx_i) = 0$$

第一條方程式展開：

$$\sum y_i - na - b\sum x_i = 0 \implies a = \bar{y} - b\bar{x}$$

其中 $\bar{x} = \frac{1}{n}\sum x_i$，$\bar{y} = \frac{1}{n}\sum y_i$ 是平均值。

將 $a = \bar{y} - b\bar{x}$ 代入第二條方程式 $\sum x_i(y_i - a - bx_i) = 0$，展開：

$$\sum x_i\bigl(y_i - (\bar{y} - b\bar{x}) - bx_i\bigr) = 0$$

$$\sum x_i(y_i - \bar{y}) - b\underbrace{\sum x_i(x_i - \bar{x})}_{\text{移項}} = 0$$

整理得：

$$b = \frac{\sum x_i(y_i - \bar{y})}{\sum x_i(x_i - \bar{x})}$$

分子分母同乘以 $n$，利用 $\sum x_i(y_i-\bar{y}) = \sum x_iy_i - n\bar{x}\bar{y}$ 化簡，可得：

$$\boxed{b = \frac{n\sum x_i y_i - \sum x_i \sum y_i}{n\sum x_i^2 - \left(\sum x_i\right)^2}, \quad a = \bar{y} - b\bar{x}}$$

這兩條公式叫做**正規方程式**（Normal Equations）。

### 2.4 決定係數（Coefficient of Determination）$R^2$ 的直覺

$R^2$ 衡量「這條直線解釋了多少資料的變異」：

$$R^2 = 1 - \frac{\text{RSS}}{\text{TSS}} = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$$

- $\text{TSS}$（Total Sum of Squares）= 資料本身的總變異量
- 若 $R^2 = 1$：直線完美通過所有點
- 若 $R^2 = 0$：直線跟用平均值預測一樣差，等同毫無解釋力
- 通常 $R^2 > 0.7$ 表示配適良好

### 2.5 手算範例：Rakata 島移入率迴歸

以下用 $I$ 對 $R$ 做迴歸，一步步計算。設 $n = 6$：

**第一步：計算基礎統計量**

| $R_i$ | $I_i$ | $R_i^2$ | $R_i I_i$ |
|-------|-------|---------|-----------|
| 0     | 8.00  | 0       | 0         |
| 36    | 3.00  | 1296    | 108       |
| 80    | 5.00  | 6400    | 400       |
| 155   | 6.50  | 24025   | 1007.5    |
| 210   | 4.00  | 44100   | 840       |
| 240   | 2.50  | 57600   | 600       |
| **合計** | **29.00** | **133421** | **2955.5** |

$\bar{R} = 721/6 \approx 120.2$，$\bar{I} = 29.00/6 \approx 4.833$

**第二步：代入公式**

$$b_I = \frac{6 \times 2955.5 - 721 \times 29.00}{6 \times 133421 - 721^2} = \frac{17733 - 20909}{800526 - 519841} = \frac{-3176}{280685} \approx -0.01132$$

$$a_I = 4.833 - (-0.01132) \times 120.2 \approx 4.833 + 1.360 \approx 6.193$$

所以：$I(R) \approx 6.193 - 0.01132 \cdot R$

**物理意義**：
- 截距（intercept）$a_I \approx 6.193$：空島（$R=0$）時的移入率，每年約 6.2 個物種
- 斜率（slope）$b_I \approx -0.01132$：每增加一個物種，移入率平均下降 0.011 個物種/年

**滅絕率迴歸結果**（計算過程類似）：

$$E(R) \approx -0.2744 + 0.008040 \cdot R$$

- 截距 $a_E \approx -0.274$：數學外推到 $R=0$ 時有輕微負值，但生物學上 $R=0$ 時滅絕率應為 0，這個偏差是線性近似的限制，可接受
- 斜率 $b_E \approx 0.00804$：每增加一個物種，滅絕率平均上升 0.008 個物種/年

### 2.6 Python 實作

```python
import numpy as np

# 觀測資料
R_data = np.array([0, 36, 80, 155, 210, 240], dtype=float)
I_data = np.array([8.0, 3.0, 5.0, 6.5, 4.0, 2.5], dtype=float)
E_data = np.array([0.0, 0.05, 0.10, 0.50, 1.75, 1.75], dtype=float)

# numpy.polyfit(x, y, 次數)
# 次數=1 代表線性迴歸
# 回傳 [斜率, 截距]（高次到低次排列）
coeffs_I = np.polyfit(R_data, I_data, 1)
slope_I, intercept_I = coeffs_I
print(f"I(R) = {intercept_I:.4f} + {slope_I:.6f} * R")

# 計算 R^2
I_pred = np.polyval(coeffs_I, R_data)       # 預測值
ss_res = np.sum((I_data - I_pred) ** 2)     # RSS
ss_tot = np.sum((I_data - I_data.mean()) ** 2)  # TSS
r2_I = 1 - ss_res / ss_tot
print(f"R^2 = {r2_I:.4f}")
```

**輸出結果**：
```
I(R) = 6.1930 + -0.011315 * R
R^2 = 0.2682
```

> **注意**：$R^2 = 0.268$ 偏低，表示線性模型對移入率的配適度（goodness of fit）有限——資料散佈很大。這是現實生態資料的常見狀況。相比之下，滅絕率的 $R^2 = 0.860$ 就很不錯。

---

## 第三章：微分方程式入門

### 3.1 導數 = 變化速率

你在微積分課學過：若 $R(t)$ 是一個關於時間 $t$ 的函數，則

$$\frac{dR}{dt} = \lim_{\Delta t \to 0} \frac{R(t + \Delta t) - R(t)}{\Delta t}$$

代表「$R$ 在時刻 $t$ 的瞬間變化速率」。比如：

- 若 $\frac{dR}{dt} = +5$，表示現在每年物種數正在增加 5 種
- 若 $\frac{dR}{dt} = -3$，表示每年物種數在減少 3 種
- 若 $\frac{dR}{dt} = 0$，表示物種數暫時不變（可能在平衡點）

### 3.2 島嶼物種動態方程式

在任何時刻，物種數的淨變化率等於移入率減去滅絕率：

$$\frac{dR}{dt} = I(R) - E(R)$$

把線性迴歸得到的 $I(R)$ 和 $E(R)$ 代入：

$$\frac{dR}{dt} = (6.1930 - 0.011315 R) - (-0.2744 + 0.008040 R)$$

$$= (6.1930 + 0.2744) + (-0.011315 - 0.008040) R$$

$$\boxed{\frac{dR}{dt} = 6.4675 - 0.019355 \cdot R}$$

這是一個**一階線性常微分方程式**，形式為 $\frac{dR}{dt} = A - BR$（其中 $A > 0, B > 0$）。

### 3.3 求平衡點

在**平衡狀態**下，物種數不再改變，即 $\frac{dR}{dt} = 0$：

$$I(R^*) = E(R^*)$$

$$a_I + b_I R^* = a_E + b_E R^*$$

$$a_I - a_E = (b_E - b_I) R^*$$

$$\boxed{R^* = \frac{a_I - a_E}{b_E - b_I}}$$

代入數值：

$$R^* = \frac{6.1930 - (-0.2744)}{0.008040 - (-0.011315)} = \frac{6.4675}{0.019355} \approx 334 \text{ 個物種}$$

### 3.4 穩定性分析：為什麼 R* 是穩定的？

方程式 $\frac{dR}{dt} = 6.4675 - 0.019355 R$ 的行為很直觀：

**情況一：$R < R^* = 334$**
$$\frac{dR}{dt} = 6.4675 - 0.019355 \times (\text{小的 } R) > 0$$
物種數增加，往 $R^*$ 趨近。

**情況二：$R > R^* = 334$**
$$\frac{dR}{dt} = 6.4675 - 0.019355 \times (\text{大的 } R) < 0$$
物種數減少，往 $R^*$ 趨近。

**情況三：$R = R^* = 334$**
$$\frac{dR}{dt} = 0$$
靜止不動。

這就像一個磁鐵——不管你從哪個方向靠近，它都會把 $R$ 吸引到 $R^*$。這種性質叫做**穩定不動點**（stable fixed point）或**穩定平衡**。

### 3.5 解析解

對於線性形式 $\frac{dR}{dt} = A - BR$，可以直接求出解析解（closed-form solution）。令 $u = R - R^* = R - A/B$，則：

$$\frac{du}{dt} = \frac{dR}{dt} = A - B(u + R^*) = A - Bu - BR^* = -Bu$$

（因為 $A = BR^*$）

對 $\dfrac{du}{dt} = -Bu$ 分離變數（separation of variables）：

$$\frac{du}{u} = -B\,dt$$

兩邊積分：

$$\int \frac{du}{u} = \int -B\,dt \implies \ln|u| = -Bt + C$$

取指數，令積分常數 $u_0 = u(0) = R_0 - R^*$，得：

$$u(t) = u_0\,e^{-Bt}$$

代回 $u = R - R^*$，即：

$$\boxed{R(t) = R^* + (R_0 - R^*) e^{-Bt}}$$

其中 $R_0$ 是初始物種數，$B = b_E - b_I = 0.019355$。

**特徵時間（relaxation time）**：

$$\tau = \frac{1}{B} = \frac{1}{0.019355} \approx 51.7 \text{ 年}$$

$\tau$ 代表系統回到平衡的快慢——大約在 $3\tau \approx 155$ 年後，初始偏差已消除 95%。

### 3.6 大陸物種庫 P

$P$（mainland pool）的定義：當島嶼上的物種數達到 $P$ 時，移入率降為零（島上已包含大陸所有物種，沒有新物種可以移入）：

$$I(P) = 0 \implies a_I + b_I P = 0 \implies P = -\frac{a_I}{b_I}$$

代入數值：

$$P = -\frac{6.1930}{-0.011315} \approx 547 \text{ 個物種}$$

**注意區別**：
- $R^* \approx 334$：動態平衡物種數（有生物在，也在滅絕，但移入 = 滅絕）
- $P \approx 547$：大陸物種庫的上限（純理論上限，實際上 $R < P$ 因為有滅絕壓力）

---

## 第四章：有限差分法（Finite Difference Method，數值模擬）

### 4.1 為什麼需要數值方法？

第三章的線性 ODE 可以手解。但現實中，絕大多數微分方程式沒有解析解——比如非線性 ODE 如 $\frac{dR}{dt} = \lambda e^{-\alpha R} - \beta R^2$。這時我們需要**數值方法**，用電腦一步一步逼近真實解。

### 4.2 Euler 方法的核心想法

回到導數的定義：

$$\frac{dR}{dt} \approx \frac{R(t + \Delta t) - R(t)}{\Delta t}$$

當 $\Delta t$ 很小，近似就很準確。重新排列：

$$R(t + \Delta t) \approx R(t) + \Delta t \cdot \frac{dR}{dt}\bigg|_{t}$$

這就是**前向 Euler 方法**（Forward Euler Method）：

$$\boxed{R_{n+1} = R_n + \Delta t \cdot f(R_n, t_n)}$$

其中 $f(R, t) = I(R) - E(R) = \frac{dR}{dt}$，$\Delta t$ 是時間步長（time step）。

**直覺**：你知道現在的位置 $R_n$ 和現在的「速度」$f(R_n)$，就可以估計一小段時間 $\Delta t$ 後的新位置。

### 4.3 手動追蹤前五步（以 $R_0 = 0$ 為例）

設 $\Delta t = 1$ 年（為了方便手算，實際模擬用 0.5 年）：

$$f(R) = 6.4675 - 0.019355 R$$

| 步驟 $n$ | 時間 $t_n$（年）| $R_n$ | $f(R_n)$ | $R_{n+1} = R_n + 1 \times f(R_n)$ |
|:--------:|:--------------:|:-----:|:---------:|:----------------------------------:|
| 0 | 0  | 0.000  | 6.4675 | 6.4675 |
| 1 | 1  | 6.468  | 6.3424 | 12.810 |
| 2 | 2  | 12.810 | 6.1946 | 19.004 |
| 3 | 3  | 19.004 | 6.0776 | 25.082 |
| 4 | 4  | 25.082 | 5.9327 | 31.015 |
| 5 | 5  | 31.015 | ... | ... |

觀察：物種數在初期快速增加（因為 $I \gg E$），增速逐漸放緩，最終趨向 $R^* = 334$。

### 4.4 選擇合適的 $\Delta t$

$\Delta t$ 的選擇影響模擬的精度和穩定性：

| $\Delta t$ | 效果 |
|:----------:|------|
| 太大（如 $\Delta t = 100$ 年）| 可能發生數值振盪（numerical oscillation），甚至發散（不穩定）|
| 適中（如 $\Delta t = 0.5$ 年）| 精度與速度平衡，通常是好選擇 |
| 太小（如 $\Delta t = 0.001$ 年）| 結果精準，但計算量大且耗時 |

**粗略準則**：$\Delta t$ 應遠小於系統特徵時間 $\tau = 51.7$ 年。$\Delta t = 0.5$ 年約為 $\tau$ 的 1%，夠小了。

**對於線性系統，Euler 方法穩定的條件是**：$\Delta t < 2/B = 2/0.019355 \approx 103$ 年。所以 0.5 年非常安全。

### 4.5 Python 實作

```python
import numpy as np
import matplotlib.pyplot as plt

# 模型參數（來自線性迴歸）
a_I, b_I = 6.1930, -0.011315  # I(R) = a_I + b_I * R
a_E, b_E = -0.2744,  0.008040  # E(R) = a_E + b_E * R

def dRdt(R):
    """物種數的瞬間變化率"""
    immigration = max(a_I + b_I * R, 0.0)  # 移入率不能為負
    extinction  = max(a_E + b_E * R, 0.0)  # 滅絕率不能為負
    return immigration - extinction

def simulate(R0, t_max, dt):
    """
    前向 Euler 模擬
    R0    : 初始物種數
    t_max : 模擬總時長（年）
    dt    : 時間步長（年）
    """
    n_steps = int(t_max / dt) + 1
    t = np.linspace(0, t_max, n_steps)  # 時間陣列
    R = np.zeros(n_steps)               # 物種數陣列
    R[0] = R0                           # 設定初始條件

    for i in range(n_steps - 1):
        # 前向 Euler：R(t+dt) = R(t) + dt * f(R(t))
        R[i+1] = R[i] + dt * dRdt(R[i])
        R[i+1] = max(R[i+1], 0.0)  # 物種數不能為負

    return t, R

# 執行模擬
t1, R1 = simulate(R0=0,   t_max=500, dt=0.5)  # 從空島出發
t2, R2 = simulate(R0=500, t_max=500, dt=0.5)  # 從物種過剩出發

# 繪圖
R_star = 6.4675 / 0.019355  # 平衡點

plt.figure(figsize=(9, 5))
plt.plot(t1, R1, 'b-',  linewidth=2, label='初始 $R_0 = 0$（空島）')
plt.plot(t2, R2, 'r--', linewidth=2, label='初始 $R_0 = 500$（物種過剩）')
plt.axhline(R_star, color='green', linestyle=':', linewidth=1.5,
            label=f'平衡點 $R^* = {R_star:.1f}$')
plt.xlabel('時間（年）', fontsize=12)
plt.ylabel('物種數 $R$', fontsize=12)
plt.title('Rakata 島物種動態模擬（線性模型）', fontsize=13)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('simulation.png', dpi=150)
plt.show()
```

### 4.6 如何解讀收斂圖

當你畫出模擬結果，會看到兩條 S 型曲線（從下往上）或反 S 型曲線（從上往下）：

- **從 $R_0 = 0$ 出發**：物種數先快速增加（$I \gg E$），接近 $R^*$ 後趨緩，最終平穩
- **從 $R_0 = 500$ 出發**：物種數先快速減少（$E \gg I$），接近 $R^*$ 後趨緩，最終平穩
- **兩條曲線最終收斂到同一個 $R^*$**：這驗證了平衡點的存在和穩定性

**收斂時間**（convergence time）定義為「物種數進入 $R^* \pm 5\%$ 範圍的時間點」：
- 從 $R_0 = 0$ 出發：約 154 年
- 從 $R_0 = 500$ 出發：約 118 年（從上方靠近較快，因為 $E > I$ 的驅動力更大）

---

## 第五章：Python 程式設計實作

### 5.1 環境設定與必要套件

這次作業需要三個主要套件：

```python
import numpy as np          # 數值計算（陣列、數學函數）
import matplotlib.pyplot as plt  # 繪圖
import os                   # 檔案路徑操作
```

如果套件尚未安裝，在終端機執行：
```bash
pip install numpy matplotlib
```

### 5.2 定義資料為 NumPy 陣列

```python
# 用 np.array() 建立陣列，dtype=float 確保是浮點數
R_data = np.array([0, 36, 80, 155, 210, 240], dtype=float)
I_data = np.array([8.0, 3.0, 5.0, 6.5, 4.0, 2.5], dtype=float)
E_data = np.array([0.0, 0.05, 0.10, 0.50, 1.75, 1.75], dtype=float)

# NumPy 陣列支援向量化運算（不需要 for 迴圈）
print(R_data * 2)        # [  0.  72. 160. 310. 420. 480.]
print(np.mean(R_data))   # 120.17
print(np.sum(I_data))    # 29.0
```

### 5.3 使用 numpy.polyfit 做迴歸

```python
# polyfit(x, y, deg) 回傳多項式係數（從最高次到最低次）
# deg=1 是線性（直線）
coeffs_I = np.polyfit(R_data, I_data, deg=1)
# coeffs_I = [斜率, 截距]
slope_I, intercept_I = coeffs_I
print(f"I(R) = {intercept_I:.4f} + {slope_I:.6f} * R")

# polyval(coeffs, x) 計算多項式在 x 的值
R_test = np.array([100, 200, 300])
I_test = np.polyval(coeffs_I, R_test)
print(f"I(100) = {I_test[0]:.3f}")  # 預測值
```

**計算 $R^2$：**
```python
def compute_r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1.0 - ss_res / ss_tot

I_pred = np.polyval(coeffs_I, R_data)
r2 = compute_r2(I_data, I_pred)
print(f"R^2 = {r2:.4f}")
```

### 5.4 使用 matplotlib 繪圖

**5.4.1 基本散點圖與迴歸線**

```python
R_line = np.linspace(0, 300, 500)  # 繪圖用的連續 x 值
I_line = np.polyval(coeffs_I, R_line)
E_line = np.polyval(coeffs_E, R_line)

fig, ax = plt.subplots(figsize=(8, 5))

# 散點（觀測資料）
ax.scatter(R_data, I_data, color='blue', s=60, zorder=5, label='移入率資料')
ax.scatter(R_data, E_data, color='red',  s=60, zorder=5, label='滅絕率資料')

# 迴歸直線
ax.plot(R_line, I_line, 'b-', linewidth=2, label='I(R) 迴歸線')
ax.plot(R_line, E_line, 'r-', linewidth=2, label='E(R) 迴歸線')

# 軸標籤（含單位！）
ax.set_xlabel('物種數 R', fontsize=12)
ax.set_ylabel('速率（物種 / 年）', fontsize=12)
ax.set_title('Rakata 島線性迴歸', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
```

**5.4.2 多個子圖（subplots）**

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 5))  # 1 列 2 欄

# 左圖
ax1 = axes[0]
ax1.plot(...)
ax1.set_title('左圖標題')

# 右圖
ax2 = axes[1]
ax2.plot(...)
ax2.set_title('右圖標題')

fig.tight_layout()  # 自動調整間距，避免標題重疊
```

**5.4.3 標記平衡點**

```python
R_star = 334.15

# 垂直虛線標記平衡點
ax.axvline(R_star, color='green', linestyle='--', linewidth=1.5,
           label=f'$R^* = {R_star:.1f}$')

# 在圖上加文字標注
ax.annotate(f'平衡點\n$R^* = {R_star:.0f}$',
            xy=(R_star, 1.5),          # 指向的座標
            xytext=(R_star + 20, 3),   # 文字放置的座標
            arrowprops=dict(arrowstyle='->', color='green'),
            fontsize=10, color='green')
```

### 5.5 模擬迴圈的完整寫法

```python
def simulate_euler(R0, t_max, dt, rate_func):
    """
    通用的前向 Euler 模擬器

    Parameters
    ----------
    R0        : 初始物種數
    t_max     : 模擬總時長（年）
    dt        : 時間步長（年）
    rate_func : 函數，接受 R，回傳 dR/dt

    Returns
    -------
    t : 時間陣列
    R : 物種數陣列
    """
    n_steps = int(t_max / dt) + 1
    t = np.linspace(0, t_max, n_steps)
    R = np.zeros(n_steps)
    R[0] = R0

    for i in range(n_steps - 1):        # 從步驟 0 到倒數第二步
        dR = rate_func(R[i])             # 計算當前速率
        R[i+1] = R[i] + dt * dR         # Euler 更新
        R[i+1] = max(R[i+1], 0.0)       # 防止負值

    return t, R

# 使用範例
def my_rate(R):
    I = max(a_I + b_I * R, 0)
    E = max(a_E + b_E * R, 0)
    return I - E

t, R = simulate_euler(R0=0, t_max=500, dt=0.5, rate_func=my_rate)
```

### 5.6 儲存圖片

```python
import os

# 建立輸出資料夾（如果不存在）
output_dir = 'hw1_figures'
os.makedirs(output_dir, exist_ok=True)

# 儲存圖片
# dpi=150 → 解析度 150 點/英寸，適合報告用
fig.savefig(os.path.join(output_dir, 'fig1_regression.png'), dpi=150)
plt.close(fig)  # 關閉圖形，釋放記憶體
```

---

## 第六章：進階模型——非線性函數

### 6.1 為什麼需要非線性模型？

線性模型有幾個生物學上的問題：

1. **移入率可能變成負數**：線性函數 $I(R) = a_I + b_I R$ 在 $R > P = -a_I/b_I \approx 547$ 時會變成負值，但移入率不可能是負數！
2. **低物種數時滅絕率可能是負數**：$E(R) = a_E + b_E R$ 在 $a_E < 0$ 時，$R=0$ 附近會有負滅絕率，同樣不合理
3. **真實生態關係往往是曲線**：棲位（niche）飽和、競爭交互的累積都是非線性的

### 6.2 負指數移入率

$$\boxed{I(R) = \lambda \cdot e^{-\alpha R}}$$

**參數意義**：
- $\lambda$：最大移入率，即空島（$R=0$）時的移入率（$I(0) = \lambda$）
- $\alpha$：衰減速率，$\alpha$ 越大，移入率隨物種數增加而下降得越快

**優良性質**：
- $I(R) > 0$ 恆成立（指數函數永遠正值）
- 隨 $R$ 增加單調遞減
- 趨近但不會到達零（不像線性函數會穿越橫軸）

**生物直覺**：當島上已有 $R$ 個物種，每個新移入者成功定殖（colonization）的機率大約是 $e^{-\alpha R}$——棲位愈飽和，成功率以指數速率下降。

本作業採用 $\lambda = 8, \alpha = 0.008$（與線性模型截距 $a_I \approx 6.2$ 相近，都在同一量級）。

### 6.3 二次滅絕率

$$\boxed{E(R) = \beta \cdot R^2}$$

**參數意義**：
- $\beta$：競爭係數，表示每對物種之間的競爭強度
- $E(0) = 0$：空島沒有滅絕，生物學正確！

**生物直覺（成對競爭）**：若每兩個物種之間都有競爭交互作用，則物種對的數量為：

$$\binom{R}{2} = \frac{R(R-1)}{2} \approx \frac{R^2}{2}$$

若每個競爭對都有一個微小機率 $p$ 使其中一個物種滅絕，則總滅絕率約為：

$$E \approx p \cdot \frac{R^2}{2} = \frac{p}{2} R^2 = \beta R^2$$

本作業採用 $\beta = 3 \times 10^{-5}$。

### 6.4 非線性模型的平衡條件

設 $I(R^*) = E(R^*)$：

$$\lambda \cdot e^{-\alpha R^*} = \beta \cdot (R^*)^2$$

這個方程式叫做**超越方程式**（transcendental equation）——方程式裡同時有指數函數和多項式，**沒有解析解**，必須用數值方法求解。

### 6.5 數值求根：二分法

**核心思想**：如果 $f(R) = \lambda e^{-\alpha R} - \beta R^2$ 在 $R_a$ 時是正的，在 $R_b$ 時是負的，那麼在 $[R_a, R_b]$ 之間一定有一個零點（由中值定理保證）。

```
f(R)
  |
  |    *  ← 正值區域
  |   * *
  |  *   *
  | *     * ← 零點 R*
--+--+--+--*--------> R
  | Ra     Rb
  |          * ← 負值區域
  |           *
```

**二分法步驟**：

1. 取中點 $R_{mid} = (R_a + R_b) / 2$
2. 若 $f(R_{mid}) > 0$：零點在右半段，令 $R_a = R_{mid}$
3. 若 $f(R_{mid}) < 0$：零點在左半段，令 $R_b = R_{mid}$
4. 重複直到 $|R_b - R_a|$ 夠小

**Python 實作（手動版）**：

```python
def bisection(f, r_lo, r_hi, n_iter=50):
    """
    二分法求 f(R) = 0 的根
    假設 f(r_lo) 和 f(r_hi) 異號
    """
    for _ in range(n_iter):
        r_mid = 0.5 * (r_lo + r_hi)
        if f(r_mid) > 0:
            r_lo = r_mid
        else:
            r_hi = r_mid
    return 0.5 * (r_lo + r_hi)

# 定義 f(R) = I(R) - E(R)
lam, alpha, beta = 8.0, 0.008, 3e-5

def f_curv(R):
    return lam * np.exp(-alpha * R) - beta * R**2

# 先掃描找符號改變的位置
R_scan = np.linspace(1, 800, 10000)
diff = f_curv(R_scan)
sign_changes = np.where(np.diff(np.sign(diff)))[0]

if len(sign_changes) > 0:
    r_lo = R_scan[sign_changes[0]]
    r_hi = R_scan[sign_changes[0] + 1]
    R_star_curv = bisection(f_curv, r_lo, r_hi)
    print(f"曲線模型平衡點 R* = {R_star_curv:.2f}")
    # 輸出：曲線模型平衡點 R* = 217.15
```

**驗算**：
- $I(217) = 8 \times e^{-0.008 \times 217} = 8 \times e^{-1.736} \approx 1.411$
- $E(217) = 3 \times 10^{-5} \times 217^2 \approx 1.413$ ✓

### 6.6 線性 vs 非線性模型比較

| 特性 | 線性模型 | 非線性（曲線）模型 |
|------|:--------:|:------------------:|
| $I(R)$ 形狀 | 直線遞減 | 指數遞減 |
| $E(R)$ 形狀 | 直線遞增 | 二次曲線遞增 |
| $I(R) \geq 0$ | 不保證（$R > P$ 時為負）| 恆成立 |
| $E(0) = 0$ | 不保證（截距可能為負）| 恆成立 |
| 平衡點 $R^*$ | 334（線性求解）| 217（數值求解）|
| 高 $R$ 時滅絕壓力 | 線性增加 | 超線性加速增加 |
| 生物合理性 | 有瑕疵 | 更合理 |

---

## 第七章：島嶼面積效應

### 7.1 物種-面積關係（Species-Area Relationship）

早在 MacArthur-Wilson 之前，生態學家就觀察到一個普遍規律：**島嶼越大，物種越多**。Preston（1962）提出了著名的冪次律：

$$\boxed{S = c \cdot A^z}$$

其中 $S$ 是物種數，$A$ 是島嶼面積，$c$ 和 $z$ 是常數。實測 $z$ 值通常在 $0.25$–$0.35$ 之間。

這個關係在對數-對數圖上是一條直線：$\ln S = \ln c + z \ln A$。

### 7.2 面積如何影響移入率與滅絕率？

**面積影響移入率（$I \uparrow$ 當 $A \uparrow$）**：
- 較大的島嶼是更大的「靶子」，飛散的孢子、種子、動物更容易抵達
- 較大的島嶼有更多樣的棲地（森林、草原、濕地等），可以支持不同生態棲位的物種
- 效果可表示為 $I \propto A^{0.3}$

**面積影響滅絕率（$E \downarrow$ 當 $A \uparrow$）**：
- 較大的島嶼上每個物種可佔用的棲地更多，種群規模（population size）更大
- 種群規模大 → 隨機滅絕（demographic stochasticity）風險低
- 效果可表示為 $E \propto A^{-0.5}$（面積翻倍，滅絕率降低 $\sqrt{2}$ 倍）

### 7.3 含面積參數的模型

將面積 $A$ 納入非線性模型：

$$I(R, A) = \lambda \cdot A^{0.3} \cdot e^{-\alpha R}$$

$$E(R, A) = \frac{\beta}{A^{0.5}} \cdot R^2$$

以 $A = 1$ 為基準，當面積增大時：
- $I$ 曲線整體上移（移入率提高）
- $E$ 曲線整體下移（滅絕率降低）
- 兩條曲線的交點 $R^*$ 向右移，表示**較大島嶼支持更多物種**

### 7.4 數值結果

| 島嶼面積 $A$ | 平衡物種數 $R^*$ | 相對基準 $A=1$ 的增幅 |
|:-----------:|:--------------:|:-------------------:|
| 1（基準）    | 217            | —                   |
| 5           | 298            | +37%                |
| 20          | 378            | +74%                |

### 7.5 Python 實作

```python
def I_with_area(R, lam, alpha, A):
    return lam * (A ** 0.3) * np.exp(-alpha * R)

def E_with_area(R, beta, A):
    return (beta / (A ** 0.5)) * R ** 2

def find_equilibrium(lam, alpha, beta, A):
    """掃描 + 二分法求平衡點"""
    R_scan = np.linspace(1, 1200, 100000)
    diff = I_with_area(R_scan, lam, alpha, A) - E_with_area(R_scan, beta, A)
    sc = np.where(np.diff(np.sign(diff)))[0]
    if len(sc) == 0:
        return None
    r_lo, r_hi = R_scan[sc[0]], R_scan[sc[0]+1]
    for _ in range(60):
        r_mid = 0.5 * (r_lo + r_hi)
        if (I_with_area(r_mid, lam, alpha, A) -
            E_with_area(r_mid, beta, A)) > 0:
            r_lo = r_mid
        else:
            r_hi = r_mid
    return 0.5 * (r_lo + r_hi)

# 計算各面積的平衡點
lam, alpha, beta = 8.0, 0.008, 3e-5
for A in [1, 5, 20]:
    R_star_A = find_equilibrium(lam, alpha, beta, A)
    print(f"A = {A:2d}: R* = {R_star_A:.1f}")
```

### 7.6 保育意涵

這個分析對自然保護有直接意義：

**棲地破碎化的威脅**：當大片森林被開墾切割為零散小塊，每塊的 $A$ 縮小 → $R^*$ 降低。原本存在的物種數超過新的 $R^*$，物種會慢慢滅絕。這個「時間延遲的滅絕」稱為**滅絕債**（extinction debt）。

**大型保護區 vs 多個小型保護區**：生態學上著名的 SLOSS（Single Large Or Several Small）爭論中，島嶼生物地理學支持「一個大型保護區優於許多小型保護區之和」的觀點（當其他條件相同時）。

---

## 附錄一：作業解題流程圖

```
┌────────────────────────────────────┐
│  原始資料輸入                       │
│  R = [0, 36, 80, 155, 210, 240]    │
│  I = [8.0, 3.0, 5.0, 6.5, 4.0, 2.5]│
│  E = [0.0, 0.05, 0.10, 0.50, 1.75, 1.75]│
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  第一題 (a)：線性迴歸               │
│  numpy.polyfit(R, I, 1) → a_I, b_I │
│  numpy.polyfit(R, E, 1) → a_E, b_E │
│  計算 R² 衡量配適度                  │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  第一題 (b)：建立 ODE               │
│  dR/dt = I(R) - E(R)               │
│       = (a_I - a_E) + (b_I - b_E)R │
│  代入數值：dR/dt = 6.4675 - 0.0194R│
└──────────────┬─────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐  ┌──────────────────┐
│ 第一題 (c)   │  │ 第一題 (d)        │
│ 求平衡點 R*  │  │ 求大陸物種庫 P   │
│ I(R*) = E(R*)│  │ I(P) = 0         │
│ R* = 334     │  │ P = -a_I/b_I=547 │
└──────┬───────┘  └──────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│  第一題 (e)：有限差分數值模擬        │
│  R(t+dt) = R(t) + dt * dR/dt       │
│  初始條件：R0=0 和 R0=500          │
│  驗證兩者均收斂到 R* ≈ 334         │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  第二題 (a)：替代非線性模型         │
│  I(R) = λ·exp(-αR)，λ=8，α=0.008  │
│  E(R) = β·R²，β=3×10⁻⁵            │
│  繪圖比較線性 vs 曲線               │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  第二題 (b)：求曲線模型平衡點       │
│  λ·exp(-αR*) = β·(R*)²（無解析解）│
│  掃描 + 二分法 → R* ≈ 217          │
│  穩定性分析：f'(R*) < 0 → 穩定     │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  第二題 (c)：生物機制討論           │
│  指數 I：棲位飽和、優先佔領效應     │
│  二次 E：成對競爭交互作用           │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  第二題 (d)：加入島嶼面積 A         │
│  I(R,A) = λ·A^0.3·exp(-αR)        │
│  E(R,A) = β/A^0.5·R²              │
│  對 A=1,5,20 各求 R*               │
│  結果：R* 隨面積增大而增大          │
└────────────────────────────────────┘
```

---

## 附錄二：常見錯誤與除錯指南

### 錯誤一：迴歸公式符號搞混

**症狀**：算出 $b_I > 0$（移入率隨物種增加而增加），不符合生態直覺

**原因**：`numpy.polyfit` 回傳的是 `[斜率, 截距]`，容易寫錯

**正確寫法**：
```python
coeffs = np.polyfit(R_data, I_data, 1)
slope, intercept = coeffs[0], coeffs[1]  # 明確拆開
# 預期：slope < 0（移入率應隨 R 增加而遞減）
```

**檢查方式**：確認 $b_I \approx -0.011$（負值），$b_E \approx +0.008$（正值）

---

### 錯誤二：$\Delta t$ 選太大導致數值振盪

**症狀**：模擬結果在平衡點附近劇烈震盪，甚至發散到數百或負無窮

**原因**：Euler 方法的穩定性條件要求 $\Delta t < 2/B$，其中 $B = 0.0194$，上限約 103 年。但實務上要可靠，$\Delta t$ 應遠小於特徵時間 $\tau = 51.7$ 年

**解法**：使用 $\Delta t = 0.5$ 年（作業建議值），永遠不要用 $\Delta t > 10$ 年

**測試方式**：嘗試 $\Delta t = 200$ 年，觀察結果是否發散，加深對穩定性的理解

---

### 錯誤三：忘記 $E(0)$ 在生物學上應為零

**症狀**：報告中寫「滅絕率截距 $a_E = -0.274$」但沒有解釋這個負值

**正確說法**：這是線性模型在 $R = 0$ 附近的外推誤差。實際上當 $R = 0$ 時島嶼沒有物種，自然沒有滅絕率。線性函數過度外推造成輕微負截距。若要生物學上嚴謹，應加上 $E(R) \geq 0$ 的約束，或改用二次模型 $E(R) = \beta R^2$（自然滿足 $E(0) = 0$）。

---

### 錯誤四：混淆 $R^*$ 和 $P$

**$R^*$（動態平衡點）**：移入率等於滅絕率時的物種數。島嶼上有物種在來，也有物種在滅絕，但兩者速率相等，淨變化為零。$R^* \approx 334$。

**$P$（大陸物種庫）**：大陸上存在的物種總數。當島嶼物種數達到 $P$ 時，所有物種都已在島上，移入率降為零。$P \approx 547$。

**關係**：$R^* < P$，因為在 $R^*$ 時滅絕壓力阻止物種數繼續增加。

---

### 錯誤五：matplotlib 圖形缺少軸標籤和單位

**症狀**：圖片上看不出 x 軸和 y 軸代表什麼，扣分

**模板**：
```python
ax.set_xlabel('物種數 $R$（種）', fontsize=12)    # 必須有標籤 + 單位
ax.set_ylabel('速率（物種 / 年）', fontsize=12)   # 必須有標籤 + 單位
ax.set_title('圖題要明確描述內容', fontsize=13)   # 圖題必要
ax.legend(fontsize=10)                            # 如有多條線，必須加圖例
```

每張圖都要有：
- [ ] x 軸標籤（含單位）
- [ ] y 軸標籤（含單位）
- [ ] 圖題
- [ ] 圖例（如有多條線）

---

### 錯誤六：模擬迴圈的差一錯誤（off-by-one error）

**症狀**：模擬結果只有 $n-1$ 步，最後一個時間點沒有資料；或陣列索引超界

**原因**：迴圈範圍設定錯誤

**錯誤寫法**：
```python
n_steps = int(t_max / dt)  # 漏掉了最後一步！
for i in range(n_steps):   # 當 i = n_steps-1 時，R[i+1] 越界！
    R[i+1] = ...
```

**正確寫法**：
```python
n_steps = int(t_max / dt) + 1  # +1 包含終點
R = np.zeros(n_steps)
t = np.linspace(0, t_max, n_steps)

for i in range(n_steps - 1):   # 只到倒數第二個索引
    R[i+1] = R[i] + dt * dRdt(R[i])
```

---

### 快速除錯檢查清單

在提交作業前，逐一確認：

- [ ] $b_I < 0$（移入率斜率為負）
- [ ] $b_E > 0$（滅絕率斜率為正）
- [ ] $R^* \approx 334$（線性模型）
- [ ] $P \approx 547$（大陸物種庫）
- [ ] 模擬從 $R_0 = 0$ 和 $R_0 = 500$ 都收斂到同一個 $R^*$
- [ ] 曲線模型 $R^* \approx 217$
- [ ] 面積越大，$R^*$ 越高
- [ ] 所有圖形有完整標籤

---

*本教學文件涵蓋 BME5113 HW1 所需的所有知識基礎。建議先通讀一遍，動手跑每個程式碼範例，再嘗試自行完成作業。祝學習順利！*
