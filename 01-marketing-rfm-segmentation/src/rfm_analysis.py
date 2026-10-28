"""RFM customer segmentation with a documented data-cleaning log.

Usage:
    python src/rfm_analysis.py data/orders.csv

The script matches column names automatically (case-insensitive) for common
variants, e.g. customer_id / CustomerID, order_date / InvoiceDate,
order_id / InvoiceNo, quantity, price / UnitPrice, total_amount / sales.
If it cannot find a required column, it stops and lists the columns it saw.
Edit COLUMN_ALIASES below to add your own column names.

Outputs (in ../images/):
    cleaning_log.csv     row counts after each cleaning step
    segment_summary.csv  customers, recency, frequency, revenue per segment
    rfm_segments.png     revenue share by segment
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "images"

COLUMN_ALIASES = {
    "customer_id": ["customer_id", "customerid", "customer", "user_id", "userid", "cust_id", "client_id"],
    "order_id": ["order_id", "orderid", "invoice_no", "invoiceno", "invoice", "transaction_id",
                 "transactionid", "order_number", "order_no"],
    "order_date": ["order_date", "orderdate", "invoice_date", "invoicedate", "date", "purchase_date",
                   "transaction_date", "order_datetime", "timestamp", "order_timestamp"],
    "quantity": ["quantity", "qty", "units", "units_sold", "order_quantity"],
    "price": ["price", "unit_price", "unitprice", "item_price"],
    "amount": ["total_amount", "total", "amount", "sales", "revenue", "order_total", "total_price",
               "line_total", "order_value", "sales_amount"],
}


def _norm(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def resolve_columns(df: pd.DataFrame) -> dict:
    """Map standard names to the actual column names in the file."""
    lookup = {_norm(c): c for c in df.columns}
    found = {}
    for std, options in COLUMN_ALIASES.items():
        for opt in options:
            if opt in lookup:
                found[std] = lookup[opt]
                break
    missing = [k for k in ("customer_id", "order_id", "order_date") if k not in found]
    has_money = "amount" in found or ("quantity" in found and "price" in found)
    if missing or not has_money:
        need = missing + ([] if has_money else ["amount (or quantity + price)"])
        raise SystemExit(
            f"Could not find required column(s): {need}\n"
            f"Columns in file: {list(df.columns)}\n"
            "Add the right names to COLUMN_ALIASES at the top of this script."
        )
    return found


def clean(raw: pd.DataFrame):
    """Return (clean_df, cleaning_log). Column names are standardized."""
    log = []

    def record(step, check, action, before, after, note=""):
        log.append({"Step": step, "Check": check, "Action": action,
                    "RowsBefore": before, "RowsAfter": after,
                    "RowsAffected": before - after, "Note": note})

    cols = resolve_columns(raw)
    df = raw.rename(columns={v: k for k, v in cols.items()}).copy()
    n = len(df)
    record(1, "Initial load", "Load raw file", n, n, f"columns used: {cols}")

    # 2. missing values in key fields
    key = [c for c in ("customer_id", "order_id", "order_date") if c in df.columns]
    nulls = df[key].isna().sum().to_dict()
    before = len(df)
    df = df.dropna(subset=key)
    record(2, "Missing values", "Drop rows missing customer, order or date", before, len(df),
           f"nulls per key column: {nulls}")

    # 3. exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    record(3, "Duplicates", "Drop exact duplicate rows", before, len(df))

    # 4. data types
    before = len(df)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for c in ("quantity", "price", "amount"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    numeric = [c for c in ("quantity", "price", "amount") if c in df.columns]
    df = df.dropna(subset=["order_date"] + numeric)
    record(4, "Data types", "Convert date/numeric columns; drop unparseable values", before, len(df))

    # 5. invalid values
    before = len(df)
    valid = pd.Series(True, index=df.index)
    for c in numeric:
        valid &= df[c] > 0
    df = df[valid]
    record(5, "Invalid values", "Drop non-positive quantity, price or amount", before, len(df))

    # sales column
    df["sales"] = df["amount"] if "amount" in df.columns else df["quantity"] * df["price"]

    # 6. outliers (flag only, do not remove)
    q1, q3 = df["sales"].quantile([0.25, 0.75])
    upper = q3 + 1.5 * (q3 - q1)
    flagged = int((df["sales"] > upper).sum())
    record(6, "Outliers", "Flag sales above Q3 + 1.5*IQR (kept in data)", len(df), len(df),
           f"{flagged} rows flagged; upper fence = {upper:.2f}; max = {df['sales'].max():.2f}")

    # 7. consistency (report only)
    note = f"date range {df['order_date'].min().date()} to {df['order_date'].max().date()}"
    if {"amount", "quantity", "price"} <= set(df.columns):
        mismatch = int(((df["amount"] - df["quantity"] * df["price"]).abs() > 0.05 * df["amount"]).sum())
        note += f"; {mismatch} rows where amount differs from quantity*price by >5%"
    record(7, "Consistency", "Check date range and amount vs quantity*price", len(df), len(df), note)

    record(8, "Final dataset", "Cleaned data ready for RFM", len(df), len(df))
    return df, pd.DataFrame(log)


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df["order_date"].max().normalize() + pd.Timedelta(days=1)
    g = df.groupby("customer_id").agg(
        last_order=("order_date", "max"),
        Frequency=("order_id", "nunique"),
        Monetary=("sales", "sum"),
    )
    g["Recency"] = (snapshot - g["last_order"]).dt.days
    rfm = g[["Recency", "Frequency", "Monetary"]].copy()
    # quintile scores 1-5 (rank first so ties do not break qcut)
    rfm["R"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    r, f = rfm["R"], rfm["F"]
    rfm["Segment"] = np.select(
        [(r >= 4) & (f >= 4), (r >= 3) & (f >= 3), (r >= 4) & (f <= 2),
         (r <= 2) & (f >= 3), (r <= 2) & (f <= 2)],
        ["Champions", "Loyal", "New / Promising", "At Risk", "Lost"],
        default="Need Attention",
    )
    return rfm


def summarize(rfm: pd.DataFrame) -> pd.DataFrame:
    s = rfm.groupby("Segment").agg(
        Customers=("Monetary", "size"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        TotalRevenue=("Monetary", "sum"),
    )
    s["RevenueShare%"] = (s["TotalRevenue"] / s["TotalRevenue"].sum() * 100).round(1)
    return s.sort_values("TotalRevenue", ascending=False).round(1)


def plot(summary: pd.DataFrame, out_path: Path) -> None:
    ax = summary["RevenueShare%"].plot(kind="bar", figsize=(8, 5), color="#2f6f9f")
    ax.set_title("Revenue share by customer segment")
    ax.set_ylabel("% of total revenue")
    ax.set_xlabel("")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/orders.csv"
    OUT_DIR.mkdir(exist_ok=True)
    raw_df = pd.read_csv(path, low_memory=False)
    data, cleaning_log = clean(raw_df)
    pd.set_option("display.width", 200, "display.max_columns", 20, "display.max_colwidth", 80)
    print("=== Cleaning log ===")
    print(cleaning_log[["Step", "Check", "RowsBefore", "RowsAfter", "RowsAffected"]].to_string(index=False))
    cleaning_log.to_csv(OUT_DIR / "cleaning_log.csv", index=False)

    rfm_table = build_rfm(data)
    result = summarize(rfm_table)
    print("\n=== Segment summary ===")
    print(result)
    result.to_csv(OUT_DIR / "segment_summary.csv")
    plot(result, OUT_DIR / "rfm_segments.png")
    print(f"\nSaved cleaning_log.csv, segment_summary.csv, rfm_segments.png to {OUT_DIR}")
