import yfinance as yf
import pandas as pd
import sys

def load_stocks_from_csv(filename):
    df = pd.read_csv(filename)
    return dict(zip(df['name'], df['code']))

def get_yf_closes(ticker, period="3mo", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    return df['Close']

def check_golden_death_cross(closes, short=5, long=20):
    if closes is None or closes.empty:
        return "資料不足"
    # 若已經是DataFrame就直接用，否則轉成DataFrame
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

if __name__ == "__main__":
    # 預設用 0050，參數可選 mid100
    group = "0050"
    if len(sys.argv) > 1:
        group = sys.argv[1].lower()
    if group == "0050":
        stocks = load_stocks_from_csv("stocks_0050.csv")
    elif group == "mid100":
        stocks = load_stocks_from_csv("stocks_mid100.csv")
    else:
        print("未知的成分股組別，只支援 0050 或 mid100")
        sys.exit(1)

    golden_list = []
    for name, ticker in stocks.items():
        closes = get_yf_closes(ticker, period="3mo")
        if closes is None or closes.empty or len(closes) < 21:
            continue
        result = check_golden_death_cross(closes)
        if result == "黃金交叉":
            golden_list.append(f"{name}({ticker})")
    if golden_list:
        print("黃金交叉:", ", ".join(golden_list))
    else:
        print("無黃金交叉")
