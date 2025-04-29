import requests
import pandas as pd

def get_binance_klines(symbol="SOLUSDT", interval="30m", limit=30):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    closes = [float(item[4]) for item in data]
    return closes

def check_golden_death_cross(closes, short=5, long=20):
    df = pd.DataFrame({"close": closes})
    df["ma_short"] = df["close"].rolling(window=short).mean()
    df["ma_long"] = df["close"].rolling(window=long).mean()
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    if prev["ma_short"] < prev["ma_long"] and curr["ma_short"] > curr["ma_long"]:
        return "黃金交叉"
    elif prev["ma_short"] > prev["ma_long"] and curr["ma_short"] < curr["ma_long"]:
        return "死亡交叉"
    else:
        return "無交叉"

if __name__ == "__main__":
    closes = get_binance_klines()
    result = check_golden_death_cross(closes)
    print(f"30m SOLUSDT: {result}")