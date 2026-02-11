import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Attempt to download live AAPL data; fall back to sample data if unavailable
try:
    ticker = yf.Ticker("AAPL")
    data = ticker.history(period="3mo")
    if data.empty:
        raise ValueError("No data returned")
    source = "Yahoo Finance (live)"
except Exception:
    # Generate realistic sample stock data for demonstration
    np.random.seed(42)
    num_rows = 25
    dates = pd.bdate_range(end=datetime.now(), periods=num_rows)

    base_price = 230.0
    returns = np.random.normal(0.001, 0.015, num_rows)
    close_prices = base_price * np.cumprod(1 + returns)
    open_prices = close_prices * (1 + np.random.normal(0, 0.005, num_rows))
    high_prices = np.maximum(open_prices, close_prices) * (1 + np.abs(np.random.normal(0, 0.008, num_rows)))
    low_prices = np.minimum(open_prices, close_prices) * (1 - np.abs(np.random.normal(0, 0.008, num_rows)))
    volume = np.random.randint(40_000_000, 90_000_000, num_rows)
    dividends = np.zeros(num_rows)
    stock_splits = np.zeros(num_rows)

    data = pd.DataFrame({
        "Open": np.round(open_prices, 2),
        "High": np.round(high_prices, 2),
        "Low": np.round(low_prices, 2),
        "Close": np.round(close_prices, 2),
        "Volume": volume,
        "Dividends": dividends,
        "Stock Splits": stock_splits,
    }, index=dates)
    data.index.name = "Date"
    source = "Sample data (network unavailable)"

# Display a 25-row preview of the data in table format
print("=" * 100)
print(f"{'AAPL Stock Data - 25 Row Preview':^100}")
print(f"{'Source: ' + source:^100}")
print("=" * 100)
print(data.head(25).to_string())
print("=" * 100)
print(f"\nShape: {data.shape[0]} rows x {data.shape[1]} columns")
print(f"Columns: {', '.join(data.columns.tolist())}")
