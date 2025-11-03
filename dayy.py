import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests

# -------- Fetch NSE 500 stocks automatically -------- #
@st.cache_data(ttl=86400)
def get_nse500():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    df = pd.read_csv(url)
    df["Symbol"] = df["Symbol"].astype(str) + ".NS"
    return df["Symbol"].tolist()

nse500_symbols = get_nse500()

# -------- App UI -------- #
st.title("📈 NSE-500 Tight Range (0.30%-0.40%) Intraday Screener")
st.caption("30-min timeframe | EMA-21 Support | Volume > SMA-20")

progress = st.progress(0)
results = []

# -------- Scanning -------- #
for i, symbol in enumerate(nse500_symbols):
    try:
        data = yf.download(symbol, period="5d", interval="30m", progress=False)
        data.dropna(inplace=True)

        data["EMA21"] = data["Close"].ewm(span=21).mean()
        data["Vol20"] = data["Volume"].rolling(20).mean()

        latest = data.iloc[-1]

        high, low, close = latest["High"], latest["Low"], latest["Close"]
        ema21 = latest["EMA21"]
        vol, vol20 = latest["Volume"], latest["Vol20"]

        range_pct = ((high - low) / close) * 100
        ema_dist = abs(close - ema21) / ema21 * 100

        cond_range = (0.30 <= range_pct <= 0.40)
        cond_ema = (ema_dist <= 0.50)
        cond_vol = (vol > vol20)

        if cond_range and cond_ema and cond_vol:
            results.append([
                symbol.replace(".NS",""),
                round(close,2),
                round(range_pct,2),
                round(ema_dist,2),
                int(vol),
                int(vol20)
            ])
    except Exception:
        pass

    progress.progress((i+1)/len(nse500_symbols))

# -------- Output -------- #
df = pd.DataFrame(results, columns=["Stock","CMP","Range %","EMA Dist %","Volume","Avg Vol(20)"])

st.subheader("🎯 Stocks Meeting Criteria")
st.dataframe(df)
st.success(f"✅ Total stocks found: **{len(df)}**")

st.caption("Strategy: Tight Range + EMA 21 Support + Volume Surge | Designed for Intraday Breakout Trades ⚡")
