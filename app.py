import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.data_loader import load_symbols, download_stock
from modules.indicators import add_indicators
from modules.signals import analyze_stock

st.set_page_config(page_title="EGX Smart Entry Scanner", page_icon="📈", layout="wide")

st.title("📈 EGX Smart Entry Scanner PRO")
st.caption("فحص الأسهم المصرية واستخراج أقوى فرص الدخول مع Entry / SL / TP1 / TP2 / TP3 / ATR")

with st.sidebar:
    st.header("⚙️ إعدادات الفحص")
    period = st.selectbox("الفترة التاريخية", ["1y", "2y", "5y"], index=1)
    interval = st.selectbox("الفريم", ["1d", "1wk"], index=0)
    min_score = st.slider("أقل Score", 50, 95, 70)
    min_rr = st.slider("أقل Risk/Reward للهدف الأول", 1.0, 4.0, 1.5, 0.1)
    min_avg_value = st.number_input("أقل متوسط قيمة تداول يومية (جنيه)", 0, 100_000_000, 500_000, 100_000)
    workers = st.slider("عدد العمليات المتوازية", 2, 12, 6)
    top_n = st.slider("عدد النتائج", 5, 50, 20)
    run = st.button("🚀 ابدأ فحص السوق", use_container_width=True)

st.info(
    "المحرك يستخدم Trend + RSI + MACD + ADX + ATR + OBV + MFI + Volume + Support/Resistance "
    "ويحسب مستويات الدخول والستوب والأهداف بشكل آلي."
)

@st.cache_data(ttl=60*60*6, show_spinner=False)
def get_symbols():
    return load_symbols()

symbols = get_symbols()
st.write(f"عدد الرموز المتاحة للفحص: **{len(symbols)}**")

if run:
    progress = st.progress(0)
    status = st.empty()
    results = []

    def one(row):
        symbol = row["symbol"]
        name = row.get("name", symbol)
        try:
            df = download_stock(symbol, period=period, interval=interval)
            if df is None or len(df) < 120:
                return None
            df = add_indicators(df)
            return analyze_stock(
                df, symbol=symbol, name=name,
                min_avg_value=min_avg_value, min_rr=min_rr
            )
        except Exception as e:
            return {"symbol": symbol, "name": name, "error": str(e)}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(one, row) for _, row in symbols.iterrows()]
        total = len(futures)
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            if r and "error" not in r:
                results.append(r)
            progress.progress(i / total)
            status.write(f"تم فحص {i}/{total}")

    progress.empty()
    status.empty()

    if not results:
        st.error("لم يتم الحصول على بيانات كافية. جرّب إعادة الفحص أو راجع مصدر البيانات.")
        st.stop()

    out = pd.DataFrame(results)
    out = out[out["score"] >= min_score].copy()
    if out.empty:
        st.warning("مفيش إشارات فوق الـScore المحدد حاليًا.")
        st.stop()

    out = out.sort_values(["score", "rr_tp1"], ascending=[False, False]).head(top_n)

    st.success(f"تم العثور على {len(out)} فرصة مطابقة للفلاتر.")

    cols = [
        "rank", "symbol", "name", "signal", "score", "entry_low", "entry_high",
        "stop_loss", "tp1", "tp2", "tp3", "atr", "atr_pct", "rr_tp1",
        "rsi", "adx", "volume_ratio", "support", "resistance", "reason"
    ]
    out["rank"] = range(1, len(out) + 1)
    for c in cols:
        if c not in out:
            out[c] = None

    st.subheader("🏆 أفضل فرص الدخول")
    display = out[cols].copy()
    display.columns = [
        "Rank", "السهم", "الشركة", "الإشارة", "Score", "دخول من",
        "دخول إلى", "Stop Loss", "TP1", "TP2", "TP3", "ATR",
        "ATR %", "R/R TP1", "RSI", "ADX", "Volume x",
        "الدعم", "المقاومة", "الأسباب"
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("📌 تفاصيل أفضل 10")
    for _, r in out.head(10).iterrows():
        with st.expander(f"#{int(r['rank'])} — {r['symbol']} — {r['signal']} — Score {r['score']}/100"):
            a, b, c, d = st.columns(4)
            a.metric("Entry", f"{r['entry_low']:.2f} – {r['entry_high']:.2f}")
            b.metric("Stop Loss", f"{r['stop_loss']:.2f}")
            c.metric("ATR", f"{r['atr']:.2f} ({r['atr_pct']:.2f}%)")
            d.metric("R/R TP1", f"{r['rr_tp1']:.2f}")
            st.write(
                f"**TP1:** {r['tp1']:.2f}  |  **TP2:** {r['tp2']:.2f}  |  **TP3:** {r['tp3']:.2f}"
            )
            st.write(
                f"RSI **{r['rsi']:.1f}** · ADX **{r['adx']:.1f}** · "
                f"Volume **{r['volume_ratio']:.2f}x** · Support **{r['support']:.2f}** · "
                f"Resistance **{r['resistance']:.2f}**"
            )
            st.write("**نوع الإشارة:**", r["signal"])
            st.write("**الأسباب:**", r["reason"])

    csv_data = out.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ تحميل النتائج CSV",
        csv_data,
        file_name="egx_scanner_results.csv",
        mime="text/csv"
    )
