"""Stock risk & return analysis.

Usage:
    python src/stock_analysis.py

Edit TICKERS / START / END below to analyse your own stocks.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

TICKERS = ["PTT.BK", "CPALL.BK", "AOT.BK", "SCB.BK", "ADVANC.BK"]
START = "2021-01-01"
END = "2025-12-31"
RISK_FREE_RATE = 0.02  # annual, adjust to the rate you want to use
TRADING_DAYS = 252


def download_prices(tickers, start, end) -> pd.DataFrame:
    import yfinance as yf

    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = data["Close"].dropna(how="all")
    return prices.dropna()


def compute_metrics(prices: pd.DataFrame, rf: float = RISK_FREE_RATE) -> pd.DataFrame:
    returns = prices.pct_change().dropna()
    ann_return = (1 + returns.mean()) ** TRADING_DAYS - 1
    ann_vol = returns.std() * np.sqrt(TRADING_DAYS)
    sharpe = (ann_return - rf) / ann_vol
    cum = (1 + returns).cumprod()
    max_dd = (cum / cum.cummax() - 1).min()
    return pd.DataFrame(
        {
            "AnnReturn%": (ann_return * 100).round(2),
            "AnnVolatility%": (ann_vol * 100).round(2),
            "Sharpe": sharpe.round(2),
            "MaxDrawdown%": (max_dd * 100).round(2),
        }
    ).sort_values("Sharpe", ascending=False)


def plot_cumulative(prices: pd.DataFrame, path: str) -> None:
    cum = prices / prices.iloc[0] * 100
    ax = cum.plot(figsize=(10, 5))
    ax.set_title("Cumulative performance (start = 100)")
    ax.set_ylabel("Index")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_correlation(prices: pd.DataFrame, path: str) -> None:
    corr = prices.pct_change().dropna().corr()
    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", vmin=-1, vmax=1)
    plt.title("Correlation of daily returns")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


if __name__ == "__main__":
    px = download_prices(TICKERS, START, END)
    metrics = compute_metrics(px)
    print(metrics)
    metrics.to_csv("data/metrics_summary.csv")
    plot_cumulative(px, "images/cumulative_returns.png")
    plot_correlation(px, "images/correlation.png")
    print("Saved charts to images/ and metrics to data/metrics_summary.csv")
