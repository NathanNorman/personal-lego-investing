"""
Fetch S&P 500 data and calculate ROI comparisons.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf


def get_sp500_data(start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    """
    Fetch S&P 500 historical data.

    Args:
        start_date: Start date (YYYY-MM-DD), defaults to 2 years ago
        end_date: End date (YYYY-MM-DD), defaults to today

    Returns:
        DataFrame with Date, Close, and daily returns
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Fetch S&P 500 ETF (SPY) as proxy
    spy = yf.Ticker("SPY")
    df = spy.history(start=start_date, end=end_date)

    # Calculate returns
    df["daily_return"] = df["Close"].pct_change()
    df["cumulative_return"] = (1 + df["daily_return"]).cumprod() - 1

    return df[["Close", "daily_return", "cumulative_return"]].reset_index()


def calculate_sp500_return(start_date: str, end_date: str | None = None) -> float:
    """
    Calculate S&P 500 return between two dates.

    Args:
        start_date: Investment start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD), defaults to today

    Returns:
        Return as decimal (e.g., 0.15 for 15%)
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = get_sp500_data(start_date, end_date)

    if len(df) < 2:
        return 0.0

    start_price = df.iloc[0]["Close"]
    end_price = df.iloc[-1]["Close"]

    return (end_price - start_price) / start_price


def calculate_lego_roi(
    retail_price: float,
    current_price: float,
    purchase_date: str,
) -> dict:
    """
    Calculate LEGO set ROI and compare to S&P 500.

    Args:
        retail_price: Original retail price
        current_price: Current market price
        purchase_date: Date of purchase (YYYY-MM-DD)

    Returns:
        Dictionary with ROI metrics
    """
    # LEGO ROI
    lego_return = (current_price - retail_price) / retail_price

    # S&P 500 return for same period
    sp500_return = calculate_sp500_return(purchase_date)

    # What would the same money have made in S&P 500?
    sp500_equivalent = retail_price * (1 + sp500_return)

    return {
        "retail_price": retail_price,
        "current_price": current_price,
        "purchase_date": purchase_date,
        "lego_return_pct": round(lego_return * 100, 2),
        "sp500_return_pct": round(sp500_return * 100, 2),
        "lego_profit": round(current_price - retail_price, 2),
        "sp500_equivalent_value": round(sp500_equivalent, 2),
        "sp500_profit": round(sp500_equivalent - retail_price, 2),
        "outperformance_pct": round((lego_return - sp500_return) * 100, 2),
        "beats_sp500": lego_return > sp500_return,
    }


def get_sp500_monthly_returns(months: int = 24) -> list[dict]:
    """Get monthly S&P 500 returns for the last N months."""
    start_date = (datetime.now() - timedelta(days=months * 31)).strftime("%Y-%m-%d")
    df = get_sp500_data(start_date)

    # Resample to monthly
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    monthly = df["Close"].resample("M").last()

    monthly_returns = monthly.pct_change().dropna()

    return [
        {"month": idx.strftime("%Y-%m"), "return_pct": round(val * 100, 2)}
        for idx, val in monthly_returns.items()
    ]


def save_sp500_data(output_path: str) -> None:
    """Save S&P 500 data for dashboard."""
    # Get last 24 months of data
    df = get_sp500_data()

    # Convert to JSON-friendly format
    data = {
        "generated_at": datetime.now().isoformat(),
        "period": "24_months",
        "monthly_returns": get_sp500_monthly_returns(),
        "total_return_24m": round(calculate_sp500_return(
            (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
        ) * 100, 2),
        "total_return_12m": round(calculate_sp500_return(
            (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        ) * 100, 2),
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"S&P 500 data saved to {output_path}")
    print(f"24-month return: {data['total_return_24m']}%")
    print(f"12-month return: {data['total_return_12m']}%")


if __name__ == "__main__":
    output_file = Path(__file__).parent.parent / "data" / "processed" / "sp500_data.json"
    save_sp500_data(str(output_file))
