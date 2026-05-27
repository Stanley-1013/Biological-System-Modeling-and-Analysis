# HW5 手寫版（精簡）

> 給手寫繳交用。**粗體 [貼圖]** 直接貼程式輸出圖；其餘段落只寫關鍵式子與數字。
> 完整推導見 [SOLUTION.md](SOLUTION.md)；教學見 [TUTORIAL.md](TUTORIAL.md)。

---

## P1 — 變異數傳播 (25%)

**通用 (Eq. 9.3，p.186)**：$\;\mathrm{var}(z)\approx\sum_i\sum_j\dfrac{\partial f}{\partial x_i}\dfrac{\partial f}{\partial x_j}\sigma_{ij}$

不相關時 $\sigma_{ij}=0\,(i\neq j)$；相關時加 cross-term $2\,(\partial f/\partial x)(\partial f/\partial y)\sigma_{xy}$。

### (1) $z = e^{k_1 x}$

$\partial z/\partial k_1 = x e^{k_1 x},\;\; \partial z/\partial x = k_1 e^{k_1 x}$

- **Uncorr**: $\sigma_z^{2} = (k_1^{2}\sigma_x^{2} + x^{2}\sigma_{k_1}^{2})\,e^{2k_1 x}$
- **Corr**:   $\sigma_z^{2} = (k_1^{2}\sigma_x^{2} + 2k_1 x\,\sigma_{xk_1} + x^{2}\sigma_{k_1}^{2})\,e^{2k_1 x}$

### (2) $z = k_1\cos(k_2 x) + k_3\sin(k_4 y)$

6 變數，偏微：
$\partial/\partial k_1=\cos(k_2x),\;\partial/\partial k_2=-k_1 x\sin(k_2x),\;\partial/\partial k_3=\sin(k_4y),\;\partial/\partial k_4=k_3 y\cos(k_4y)$
$\partial/\partial x=-k_1k_2\sin(k_2x),\;\partial/\partial y=k_3k_4\cos(k_4y)$

- **Uncorr**:
$\sigma_z^{2}=\cos^{2}(k_2x)\sigma_{k_1}^{2}+k_1^{2}x^{2}\sin^{2}(k_2x)\sigma_{k_2}^{2}+\sin^{2}(k_4y)\sigma_{k_3}^{2}+k_3^{2}y^{2}\cos^{2}(k_4y)\sigma_{k_4}^{2}+k_1^{2}k_2^{2}\sin^{2}(k_2x)\sigma_x^{2}+k_3^{2}k_4^{2}\cos^{2}(k_4y)\sigma_y^{2}$
- **Corr** (only $(x,y)$): 加 $-2k_1k_2k_3k_4\sin(k_2x)\cos(k_4y)\,\sigma_{xy}$

### (3) $z = x^{3}y^{-3}$

$\partial z/\partial x=3x^{2}/y^{3},\;\partial z/\partial y=-3x^{3}/y^{4}$

- **Uncorr**: $\sigma_z^{2}=\dfrac{9x^{4}}{y^{8}}(y^{2}\sigma_x^{2}+x^{2}\sigma_y^{2})$
- **Corr**:   $\sigma_z^{2}=\dfrac{9x^{4}}{y^{8}}(y^{2}\sigma_x^{2}+x^{2}\sigma_y^{2}-2xy\,\sigma_{xy})$

或相對誤差形式：$\;\dfrac{\sigma_z}{|z|}\approx 3\sqrt{(\sigma_x/x)^{2}+(\sigma_y/y)^{2}-2\rho_{xy}(\sigma_x/x)(\sigma_y/y)}$

---

## P2 — 滅絕模型 $P=(d/b)^{n}$ 敏感度 (25%)

**Eq. 9.4**: $\;P = (d/b)^{n}$；mean $d=0.8,\,b=0.9,\,n=10$；std $\sigma=(0.157,\,0.174,\,0.69)$
**$P_\mathrm{det}=(0.8/0.9)^{10}=0.308$**

### (a) Eq. 9.1 單參數擾動 $S=(\Delta R/R_n)/(\Delta P/P_n)$

| param | 2% | 10% | 20% | mean$|S|$ |
|:-:|:-:|:-:|:-:|:-:|
| d | $S^\pm=(10.95,9.15)$ | $(15.94,6.51)$ | $(25.96,4.46)$ | **12.16** |
| b | $(-8.98,-11.19)$ | $(-6.14,-18.68)$ | $(-4.19,-41.57)$ | **15.13** |
| n | $(-1.16,-1.19)$ | $(-1.11,-1.25)$ | $(-1.05,-1.33)$ | **1.18** |

**排序**：$\;|S_b| \gtrsim |S_d| \gg |S_n|$ （$b$ 與 $d$ 近乎並列；變異數貢獻 50.7% vs 49.2%）

### (b) 解析 var(Eq. 9.5)

$\mathrm{var}(P)=\left(\dfrac{n\bar d^{n-1}}{\bar b^{n}}\right)^{2}\!\sigma_d^{2}+\left(\dfrac{n\bar d^{n}}{\bar b^{n+1}}\right)^{2}\!\sigma_b^{2}+\left(\ln\tfrac{\bar d}{\bar b}\cdot P\right)^{2}\sigma_n^{2}$

**= 0.7203，$\sigma_P=0.849$，CI=[−1.36, 1.97]**

| 項 | var 貢獻 | 占比 |
|:-:|--:|--:|
| d | 0.365 | 50.7% |
| b | 0.355 | 49.2% |
| n | 0.001 |  0.1% |

### (c) Monte Carlo (N=10000, log-normal, 拒絕 d≥b)

mean=0.206，median=0.094，2.5–97.5% = **[0.001, 0.883]**

### 比較

兩法皆指向 **$b\sim d \gg n$**；解析法因 Taylor 一階假設+常態假設導致 CI 失控（超出 [0,1]）；
MC 結果與書 Fig. 9.6 一致：右偏分布，0.308 不具實質意義。

**[貼圖 fig2_problem2_sensitivity_mc.png]**

---

## P3 — Gause Case III 局部穩定性 (25%)

**Eq. 9.13/9.14**:
$\dot n_1 = r_1 n_1(1-(n_1+\alpha n_2)/K_1),\;\;\dot n_2 = r_2 n_2(1-(n_2+\beta n_1)/K_2)$

**參數** (p.208 except $K_2,\beta$)：$r_1=r_2=0.05,\;\alpha=0.2,\;K_1=200,\;K_2=800,\;\beta=3$

### Case III 條件確認 (Fig. 9.11c)

$$K_1/\alpha > K_2 \;\text{且}\; K_1 < K_2/\beta$$

$K_1/\alpha = 1000 > K_2 = 800$ ✓ 且 $K_1 = 200 < K_2/\beta = 266.7$ ✓ → **Case III**

### 四個平衡點 (Eq. 9.17/9.18)

| 點 | 座標 |
|:-:|:--|
| $E_0$ | $(0,0)$ |
| $E_1$ | $(K_1, 0) = (200, 0)$ |
| $E_2$ | $(0, K_2) = (0, 800)$ |
| $E_3$ | $((K_1-\alpha K_2)/(1-\alpha\beta),\;(K_2-\beta K_1)/(1-\alpha\beta)) = (100, 500)$ |

### Jacobian (Eq. 9.40)

$J_{11}=r_1-2r_1 n_1/K_1-r_1 n_2\alpha/K_1,\;J_{12}=-r_1 n_1\alpha/K_1,\;J_{21}=-r_2 n_2\beta/K_2,\;J_{22}=r_2-2r_2 n_2/K_2-r_2 n_1\beta/K_2$

代入 $(100,500)$：
$J_{11}=0.05-0.05-0.025=-0.025,\;J_{12}=-0.005,\;J_{21}=-0.09375,\;J_{22}=0.05-0.0625-0.01875=-0.03125$

$$\mathbf J(E_3)=\begin{pmatrix}-0.025 & -0.005\\ -0.09375 & -0.03125\end{pmatrix}$$

**特徵方程**: $\lambda^{2}+0.05625\lambda+0.0003125=0$

$\lambda_{1,2}=\dfrac{-0.05625\pm\sqrt{0.05625^{2}-4(0.0003125)}}{2}=\dfrac{-0.05625\pm 0.04375}{2}$

$$\boxed{\;\lambda_1=-0.00625,\;\lambda_2=-0.05\;\;(\text{both negative}) \Rightarrow \textbf{stable node}\;}$$

### 其他平衡點驗證

| 點 | $\lambda_{1,2}$ | 類型 |
|:-:|:--|:-:|
| $(0,0)$ | $(+0.05,+0.05)$ | unstable node |
| $(200,0)$ | $(-0.05,+0.0125)$ | **saddle** |
| $(0,800)$ | $(+0.01,-0.05)$ | **saddle** |
| **(100,500)** | $(-0.05,-0.00625)$ | **stable node** ✓ |

**[貼圖 fig3_problem3_gause_caseIII.png]**

---

## P4 — 自訂 2-D 系統 (25%)

**模型**：$\dot x = a_1 x^{2}-a_2 x^{3}-bxy,\;\;\dot y = dxy-fy^{2}$
**參數**：$a_1=1,\;a_2=0.05,\;b=5,\;d=1,\;f=10$

### (1) Nullclines

| nullcline | 方程 | 向量方向 |
|:--|:--|:--|
| $\dot x=0$: $x=0$ | $y$ 軸 | $\dot y=-fy^{2}<0$ → 向下 |
| $\dot x=0$: $y=(a_1 x-a_2 x^{2})/b$ | 拋物線 | $\dot y=xy(0.1x-1)=0.1xy(x-10)$；$x<10$ 向下、$x>10$ 向上 |
| $\dot y=0$: $y=0$ | $x$ 軸 | $\dot x=x^{2}(a_1-a_2 x)$；$x<20$ 向右、$x>20$ 向左 |
| $\dot y=0$: $y=dx/f=x/10$ | 過原點直線 | $\dot x=0.05x^{2}(10-x)$；$x<10$ 向右、$x>10$ 向左 |

### (2) 平衡點（符號）

$\;\;E_0=(0,0),\;\;E_1=(a_1/a_2,\,0),\;\;E_2=\left(\dfrac{a_1 f-bd}{a_2 f},\;\dfrac{d(a_1 f-bd)}{a_2 f^{2}}\right)$

代入數值：$E_0=(0,0),\,E_1=(20,0),\,E_2=(10,1)$

### (3) Jacobian

$\mathbf J = \begin{pmatrix}2a_1 x-3a_2 x^{2}-by & -bx\\ dy & dx-2fy\end{pmatrix}$

#### $E_0=(0,0)$：$\mathbf J=\mathbf 0$ → 線性化失效（degenerate）

#### $E_1=(20,0)$:
$\mathbf J=\begin{pmatrix}-20&-100\\ 0& 20\end{pmatrix}$；上三角，$\lambda=(-20,\,20)$，$\det=-400<0$ → **saddle**

#### $E_2=(10,1)$:
$\mathbf J=\begin{pmatrix}0&-50\\ 1&-10\end{pmatrix}$；$\mathrm{tr}=-10,\;\det=50,\;\mathrm{tr}^{2}-4\det=-100<0$
→ $\lambda=-5\pm 5i$ → **stable spiral** ✓

### (4) 為何穩定 / 不穩定

- $E_2$ **stable spiral**：Hartman-Grobman 保證局部拓樸等價於線性化；$\mathrm{Re}\,\lambda=-5<0$ → 軌跡螺旋收斂，週期 $T=2\pi/5\approx 1.26$。
- $E_1$ **saddle**：兩特徵值一正一負，沿不穩定流形（$\lambda=+20$ 對應向量）爆炸增長。
- $E_0$ **degenerate**：Jacobian 全 0；改看高階主導項 $\dot x\approx a_1 x^{2}>0$（$x$ 自離原點），非吸引子。

**[貼圖 fig4_problem4_nullclines.png]**

---

## 摘要一頁

| 題 | 結論 | 關鍵數字 |
|:-:|:--|:--|
| P1 | Eq.9.3 推三式 var；不相關 vs 相關差 cross-term | 三題公式 boxed 在 SOLUTION |
| P2 | 敏感度 $b > d \gg n$；解析 var(P)=0.72 但 CI 失控；MC 重現書 Fig.9.6 | $|S_b|=15,\,|S_d|=12,\,|S_n|=1$ |
| P3 | Case III 共存點 $(100,500)$ **stable** | $\lambda=(-0.05,-0.006)$ |
| P4 | $E_2=(10,1)$ stable spiral；$E_1$ saddle；$E_0$ degenerate | $\lambda(E_2)=-5\pm 5i$ |

---

*程式：[hw5_solution.py](hw5_solution.py)；圖檔：[hw5_figures/](hw5_figures/)；完整版：[SOLUTION.md](SOLUTION.md)；教學：[TUTORIAL.md](TUTORIAL.md)*
