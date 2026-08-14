import numpy as np
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator

def add_indicators(df):
    x = df.copy()

    x["ema20"] = EMAIndicator(x["Close"], window=20).ema_indicator()
    x["ema50"] = EMAIndicator(x["Close"], window=50).ema_indicator()
    x["ema200"] = EMAIndicator(x["Close"], window=200).ema_indicator()

    x["rsi"] = RSIIndicator(x["Close"], window=14).rsi()

    macd = MACD(x["Close"], window_slow=26, window_fast=12, window_sign=9)
    x["macd"] = macd.macd()
    x["macd_signal"] = macd.macd_signal()
    x["macd_hist"] = macd.macd_diff()

    adx = ADXIndicator(x["High"], x["Low"], x["Close"], window=14)
    x["adx"] = adx.adx()

    x["obv"] = OnBalanceVolumeIndicator(x["Close"], x["Volume"]).on_balance_volume()
    x["mfi"] = MFIIndicator(
        x["High"], x["Low"], x["Close"], x["Volume"], window=14
    ).money_flow_index()

    tr = pd.concat([
        x["High"] - x["Low"],
        (x["High"] - x["Close"].shift()).abs(),
        (x["Low"] - x["Close"].shift()).abs()
    ], axis=1).max(axis=1)
    x["atr"] = tr.rolling(14).mean()
    x["atr_pct"] = x["atr"] / x["Close"] * 100

    x["vol_avg20"] = x["Volume"].rolling(20).mean()
    x["volume_ratio"] = x["Volume"] / x["vol_avg20"]

    x["support20"] = x["Low"].rolling(20).min()
    x["resistance20"] = x["High"].rolling(20).max()
    x["support60"] = x["Low"].rolling(60).min()
    x["resistance60"] = x["High"].rolling(60).max()

    x["high52"] = x["High"].rolling(252, min_periods=60).max()
    x["low52"] = x["Low"].rolling(252, min_periods=60).min()

    x["obv_slope"] = x["obv"].diff(10)

    return x.dropna()
