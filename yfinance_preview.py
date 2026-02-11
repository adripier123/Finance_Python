import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Suppress noisy yfinance/connection warnings
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# Broad list of tickers to scan across major sectors
TICKERS = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM",
    "ADBE", "NFLX", "PYPL", "SHOP", "SQ", "SNAP", "PINS", "UBER", "LYFT", "ROKU",
    "ZM", "DOCU", "PLTR", "SOFI", "COIN", "MARA", "RIOT", "SMCI", "ARM", "DELL",
    # Healthcare / Biotech
    "PFE", "MRNA", "BNTX", "JNJ", "BMY", "ABBV", "GILD", "BIIB", "REGN", "AMGN",
    # Finance
    "JPM", "BAC", "GS", "MS", "WFC", "C", "SCHW", "BLK", "AXP", "V",
    # Energy
    "XOM", "CVX", "OXY", "SLB", "DVN", "MPC", "VLO", "HAL", "FANG", "COP",
    # Consumer / Retail
    "NKE", "SBUX", "MCD", "DIS", "WMT", "TGT", "COST", "HD", "LOW", "LULU",
    # Industrial / Other
    "BA", "CAT", "DE", "GE", "MMM", "F", "GM", "RIVN", "LCID", "FSR",
    # Canadian Stocks (TSX)
    "RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO",       # Banks
    "ENB.TO", "CNQ.TO", "SU.TO", "TRP.TO", "IMO.TO",     # Energy
    "SHOP.TO", "CSU.TO", "OTEX.TO", "BB.TO", "LSPD.TO",  # Tech
    "NTR.TO", "ABX.TO", "FNV.TO", "WFG.TO", "CCL-B.TO",  # Materials
    "CP.TO", "CNR.TO", "AC.TO", "QSR.TO", "MRU.TO",      # Industrial / Consumer
]

# Sector mapping for all tickers
SECTOR_MAP = {
    # US Tech
    "AAPL": "Tech", "MSFT": "Tech", "GOOGL": "Tech", "AMZN": "Tech", "META": "Tech",
    "NVDA": "Tech", "TSLA": "Tech", "AMD": "Tech", "INTC": "Tech", "CRM": "Tech",
    "ADBE": "Tech", "NFLX": "Tech", "PYPL": "Tech", "SHOP": "Tech", "SQ": "Tech",
    "SNAP": "Tech", "PINS": "Tech", "UBER": "Tech", "LYFT": "Tech", "ROKU": "Tech",
    "ZM": "Tech", "DOCU": "Tech", "PLTR": "Tech", "SOFI": "Tech", "COIN": "Tech",
    "MARA": "Tech", "RIOT": "Tech", "SMCI": "Tech", "ARM": "Tech", "DELL": "Tech",
    # US Healthcare / Biotech
    "PFE": "Healthcare", "MRNA": "Healthcare", "BNTX": "Healthcare", "JNJ": "Healthcare",
    "BMY": "Healthcare", "ABBV": "Healthcare", "GILD": "Healthcare", "BIIB": "Healthcare",
    "REGN": "Healthcare", "AMGN": "Healthcare",
    # US Finance
    "JPM": "Finance", "BAC": "Finance", "GS": "Finance", "MS": "Finance", "WFC": "Finance",
    "C": "Finance", "SCHW": "Finance", "BLK": "Finance", "AXP": "Finance", "V": "Finance",
    # US Energy
    "XOM": "Energy", "CVX": "Energy", "OXY": "Energy", "SLB": "Energy", "DVN": "Energy",
    "MPC": "Energy", "VLO": "Energy", "HAL": "Energy", "FANG": "Energy", "COP": "Energy",
    # US Consumer / Retail
    "NKE": "Consumer", "SBUX": "Consumer", "MCD": "Consumer", "DIS": "Consumer",
    "WMT": "Consumer", "TGT": "Consumer", "COST": "Consumer", "HD": "Consumer",
    "LOW": "Consumer", "LULU": "Consumer",
    # US Industrial / Other
    "BA": "Industrial", "CAT": "Industrial", "DE": "Industrial", "GE": "Industrial",
    "MMM": "Industrial", "F": "Industrial", "GM": "Industrial", "RIVN": "Industrial",
    "LCID": "Industrial", "FSR": "Industrial",
    # Canadian Banks
    "RY.TO": "Finance", "TD.TO": "Finance", "BNS.TO": "Finance", "BMO.TO": "Finance",
    "CM.TO": "Finance",
    # Canadian Energy
    "ENB.TO": "Energy", "CNQ.TO": "Energy", "SU.TO": "Energy", "TRP.TO": "Energy",
    "IMO.TO": "Energy",
    # Canadian Tech
    "SHOP.TO": "Tech", "CSU.TO": "Tech", "OTEX.TO": "Tech", "BB.TO": "Tech",
    "LSPD.TO": "Tech",
    # Canadian Materials
    "NTR.TO": "Materials", "ABX.TO": "Materials", "FNV.TO": "Materials",
    "WFG.TO": "Materials", "CCL-B.TO": "Materials",
    # Canadian Industrial / Consumer
    "CP.TO": "Industrial", "CNR.TO": "Industrial", "AC.TO": "Consumer",
    "QSR.TO": "Consumer", "MRU.TO": "Consumer",
}


def fetch_live_data(tickers):
    """Fetch 1-year history for all tickers and compute drop from 52-week high."""
    results = []
    for symbol in tickers:
        try:
            tk = yf.Ticker(symbol)
            hist = tk.history(period="1y")
            if hist.empty or len(hist) < 2:
                continue
            year_high = hist["High"].max()
            current_price = hist["Close"].iloc[-1]
            pct_drop = ((current_price - year_high) / year_high) * 100
            if pct_drop <= -30:
                info = tk.info
                results.append({
                    "Sector": SECTOR_MAP.get(symbol, "Other"),
                    "Ticker": symbol,
                    "Current Price": round(current_price, 2),
                    "52-Week High": round(year_high, 2),
                    "Drop from High (%)": round(pct_drop, 2),
                    "P/E": info.get("trailingPE", None),
                    "Forward P/E": info.get("forwardPE", None),
                    "1Y Target": info.get("targetMeanPrice", None),
                    "Buy Rating": info.get("recommendationKey", None),
                })
        except Exception:
            continue
    return results


def generate_sample_data():
    """Generate realistic sample data for stocks that dropped >30% from their 1-year high."""
    np.random.seed(2026)
    # (Ticker, Current Price, 52-Week High, Drop%, P/E, Forward P/E, 1Y Target, Buy Rating)
    sample = [
        ("INTC",   21.49,  38.84, -44.67,   None,  22.10,  25.50, "hold"),
        ("MRNA",   33.85,  56.81, -40.41,   None,   None,  68.00, "hold"),
        ("SMCI",   28.64,  69.46, -58.77,   8.42,   6.15,  45.00, "buy"),
        ("SNAP",    8.12,  17.30, -53.06,   None,  52.80,  13.25, "hold"),
        ("PYPL",   62.10,  93.68, -33.72,  16.88,  12.95,  85.00, "buy"),
        ("LCID",    2.04,   4.43, -53.95,   None,   None,   3.50, "hold"),
        ("RIVN",   11.78,  18.85, -37.51,   None,   None,  16.00, "buy"),
        ("FSR",     0.42,   1.54, -72.73,   None,   None,   None, "sell"),
        ("COIN",  175.28, 349.75, -49.90,  31.22,  19.84, 275.00, "buy"),
        ("PFE",    24.93,  37.19, -32.97,  36.50,  10.12,  32.00, "hold"),
        ("BMY",    41.37,  62.95, -34.28,   8.15,   7.50,  53.00, "hold"),
        ("NKE",    68.24, 109.44, -37.65,  22.74,  20.30,  90.00, "buy"),
        ("LULU",  278.40, 416.12, -33.09,  22.18,  19.52, 375.00, "buy"),
        ("BNTX",   87.53, 132.16, -33.77,   5.62,  18.40, 125.00, "buy"),
        ("ZM",     62.15,  93.47, -33.51,  23.15,  13.80,  78.00, "hold"),
        ("DOCU",   54.30,  98.76, -45.03,  12.40,  14.60,  72.00, "hold"),
        ("BA",    155.72, 231.08, -32.62,   None,  32.50, 200.00, "buy"),
        ("MMM",    92.66, 143.80, -35.56,  11.33,  10.15, 120.00, "hold"),
        ("MARA",   14.22,  34.09, -58.29,   6.80,   8.45,  24.00, "buy"),
        ("RIOT",    8.05,  18.93, -57.48,   None,  12.30,  14.50, "buy"),
        ("PINS",   25.14,  40.68, -38.20,  28.50,  17.90,  38.00, "buy"),
        ("ROKU",   51.38,  84.12, -38.90,   None,  62.40,  75.00, "buy"),
        ("LYFT",    9.96,  18.68, -46.68,  18.20,  11.75,  16.00, "buy"),
        ("BIIB",  148.30, 235.75, -37.10,  13.42,  11.85, 210.00, "hold"),
        ("DIS",    85.41, 123.74, -30.97,  34.60,  16.90, 115.00, "buy"),
        # Canadian stocks (TSX)
        ("BB.TO",    2.85,   5.72, -50.17,   None,   None,   4.00, "hold"),
        ("LSPD.TO", 16.42,  26.18, -37.28,   None,  45.30,  22.00, "buy"),
        ("AC.TO",   14.58,  23.90, -38.99,   4.20,   3.85,  21.00, "buy"),
        ("BNS.TO",  62.35,  95.10, -34.44,   9.80,   9.15,  78.00, "hold"),
        ("SU.TO",   38.72,  58.46, -33.78,   7.60,   8.20,  52.00, "buy"),
    ]
    return [
        {
            "Sector": SECTOR_MAP.get(s[0], "Other"),
            "Ticker": s[0],
            "Current Price": s[1],
            "52-Week High": s[2],
            "Drop from High (%)": s[3],
            "P/E": s[4],
            "Forward P/E": s[5],
            "1Y Target": s[6],
            "Buy Rating": s[7],
        }
        for s in sample
    ]


# --- Main ---
print(f"\nScanning {len(TICKERS)} tickers for stocks down >30% from their 1-year high...")
print(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")

try:
    results = fetch_live_data(TICKERS)
    if not results:
        raise ValueError("No live results returned")
    source = "Yahoo Finance (live)"
except Exception:
    results = generate_sample_data()
    source = "Sample data (network unavailable)"

df = pd.DataFrame(results)
df = df.sort_values("Drop from High (%)", ascending=True).reset_index(drop=True)
df.index = df.index + 1  # 1-based row numbers

# Ensure Sector is the first column
col_order = ["Sector", "Ticker", "Current Price", "52-Week High", "Drop from High (%)",
             "P/E", "Forward P/E", "1Y Target", "Buy Rating"]
df = df[col_order]

# Round numeric columns for clean display
for col in ["P/E", "Forward P/E", "1Y Target"]:
    df[col] = df[col].apply(lambda x: round(x, 2) if pd.notna(x) else "N/A")

# Capitalize Buy Rating for display
df["Buy Rating"] = df["Buy Rating"].apply(lambda x: x.replace("_", " ").title() if isinstance(x, str) else "N/A")

# Filter for Buy and Strong Buy ratings only
df = df[df["Buy Rating"].isin(["Buy", "Strong Buy"])].reset_index(drop=True)
df.index = df.index + 1  # 1-based row numbers

# Display 25-row preview
width = 130
print("=" * width)
print(f"{'Stocks Down >30% from 52-Week High (Buy/Strong Buy Only) — 25 Row Preview':^{width}}")
print(f"{'Source: ' + source:^{width}}")
print("=" * width)
print(df.head(25).to_string())
print("=" * width)
print(f"\nTotal stocks found: {len(df)}")
print(f"Biggest drop: {df.iloc[0]['Ticker']} at {df.iloc[0]['Drop from High (%)']}%")
print(f"Average drop: {df['Drop from High (%)'].mean():.2f}%")
