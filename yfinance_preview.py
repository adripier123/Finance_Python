import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Suppress noisy yfinance/connection warnings
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def fetch_ticker_lists():
    """Fetch all available equity tickers from Yahoo Finance using the yfinance screener."""
    tickers = set()

    queries = [
        yf.EquityQuery('eq', ['region', 'us']),
        yf.EquityQuery('eq', ['region', 'ca']),
    ]

    for query in queries:
        offset = 0
        size = 250  # Yahoo hard limit per request
        while True:
            response = yf.screen(query, offset=offset, size=size)
            quotes = response.get("quotes", [])
            if not quotes:
                break
            tickers.update(q["symbol"] for q in quotes if "symbol" in q)
            total = response.get("total", 0)
            offset += size
            if offset >= total:
                break

    return sorted(tickers)


def fetch_live_data(tickers):
    """Batch-download 1-year history, then fetch details only for stocks down >30%."""
    print(f"  Downloading price history for {len(tickers)} tickers...")
    data = yf.download(tickers, period="1y", progress=False, threads=True)

    if data.empty:
        return []

    multi = isinstance(data.columns, pd.MultiIndex)

    # Pass 1: find stocks down >30% from 52-week high
    candidates = []
    for symbol in tickers:
        try:
            if multi:
                high = data[("High", symbol)].dropna()
                close = data[("Close", symbol)].dropna()
            else:
                high = data["High"].dropna()
                close = data["Close"].dropna()

            if len(close) < 2:
                continue

            year_high = float(high.max())
            current_price = float(close.iloc[-1])
            pct_drop = ((current_price - year_high) / year_high) * 100

            if pct_drop <= -30:
                candidates.append((symbol, current_price, year_high, pct_drop))
        except Exception:
            continue

    # Pass 2: fetch detailed info only for candidates
    print(f"  Found {len(candidates)} stocks down >30%, fetching details...")
    results = []
    for symbol, current_price, year_high, pct_drop in candidates:
        try:
            info = yf.Ticker(symbol).info
            target = info.get("targetMeanPrice", None)
            upside = (
                round(((target - current_price) / current_price) * 100, 2)
                if target and current_price > 0 else None
            )
            results.append({
                "Sector": info.get("sector", "Other"),
                "Ticker": symbol,
                "Current Price": round(current_price, 2),
                "52-Week High": round(year_high, 2),
                "Drop from High (%)": round(pct_drop, 2),
                "P/E": info.get("trailingPE", None),
                "Forward P/E": info.get("forwardPE", None),
                "1Y Target": target,
                "Potential Upside (%)": upside,
                "Buy Rating": info.get("recommendationKey", None),
            })
        except Exception:
            continue

    return results


def generate_sample_data():
    """Generate realistic sample data for stocks that dropped >30% from their 1-year high."""
    np.random.seed(2026)
    # (Ticker, Sector, Price, 52wk High, Drop%, P/E, Fwd P/E, 1Y Target, Rating)
    sample = [
        ("INTC",    "Technology",      21.49,  38.84, -44.67,   None,  22.10,  25.50, "hold"),
        ("MRNA",    "Healthcare",      33.85,  56.81, -40.41,   None,   None,  68.00, "hold"),
        ("SMCI",    "Technology",      28.64,  69.46, -58.77,   8.42,   6.15,  45.00, "buy"),
        ("SNAP",    "Technology",       8.12,  17.30, -53.06,   None,  52.80,  13.25, "hold"),
        ("PYPL",    "Technology",      62.10,  93.68, -33.72,  16.88,  12.95,  85.00, "buy"),
        ("LCID",    "Industrials",      2.04,   4.43, -53.95,   None,   None,   3.50, "hold"),
        ("RIVN",    "Industrials",     11.78,  18.85, -37.51,   None,   None,  16.00, "buy"),
        ("FSR",     "Industrials",      0.42,   1.54, -72.73,   None,   None,   None, "sell"),
        ("COIN",    "Technology",     175.28, 349.75, -49.90,  31.22,  19.84, 275.00, "buy"),
        ("PFE",     "Healthcare",      24.93,  37.19, -32.97,  36.50,  10.12,  32.00, "hold"),
        ("BMY",     "Healthcare",      41.37,  62.95, -34.28,   8.15,   7.50,  53.00, "hold"),
        ("NKE",     "Consumer Cyclical", 68.24, 109.44, -37.65, 22.74, 20.30, 90.00, "buy"),
        ("LULU",    "Consumer Cyclical", 278.40, 416.12, -33.09, 22.18, 19.52, 375.00, "buy"),
        ("BNTX",    "Healthcare",      87.53, 132.16, -33.77,   5.62,  18.40, 125.00, "buy"),
        ("ZM",      "Technology",      62.15,  93.47, -33.51,  23.15,  13.80,  78.00, "hold"),
        ("DOCU",    "Technology",      54.30,  98.76, -45.03,  12.40,  14.60,  72.00, "hold"),
        ("BA",      "Industrials",    155.72, 231.08, -32.62,   None,  32.50, 200.00, "buy"),
        ("MMM",     "Industrials",     92.66, 143.80, -35.56,  11.33,  10.15, 120.00, "hold"),
        ("MARA",    "Technology",      14.22,  34.09, -58.29,   6.80,   8.45,  24.00, "buy"),
        ("RIOT",    "Technology",       8.05,  18.93, -57.48,   None,  12.30,  14.50, "buy"),
        ("PINS",    "Technology",      25.14,  40.68, -38.20,  28.50,  17.90,  38.00, "buy"),
        ("ROKU",    "Technology",      51.38,  84.12, -38.90,   None,  62.40,  75.00, "buy"),
        ("LYFT",    "Technology",       9.96,  18.68, -46.68,  18.20,  11.75,  16.00, "buy"),
        ("BIIB",    "Healthcare",     148.30, 235.75, -37.10,  13.42,  11.85, 210.00, "hold"),
        ("DIS",     "Consumer Cyclical", 85.41, 123.74, -30.97, 34.60, 16.90, 115.00, "buy"),
        # Canadian stocks (TSX)
        ("BB.TO",   "Technology",       2.85,   5.72, -50.17,   None,   None,   4.00, "hold"),
        ("LSPD.TO", "Technology",      16.42,  26.18, -37.28,   None,  45.30,  22.00, "buy"),
        ("AC.TO",   "Industrials",     14.58,  23.90, -38.99,   4.20,   3.85,  21.00, "buy"),
        ("BNS.TO",  "Financial Services", 62.35, 95.10, -34.44, 9.80,  9.15,  78.00, "hold"),
        ("SU.TO",   "Energy",          38.72,  58.46, -33.78,   7.60,   8.20,  52.00, "buy"),
    ]
    return [
        {
            "Sector": s[1],
            "Ticker": s[0],
            "Current Price": s[2],
            "52-Week High": s[3],
            "Drop from High (%)": s[4],
            "P/E": s[5],
            "Forward P/E": s[6],
            "1Y Target": s[7],
            "Potential Upside (%)": (
                round(((s[7] - s[2]) / s[2]) * 100, 2) if s[7] else None
            ),
            "Buy Rating": s[8],
        }
        for s in sample
    ]


# --- Main ---
print("\nFetching ticker lists...")
tickers = fetch_ticker_lists()

print(f"Scanning {len(tickers)} tickers for stocks down >30% from their 1-year high...")
print(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")

try:
    results = fetch_live_data(tickers)
    if not results:
        raise ValueError("No live results returned")
    source = "Yahoo Finance (live)"
except Exception:
    results = generate_sample_data()
    source = "Sample data (network unavailable)"

df = pd.DataFrame(results)
df = df.sort_values("Drop from High (%)", ascending=True).reset_index(drop=True)
df.index = df.index + 1  # 1-based row numbers

# Ensure column order with Sector first and Potential Upside before Buy Rating
col_order = ["Sector", "Ticker", "Current Price", "52-Week High", "Drop from High (%)",
             "P/E", "Forward P/E", "1Y Target", "Potential Upside (%)", "Buy Rating"]
df = df[col_order]

# Round numeric columns for clean display
for col in ["P/E", "Forward P/E", "1Y Target", "Potential Upside (%)"]:
    df[col] = df[col].apply(lambda x: round(x, 2) if pd.notna(x) else "N/A")

# Capitalize Buy Rating for display
df["Buy Rating"] = df["Buy Rating"].apply(lambda x: x.replace("_", " ").title() if isinstance(x, str) else "N/A")

# Filter for Buy and Strong Buy ratings only
df = df[df["Buy Rating"].isin(["Buy", "Strong Buy"])].reset_index(drop=True)
df.index = df.index + 1  # 1-based row numbers

# ANSI color codes
RED = "\033[91m"
RESET = "\033[0m"

# Use red text when displaying sample (non-live) data
is_sample = "Sample" in source
c = RED if is_sample else ""
r = RESET if is_sample else ""

# Display preview
width = 155
print(f"{c}{'=' * width}")
print(f"{'Stocks Down >30% from 52-Week High (Buy/Strong Buy Only) — Preview':^{width}}")
print(f"{'Source: ' + source:^{width}}")
if is_sample:
    print(f"{'⚠  DATA SHOWN IN RED IS NOT LIVE — SAMPLE DATA ONLY  ⚠':^{width}}")
print(f"{'=' * width}")
print(df.head(25).to_string())
print(f"{'=' * width}")
print(f"\nTotal stocks found: {len(df)}")
if len(df) > 0:
    print(f"Biggest drop: {df.iloc[0]['Ticker']} at {df.iloc[0]['Drop from High (%)']}%")
    print(f"Average drop: {df['Drop from High (%)'].mean():.2f}%")
print(r, end="")
