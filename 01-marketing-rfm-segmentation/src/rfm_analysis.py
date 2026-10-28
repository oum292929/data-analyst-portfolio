"""RFM customer segmentation.

Usage:
    python src/rfm_analysis.py data/online_retail.csv

Expected columns: InvoiceNo, InvoiceDate, Quantity, UnitPrice, CustomerID
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["CustomerID"]).copy()
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Sales"] = df["Quantity"] * df["UnitPrice"]
    return df


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Sales", "sum"),
    )
    # quintile score 1-5 (rank first so ties do not break qcut)
    rfm["R"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm


def segment(row) -> str:
    r, f = row["R"], row["F"]
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / Promising"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2:
        return "Lost"
    return "Need Attention"


def summarize(rfm: pd.DataFrame) -> pd.DataFrame:
    s = rfm.groupby("Segment").agg(
        Customers=("Monetary", "size"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        TotalRevenue=("Monetary", "sum"),
    )
    s["RevenueShare%"] = (s["TotalRevenue"] / s["TotalRevenue"].sum() * 100).round(1)
    return s.sort_values("TotalRevenue", ascending=False).round(1)


def plot(summary: pd.DataFrame, out_path: str) -> None:
    ax = summary["RevenueShare%"].plot(kind="bar", figsize=(8, 5), color="#2f6f9f")
    ax.set_title("Revenue share by customer segment")
    ax.set_ylabel("% of total revenue")
    ax.set_xlabel("")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/online_retail.csv"
    data = clean(pd.read_csv(path, encoding="ISO-8859-1"))
    rfm_table = build_rfm(data)
    result = summarize(rfm_table)
    print(result)
    result.to_csv("images/segment_summary.csv")
    plot(result, "images/rfm_segments.png")
    print("Saved images/rfm_segments.png and images/segment_summary.csv")
