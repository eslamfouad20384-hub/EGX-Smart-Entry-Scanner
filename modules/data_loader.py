from pathlib import Path
import io
import requests
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "data" / "egx_symbols.csv"

# Dataset containing Egyptian listed-company symbols/metadata.
# Local CSV remains the fallback if the remote file is unavailable.
REMOTE_URLS = [
    "https://huggingface.co/datasets/kjhq/Egypt-Stock-Symbols-and-Metadata/resolve/main/egypt.csv",
]

def _normalize_symbol(s):
    s = str(s).strip().upper()
    for suffix in [".CA", ".EG", ":CA"]:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    return s

def load_symbols():
    frames = []
    for url in REMOTE_URLS:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
            if "ticker" in df.columns:
                df["symbol"] = df["ticker"].map(_normalize_symbol)
            elif "symbol" in df.columns:
                df["symbol"] = df["symbol"].map(_normalize_symbol)
            else:
                continue
            if "name" not in df.columns:
                df["name"] = df["symbol"]
            frames.append(df[["symbol", "name"]])
            break
        except Exception:
            pass

    if frames:
        df = frames[0]
    else:
        df = pd.read_csv(LOCAL)
        df["symbol"] = df["symbol"].map(_normalize_symbol)

    df = df.dropna(subset=["symbol"]).drop_duplicates("symbol")
    return df.reset_index(drop=True)

def download_stock(symbol, period="2y", interval="1d"):
    ticker = f"{symbol}.CA"
    df = yf.download(
        ticker, period=period, interval=interval,
        auto_adjust=False, progress=False, threads=False
    )
    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    needed = ["Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in needed if c in df.columns]].copy()
    df = df.dropna()
    return df
