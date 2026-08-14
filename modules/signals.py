import math

def _round(v):
    if v is None:
        return None
    return float(v)

def analyze_stock(df, symbol, name, min_avg_value=500_000, min_rr=1.5):
    r = df.iloc[-1]
    p = float(r["Close"])

    avg_value = float((df["Close"] * df["Volume"]).tail(20).mean())
    if avg_value < min_avg_value:
        return None

    score = 0
    reasons = []

    # 1) Trend — 20 points
    if r["ema20"] > r["ema50"]:
        score += 5
        reasons.append("EMA20 فوق EMA50")
    if r["ema50"] > r["ema200"]:
        score += 10
        reasons.append("EMA50 فوق EMA200")
    if p > r["ema20"]:
        score += 5
        reasons.append("السعر فوق EMA20")

    # 2) RSI — 10
    if 45 <= r["rsi"] <= 65:
        score += 10
        reasons.append("RSI في منطقة مناسبة للاتجاه")
    elif 35 <= r["rsi"] < 45:
        score += 6
        reasons.append("RSI منخفض نسبيًا مع فرصة ارتداد")
    elif r["rsi"] < 35:
        score += 4
        reasons.append("RSI منخفض جدًا؛ فرصة انعكاس محتملة")

    # 3) MACD — 10
    if r["macd"] > r["macd_signal"]:
        score += 7
        reasons.append("MACD إيجابي")
    if r["macd_hist"] > 0 and df["macd_hist"].iloc[-1] > df["macd_hist"].iloc[-2]:
        score += 3
        reasons.append("MACD Histogram يتحسن")

    # 4) ADX — 10
    if r["adx"] >= 25:
        score += 10
        reasons.append("ADX يؤكد قوة الاتجاه")
    elif r["adx"] >= 20:
        score += 6
        reasons.append("ADX متوسط")

    # 5) Volume — 10
    if r["volume_ratio"] >= 1.5:
        score += 10
        reasons.append("ارتفاع قوي في حجم التداول")
    elif r["volume_ratio"] >= 1.1:
        score += 5
        reasons.append("حجم التداول أعلى من المتوسط")

    # 6) OBV/MFI — 10
    if r["obv_slope"] > 0:
        score += 5
        reasons.append("OBV يتحسن")
    if r["mfi"] >= 50:
        score += 5
        reasons.append("MFI إيجابي")

    support = min(float(r["support20"]), float(r["support60"]))
    resistance = max(float(r["resistance20"]), float(r["resistance60"]))
    atr = float(r["atr"])

    # 7) Structure / entry type — 20
    breakout = p > float(r["resistance20"]) * 0.997 and r["volume_ratio"] >= 1.2
    pullback = p >= r["ema20"] * 0.985 and p <= r["ema20"] * 1.03 and r["ema20"] > r["ema50"]
    reversal = (
        r["rsi"] < 45 and
        r["macd"] > r["macd_signal"] and
        r["obv_slope"] > 0
    )
    continuation = (
        r["ema20"] > r["ema50"] > r["ema200"] and
        p > r["ema20"]
    )

    if breakout:
        score += 20
        signal = "BREAKOUT BUY"
        reasons.append("اختراق مقاومة مع تأكيد حجم")
    elif pullback:
        score += 18
        signal = "PULLBACK BUY"
        reasons.append("Pullback على اتجاه صاعد")
    elif reversal:
        score += 14
        signal = "REVERSAL WATCH"
        reasons.append("إشارات انعكاس مبكرة")
    elif continuation:
        score += 15
        signal = "TREND BUY"
        reasons.append("استمرار اتجاه صاعد")
    else:
        signal = "WATCH"

    # Entry logic
    if breakout:
        entry_low = max(support, float(r["resistance20"]) - 0.35 * atr)
        entry_high = p + 0.10 * atr
    elif pullback:
        entry_low = max(support, float(r["ema20"]) - 0.35 * atr)
        entry_high = float(r["ema20"]) + 0.25 * atr
    else:
        entry_low = p - 0.20 * atr
        entry_high = p + 0.20 * atr

    # SL: structure + ATR
    sl_structure = support - 0.20 * atr
    sl_atr = entry_low - 1.50 * atr
    stop_loss = min(sl_structure, sl_atr)

    if stop_loss <= 0 or entry_low <= stop_loss:
        return None

    risk = entry_high - stop_loss

    # Targets based on risk and structure
    tp1 = max(entry_high + 1.5 * risk, resistance)
    tp2 = entry_high + 2.5 * risk
    tp3 = entry_high + 4.0 * risk

    rr_tp1 = (tp1 - entry_high) / risk if risk > 0 else 0

    if rr_tp1 < min_rr:
        return None

    # Final gate: only actionable signals
    if score < 60:
        return None

    return {
        "symbol": symbol,
        "name": name,
        "signal": signal,
        "score": int(min(score, 100)),
        "entry_low": _round(entry_low),
        "entry_high": _round(entry_high),
        "stop_loss": _round(stop_loss),
        "tp1": _round(tp1),
        "tp2": _round(tp2),
        "tp3": _round(tp3),
        "atr": _round(atr),
        "atr_pct": _round(r["atr_pct"]),
        "rr_tp1": _round(rr_tp1),
        "rsi": _round(r["rsi"]),
        "adx": _round(r["adx"]),
        "mfi": _round(r["mfi"]),
        "volume_ratio": _round(r["volume_ratio"]),
        "support": _round(support),
        "resistance": _round(resistance),
        "reason": " + ".join(reasons),
        "avg_value_20": _round(avg_value),
        "price": _round(p),
    }
