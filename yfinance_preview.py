import yfinance as yf
import pandas as pd
import logging
from datetime import datetime

# Suppress noisy yfinance/connection warnings
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# Curated list of ~540 US and Canadian stocks by market cap
TICKERS = [
    # ── US Technology (80) ──────────────────────────────────────────────
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM",
    "ADBE", "NFLX", "PYPL", "SHOP", "SQ", "SNAP", "PINS", "UBER", "LYFT", "ROKU",
    "ZM", "DOCU", "PLTR", "SOFI", "COIN", "MARA", "RIOT", "SMCI", "ARM", "DELL",
    "AVGO", "ORCL", "CSCO", "ACN", "IBM", "TXN", "QCOM", "AMAT", "NOW", "INTU",
    "MU", "LRCX", "ADI", "KLAC", "SNPS", "CDNS", "MRVL", "MSI", "TEL", "FTNT",
    "PANW", "HPQ", "HPE", "KEYS", "EPAM", "ON", "NXPI", "MPWR", "CRWD", "GDDY",
    "CTSH", "IT", "ANSS", "PTC", "CDW", "WDC", "STX", "SWKS", "QRVO", "ROP",
    "GLW", "VRSN", "NTAP", "LDOS", "ZBRA", "TRMB", "BR", "SSNC", "AKAM", "FFIV",
    # ── US Healthcare / Biotech (52) ────────────────────────────────────
    "PFE", "MRNA", "BNTX", "JNJ", "BMY", "ABBV", "GILD", "BIIB", "REGN", "AMGN",
    "UNH", "LLY", "MRK", "ABT", "TMO", "DHR", "ISRG", "ELV", "SYK", "BSX",
    "VRTX", "MDT", "ZTS", "CI", "BDX", "HCA", "A", "MCK", "EW", "IQV",
    "DXCM", "IDXX", "ALGN", "BAX", "RMD", "HOLX", "PODD", "VEEV", "WST", "ZBH",
    "GEHC", "MOH", "CNC", "HUM", "CAH", "VTRS", "INCY", "EXAS", "MTD", "CRL",
    "STE", "OGN",
    # ── US Finance (52) ─────────────────────────────────────────────────
    "JPM", "BAC", "GS", "MS", "WFC", "C", "SCHW", "BLK", "AXP", "V",
    "BRK-B", "SPGI", "MMC", "CB", "PGR", "AON", "ICE", "CME", "AFL", "AIG",
    "TRV", "MET", "PRU", "ALL", "FI", "AJG", "WTW", "HIG", "FITB", "MTB",
    "RF", "CFG", "HBAN", "KEY", "NTRS", "STT", "DFS", "COF", "SYF", "ALLY",
    "BRO", "RJF", "TROW", "NDAQ", "CBOE", "MSCI", "MCO", "CINF", "L", "FDS",
    "MKTX", "GL",
    # ── US Consumer Discretionary (48) ──────────────────────────────────
    "NKE", "SBUX", "MCD", "DIS", "WMT", "TGT", "COST", "HD", "LOW", "LULU",
    "BKNG", "TJX", "MAR", "ORLY", "AZO", "RCL", "CMG", "DHI", "LEN", "ROST",
    "GRMN", "YUM", "EBAY", "APTV", "BBY", "PHM", "NVR", "ETSY", "CPRT", "ULTA",
    "GPC", "MGM", "WYNN", "HLT", "LVS", "CCL", "DRI", "HAS", "DECK", "CZR",
    "NCLH", "ABNB", "DKNG", "POOL", "TPR", "KMX", "RL", "BWA",
    # ── US Industrial (49) ──────────────────────────────────────────────
    "BA", "CAT", "DE", "GE", "MMM", "F", "GM", "RIVN", "LCID", "FSR",
    "HON", "UNP", "RTX", "UPS", "LMT", "ETN", "ADP", "ITW", "NOC", "GD",
    "WM", "RSG", "CSX", "NSC", "FDX", "EMR", "JCI", "TT", "PH", "PCAR",
    "CMI", "ROK", "FAST", "ODFL", "AME", "VRSK", "IR", "WAB", "CARR", "GWW",
    "DOV", "TDG", "AXON", "PWR", "LHX", "HUBB", "CTAS", "GNRC", "MAS",
    # ── US Consumer Staples (25) ────────────────────────────────────────
    "PG", "KO", "PEP", "PM", "MO", "MDLZ", "CL", "EL", "KMB", "SYY",
    "STZ", "KDP", "GIS", "KHC", "HSY", "K", "MKC", "CHD", "CLX", "CAG",
    "TSN", "BG", "ADM", "MNST", "KVUE",
    # ── US Energy (21) ──────────────────────────────────────────────────
    "XOM", "CVX", "OXY", "SLB", "DVN", "MPC", "VLO", "HAL", "FANG", "COP",
    "EOG", "WMB", "PSX", "KMI", "TRGP", "BKR", "CTRA", "EQT", "MRO", "APA",
    "HES",
    # ── US Utilities (19) ───────────────────────────────────────────────
    "NEE", "SO", "DUK", "D", "SRE", "AEP", "EXC", "XEL", "ED", "WEC",
    "ES", "PEG", "AWK", "CMS", "DTE", "FE", "NRG", "CEG", "VST",
    # ── US Real Estate (20) ─────────────────────────────────────────────
    "PLD", "AMT", "EQIX", "CCI", "SPG", "PSA", "O", "DLR", "WELL", "VICI",
    "EXR", "AVB", "EQR", "VTR", "ARE", "MAA", "REG", "KIM", "INVH", "IRM",
    # ── US Materials (19) ───────────────────────────────────────────────
    "LIN", "SHW", "APD", "ECL", "FCX", "NEM", "NUE", "DOW", "DD", "VMC",
    "MLM", "PPG", "CF", "MOS", "ALB", "BALL", "IFF", "FMC", "CTVA",
    # ── US Communication Services (17) ──────────────────────────────────
    "GOOG", "CMCSA", "T", "VZ", "TMUS", "CHTR", "WBD", "FOX", "OMC", "LYV",
    "MTCH", "EA", "TTWO", "RBLX", "FOXA", "IPG", "PARA",
    # ── Canadian Financials (20) ────────────────────────────────────────
    "RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO",
    "BN.TO", "BAM.TO", "MFC.TO", "NA.TO", "SLF.TO",
    "IFC.TO", "GWO.TO", "POW.TO", "FFH.TO", "X.TO",
    "EFN.TO", "IAG.TO", "FSV.TO", "ONEX.TO", "EQB.TO",
    # ── Canadian Energy (15) ────────────────────────────────────────────
    "ENB.TO", "CNQ.TO", "SU.TO", "TRP.TO", "IMO.TO",
    "CVE.TO", "TOU.TO", "PPL.TO", "ARX.TO", "CCO.TO",
    "MEG.TO", "VRN.TO", "PEY.TO", "KEL.TO", "WCP.TO",
    # ── Canadian Materials / Mining (17) ────────────────────────────────
    "NTR.TO", "ABX.TO", "FNV.TO",
    "AEM.TO", "WPM.TO", "K.TO", "TECK-B.TO", "LUN.TO", "PAAS.TO", "BTO.TO",
    "ELD.TO", "FM.TO", "AGI.TO", "OR.TO", "IVN.TO",
    "WFG.TO", "CCL-B.TO",
    # ── Canadian Industrials (15) ───────────────────────────────────────
    "CP.TO", "CNR.TO", "AC.TO", "QSR.TO", "MRU.TO",
    "TRI.TO", "WCN.TO", "TFII.TO", "BBD-B.TO", "RBA.TO",
    "WSP.TO", "CAE.TO", "TIH.TO", "FTT.TO", "ATRL.TO",
    # ── Canadian Technology (7) ─────────────────────────────────────────
    "SHOP.TO", "CSU.TO", "OTEX.TO", "BB.TO", "LSPD.TO",
    "CLS.TO", "GIB-A.TO",
    # ── Canadian Consumer / Retail (10) ─────────────────────────────────
    "ATD.TO", "L.TO", "WN.TO", "SAP.TO", "MFI.TO",
    "DOL.TO", "GIL.TO", "CTC-A.TO", "MG.TO", "BRP.TO",
    # ── Canadian Telecom (3) ────────────────────────────────────────────
    "BCE.TO", "T.TO", "RCI-B.TO",
    # ── Canadian Utilities (4) ──────────────────────────────────────────
    "FTS.TO", "EMA.TO", "H.TO", "AQN.TO",
    # ── Canadian Tech (additional) / Other (3) ──────────────────────────
    "KXS.TO", "DSG.TO", "DCBO.TO",
    # ── Canadian Real Estate (4) ────────────────────────────────────────
    "CAR-UN.TO", "REI-UN.TO", "GRT-UN.TO", "SRU-UN.TO",
    # ── US Uranium (10) ───────────────────────────────────────────────
    "CCJ", "UEC", "UUUU", "DNN", "LEU", "NXE", "URG", "SMR", "OKLO", "LTBR",
    # ── Canadian Uranium (5) ──────────────────────────────────────────
    "NXE.TO", "DML.TO", "FCU.TO", "EFR.TO", "URC.TO",
    # ── US Crypto / Blockchain (10) ───────────────────────────────────
    "MSTR", "CLSK", "HUT", "BITF", "CIFR", "BTDR", "IREN", "WULF", "CORZ", "BTBT",
    # ── Canadian Crypto / Blockchain (3) ──────────────────────────────
    "HUT.TO", "BITF.TO", "HIVE.TO",
    # ── US Sports & Entertainment (12) ────────────────────────────────
    "TKO", "PENN", "FLUT", "CHDN", "LNW", "MSGS", "MSGE", "FWONK",
    "WMG", "SPOT", "IMAX", "WWE",
]


def fetch_ticker_lists():
    """Return the curated list of US and Canadian stock tickers."""
    return sorted(TICKERS)


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
    df[col] = df[col].apply(lambda x: round(float(x), 2) if pd.notna(x) and isinstance(x, (int, float)) else "N/A")

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
pd.set_option("display.max_rows", None)
print(df.to_string())
print(f"{'=' * width}")
print(f"\nTotal stocks found: {len(df)}")
if len(df) > 0:
    print(f"Biggest drop: {df.iloc[0]['Ticker']} at {df.iloc[0]['Drop from High (%)']}%")
    print(f"Average drop: {df['Drop from High (%)'].mean():.2f}%")
