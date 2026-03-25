# BME5113 作業撰寫規範

## 課程資訊

- **課程**：BME5113 生物系統建模與分析 (Biological Systems Modeling and Analysis)
- **系所**：國立臺灣大學 生物機電工程學系 (Dept. of Biomechatronics Engineering, NTU)
- **學期**：2025 春季

## 繳交方式

- 平台：NTU COOL 課程網站
- 繳交內容：
  1. **作業報告**（PDF 格式）
  2. **程式碼檔案**（.py / .m / .cpp）

## 報告格式要求

1. 數學推導需呈現關鍵中間步驟（不只寫最終答案）
2. 程式碼需截圖貼入報告對應題目下方
3. 模擬結果圖需嵌入報告中，附軸標籤與圖例
4. Forrester 圖可手繪掃描或程式產生，需標示所有元素
5. 單位驗證（dimensional analysis）需列出每個參數的單位

## 遲交規定

| 遲交天數 | 扣分 |
|:--------:|:----:|
| 1 天 | -10% |
| 2 天 | -20% |
| 3 天 | -30% |
| 4 天 | -40% |
| 5 天 | -50% |
| >5 天 | 不接受 |

## 建議檔案結構

```
Homework/hwN/
├── C3HW0N_2025.pdf       # 題目 PDF
├── SOLUTION.md            # 解題報告 Markdown 原始檔
├── TUTORIAL.md            # 教學文件
├── hwN_solution.py        # Python 程式碼
└── hwN_figures/           # 輸出圖片
    ├── fig1_xxx.png
    └── fig2_xxx.png
```

## 轉 PDF 方式

| 方式 | 操作 |
|------|------|
| VS Code 擴充套件 | 安裝 Markdown PDF → 右鍵 → Export (PDF) |
| Pandoc | `pandoc SOLUTION.md -o SOLUTION.pdf --pdf-engine=xelatex -V CJKmainfont="Noto Sans CJK TC"` |
| Google Doc | 複製 Markdown 貼上 → 匯出 PDF |

## 程式碼截圖

教授要求報告中附上程式碼截圖：
1. 在 VS Code 中開啟 .py 檔
2. 字型調大（Ctrl++）
3. 分區塊截圖（每題的相關程式碼）
4. 貼入報告對應題目下方
