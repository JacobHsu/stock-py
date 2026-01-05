# 台股黃金交叉自動判斷工具

本工具可自動判斷台灣 0050 或中型100成分股，哪些股票出現「黃金交叉」或「死亡交叉」技術訊號。

## 自動報告

每週一台灣時間 9:30，GitHub Action 會自動運行分析並生成報告。

📊 **查看最新報告**: [https://YOUR_USERNAME.github.io/stock-py/](https://YOUR_USERNAME.github.io/stock-py/)

---

## 檔案說明

- `golden_cross.py`：命令列工具，判斷黃金交叉
- `generate_report.py`：生成 HTML 報告（GitHub Action 使用）
- `stocks_0050.csv`：台灣50（0050）成分股清單
- `stocks_mid100.csv`：台灣中型100成分股清單
- `.github/workflows/stock-analysis.yml`：GitHub Action 工作流配置

---

## 依賴套件

請先安裝必要的 Python 套件：

```bash
pip install yfinance pandas
```

---

## 使用方式

### 1. 生成 HTML 報告（推薦）

分析 0050 和 Mid100 所有成分股，生成精美的網頁報告：

```bash
python generate_report.py
```

報告會生成在 `docs/index.html`，直接用瀏覽器打開即可查看：

```bash
# Windows
start docs/index.html

# macOS
open docs/index.html

# Linux
xdg-open docs/index.html
```

### 2. 命令列查詢（快速查看）

查詢 0050 成分股黃金交叉：

```bash
python golden_cross.py
```

查詢中型100成分股黃金交叉：

```bash
python golden_cross.py mid100
```

---

## 輸出說明

### HTML 報告
- 顯示 0050 和 Mid100 的黃金交叉和死亡交叉股票
- 精美的網頁介面，方便查看
- 包含更新時間和完整統計

### 命令列輸出
- 若有股票出現黃金交叉，會輸出：
  ```
  黃金交叉: 股票1(代碼1), 股票2(代碼2), ...
  ```
- 若無任何股票出現黃金交叉，會輸出：
  ```
  無黃金交叉
  ```

---

## 股票清單格式

`stocks_0050.csv` 台灣50成份股
`stocks_mid100.csv` 中型100成份股

---

## GitHub Pages 設置

首次使用需要啟用 GitHub Pages：

1. 進入 GitHub 倉庫的 **Settings** > **Pages**
2. 在 **Build and deployment** > **Source** 下選擇 `Deploy from a branch`
3. 在 **Branch** 下選擇 `main` 分支和 `/docs` 文件夾
4. 點擊 **Save**
5. 等待部署完成後，訪問 `https://YOUR_USERNAME.github.io/stock-py/`

**手動觸發分析**：進入 **Actions** 標籤頁，選擇 "Stock Analysis" 工作流，點擊 "Run workflow"

報告會自動提交到 main 分支的 `docs/` 文件夾，GitHub Pages 會自動更新

---

## 技術說明

- **黃金交叉**：短期均線（MA20）向上穿越長期均線（MA60），視為買入信號
- **死亡交叉**：短期均線（MA20）向下穿越長期均線（MA60），視為賣出信號
- **數據來源**：Yahoo Finance
- **分析週期**：近 6 個月日線數據
- **策略類型**：中線交易策略（MA20/MA60）
- **技術圖表**：點擊股票可查看 IFA 技術分析圖表
