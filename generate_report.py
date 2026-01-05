import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def load_stocks_from_csv(filename):
    df = pd.read_csv(filename)
    return dict(zip(df['name'], df['code']))

def get_yf_closes(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        return df['Close']
    except:
        return None

def check_golden_death_cross(closes, short=20, long=60):
    if closes is None or closes.empty:
        return "資料不足"

    if isinstance(closes, pd.DataFrame):
        df = closes.rename(columns={closes.columns[0]: "close"})
    else:
        df = closes.to_frame(name="close")

    df["ma_short"] = df["close"].rolling(window=short).mean()
    df["ma_long"] = df["close"].rolling(window=long).mean()

    if len(df) < long + 1:
        return "資料不足"

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if pd.isna(prev["ma_short"]) or pd.isna(prev["ma_long"]) or pd.isna(curr["ma_short"]) or pd.isna(curr["ma_long"]):
        return "資料不足"

    if prev["ma_short"] < prev["ma_long"] and curr["ma_short"] > curr["ma_long"]:
        return "黃金交叉"
    elif prev["ma_short"] > prev["ma_long"] and curr["ma_short"] < curr["ma_long"]:
        return "死亡交叉"
    else:
        return "無交叉"

def analyze_stocks(group_name, stocks):
    golden_list = []
    death_list = []

    for name, ticker in stocks.items():
        print(f"分析 {name} ({ticker})...")
        closes = get_yf_closes(ticker, period="6mo")
        if closes is None or closes.empty or len(closes) < 61:
            continue

        result = check_golden_death_cross(closes)
        if result == "黃金交叉":
            golden_list.append({"name": name, "ticker": ticker})
        elif result == "死亡交叉":
            death_list.append({"name": name, "ticker": ticker})

    return golden_list, death_list

def generate_html_report(report_0050, report_mid100):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台股技術分析報告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Microsoft JhengHei";
            background-color: hsl(0 0% 98%);
            min-height: 100vh;
            padding: 2rem 1rem;
            color: hsl(240 10% 3.9%);
            line-height: 1.5;
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
        }}
        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            color: hsl(240 10% 3.9%);
            margin-bottom: 0.5rem;
        }}
        .update-time {{
            color: hsl(240 3.8% 46.1%);
            font-size: 0.875rem;
        }}
        .section {{
            background: white;
            border: 1px solid hsl(240 5.9% 90%);
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            overflow: hidden;
        }}
        .section-header {{
            padding: 1.5rem;
            border-bottom: 1px solid hsl(240 5.9% 90%);
        }}
        .section-header h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: hsl(240 10% 3.9%);
        }}
        .section-content {{
            padding: 1.5rem;
        }}
        .subsection {{
            margin-bottom: 2rem;
        }}
        .subsection:last-child {{
            margin-bottom: 0;
        }}
        .subsection-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid hsl(240 5.9% 90%);
        }}
        .subsection-header h3 {{
            font-size: 1.125rem;
            font-weight: 600;
            color: hsl(240 10% 3.9%);
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 9999px;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 600;
            line-height: 1;
        }}
        .badge-golden {{
            background-color: hsl(47.9 95.8% 53.1% / 0.15);
            color: hsl(25 95% 35%);
            border: 1px solid hsl(47.9 95.8% 53.1% / 0.3);
        }}
        .badge-death {{
            background-color: hsl(240 10% 3.9% / 0.08);
            color: hsl(240 10% 3.9%);
            border: 1px solid hsl(240 5.9% 90%);
        }}
        .stock-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 0.75rem;
        }}
        .stock-item {{
            display: block;
            background: hsl(0 0% 100%);
            border: 1px solid hsl(240 5.9% 90%);
            border-radius: 0.375rem;
            padding: 0.875rem 1rem;
            transition: all 0.15s ease;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
        }}
        .stock-item:hover {{
            border-color: hsl(240 5.9% 70%);
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            transform: translateY(-1px);
        }}
        .stock-item.golden {{
            border-left: 3px solid hsl(47.9 95.8% 53.1%);
        }}
        .stock-item.golden:hover {{
            background-color: hsl(47.9 95.8% 53.1% / 0.03);
        }}
        .stock-item.death {{
            border-left: 3px solid hsl(240 5.9% 30%);
        }}
        .stock-item.death:hover {{
            background-color: hsl(240 5.9% 96%);
        }}
        .stock-name {{
            font-weight: 600;
            color: hsl(240 10% 3.9%);
            font-size: 0.9375rem;
            margin-bottom: 0.25rem;
        }}
        .stock-ticker {{
            font-size: 0.8125rem;
            color: hsl(240 3.8% 46.1%);
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        }}
        .empty-message {{
            color: hsl(240 3.8% 46.1%);
            text-align: center;
            padding: 2rem;
            background: hsl(240 4.8% 95.9%);
            border-radius: 0.375rem;
            font-size: 0.875rem;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid hsl(240 5.9% 90%);
            text-align: center;
        }}
        .footer-text {{
            color: hsl(240 3.8% 46.1%);
            font-size: 0.875rem;
            line-height: 1.75;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 1rem 0.75rem;
            }}
            h1 {{
                font-size: 1.75rem;
            }}
            .section-header, .section-content {{
                padding: 1rem;
            }}
            .stock-grid {{
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                gap: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>台股技術分析報告</h1>
            <div class="update-time">更新時間：{now}</div>
        </header>

        <div class="section">
            <div class="section-header">
                <h2>台灣50成分股 (0050)</h2>
            </div>
            <div class="section-content">
                <div class="subsection">
                    <div class="subsection-header">
                        <h3>黃金交叉</h3>
                        <span class="badge badge-golden">{len(report_0050['golden'])} 檔</span>
                    </div>
                    {generate_stock_list(report_0050['golden'], 'golden')}
                </div>

                <div class="subsection">
                    <div class="subsection-header">
                        <h3>死亡交叉</h3>
                        <span class="badge badge-death">{len(report_0050['death'])} 檔</span>
                    </div>
                    {generate_stock_list(report_0050['death'], 'death')}
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <h2>中型100成分股 (Mid100)</h2>
            </div>
            <div class="section-content">
                <div class="subsection">
                    <div class="subsection-header">
                        <h3>黃金交叉</h3>
                        <span class="badge badge-golden">{len(report_mid100['golden'])} 檔</span>
                    </div>
                    {generate_stock_list(report_mid100['golden'], 'golden')}
                </div>

                <div class="subsection">
                    <div class="subsection-header">
                        <h3>死亡交叉</h3>
                        <span class="badge badge-death">{len(report_mid100['death'])} 檔</span>
                    </div>
                    {generate_stock_list(report_mid100['death'], 'death')}
                </div>
            </div>
        </div>

        <footer>
            <div class="footer-text">
                <p>本報告僅供參考，不構成投資建議。投資有風險，請謹慎評估。</p>
                <p>數據來源：Yahoo Finance | MA5/MA20 交叉策略</p>
            </div>
        </footer>
    </div>
</body>
</html>"""

    return html

def generate_stock_list(stocks, style_class):
    if not stocks:
        return '<div class="empty-message">目前無符合條件的股票</div>'

    items = []
    for stock in stocks:
        # 提取股票代碼（去掉 .TW 後綴）
        stock_code = stock['ticker'].replace('.TW', '')
        ifa_url = f"https://ifa.ai/tw-stock/{stock_code}/technical-chart"

        items.append(f'''
            <a href="{ifa_url}" target="_blank" class="stock-item {style_class}">
                <div class="stock-name">{stock['name']}</div>
                <div class="stock-ticker">{stock['ticker']}</div>
            </a>
        ''')

    return f'<div class="stock-grid">{"".join(items)}</div>'

if __name__ == "__main__":
    print("=== 開始分析台股 ===")

    # 分析 0050 成分股
    print("\n分析台灣50成分股...")
    stocks_0050 = load_stocks_from_csv("stocks_0050.csv")
    golden_0050, death_0050 = analyze_stocks("0050", stocks_0050)

    # 分析 Mid100 成分股
    print("\n分析中型100成分股...")
    stocks_mid100 = load_stocks_from_csv("stocks_mid100.csv")
    golden_mid100, death_mid100 = analyze_stocks("mid100", stocks_mid100)

    # 生成報告
    print("\n生成 HTML 報告...")
    report_0050 = {"golden": golden_0050, "death": death_0050}
    report_mid100 = {"golden": golden_mid100, "death": death_mid100}

    html_content = generate_html_report(report_0050, report_mid100)

    # 創建輸出目錄
    os.makedirs("docs", exist_ok=True)

    # 寫入 HTML 文件
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("\n=== 分析完成 ===")
    print(f"0050 黃金交叉: {len(golden_0050)} 檔")
    print(f"0050 死亡交叉: {len(death_0050)} 檔")
    print(f"Mid100 黃金交叉: {len(golden_mid100)} 檔")
    print(f"Mid100 死亡交叉: {len(death_mid100)} 檔")
    print(f"\nHTML 報告已生成：docs/index.html")
