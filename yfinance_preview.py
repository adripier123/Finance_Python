import yfinance as yf
import pandas as pd
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


# --- Main ---
print("\nFetching ticker lists...")
tickers = fetch_ticker_lists()

print(f"Scanning {len(tickers)} tickers for stocks down >30% from their 1-year high...")
print(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")

results = fetch_live_data(tickers)
source = "Yahoo Finance (live)"

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

# Display preview
width = 155
print(f"{'=' * width}")
print(f"{'Stocks Down >30% from 52-Week High (Buy/Strong Buy Only) — Preview':^{width}}")
print(f"{'Source: ' + source:^{width}}")
print(f"{'=' * width}")
print(df.head(25).to_string())
print(f"{'=' * width}")
print(f"\nTotal stocks found: {len(df)}")
if len(df) > 0:
    print(f"Biggest drop: {df.iloc[0]['Ticker']} at {df.iloc[0]['Drop from High (%)']}%")
    print(f"Average drop: {df['Drop from High (%)'].mean():.2f}%")
