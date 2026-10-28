# Customer Segmentation Using RFM Analysis

> Segments customers by Recency, Frequency, and Monetary value so that marketing teams can match each campaign to the right customer group.

## 1. Business Problem

An online retailer serving customers across the United States wants to make its marketing spend more efficient. Sending the same promotion to every customer overspends on those who would buy anyway and under-invests in valuable customers who are becoming inactive. This project uses order history to identify which customers to retain, which to re-engage, and which to deprioritize.

**Questions addressed**
1. Which customer segments generate the most revenue?
2. Which segments are at risk of churning and warrant a win-back campaign?
3. How should marketing effort be prioritized across segments?

## 2. Dataset

- **Source:** [E-Commerce U.S. Dataset (2019~2025, 1 Million rows)](https://www.kaggle.com/datasets/limjeongeun/synthetic-u-s-e-commerce-dataset-1m-orders) on Kaggle
- **Nature of data:** Synthetic. The records are artificially generated, so the findings illustrate the analytical method and do not describe real customer behavior.
- **Size:** Approximately 1 million order records
- **Period:** 2019 to 2025
- **License:** [Confirm on the Kaggle dataset page]
- **Fields used:** [customer ID column], [order date column], [order or invoice ID column], [quantity column], [price or amount column]

The raw file is not included in this repository. To reproduce the analysis, download the dataset from the link above, save it as `data/orders.csv`, and run the script.

## 3. Tools

`SQL` · `Python (pandas, matplotlib)`

## 4. Data Cleaning

Before computing RFM metrics, the data was checked and cleaned in the following steps. Row counts were recorded after each step to keep the process transparent and reproducible.

| Step | Check | Action | Rows affected |
|---|---|---|---|
| 1 | Initial load | Load raw file and inspect structure, column types, and date range | [ ] rows loaded |
| 2 | Missing values | Count nulls per column; remove records with no customer identifier, since they cannot be attributed to a customer | [ ] rows removed |
| 3 | Duplicates | Identify exact duplicate records and duplicate order lines; remove duplicates | [ ] rows removed |
| 4 | Data types | Convert the order date to a date type; convert quantity and price to numeric types | [ ] columns converted |
| 5 | Invalid values | Exclude records with non-positive quantity or price; handle cancelled or returned orders if the dataset flags them | [ ] rows removed |
| 6 | Outliers | Inspect order values using the interquartile range and the 99th percentile; document any extreme values and decide whether to keep or cap them | [ ] rows flagged |
| 7 | Consistency | Confirm dates fall within the stated period and that totals equal quantity multiplied by price where both are present | [ ] inconsistencies found |
| 8 | Final dataset | Create the sales column and save the cleaned dataset | [ ] rows retained |

**Notes**
- Because the dataset is synthetic, some checks may find no issues. Each check is still reported, since documenting that the data was verified is part of a sound analysis.
- Cleaning logic is in [`src/rfm_analysis.py`](./src/rfm_analysis.py), function `clean()`.

## 5. Methodology

1. **RFM calculation:** For each customer, compute Recency (days from the last purchase to a snapshot date set one day after the most recent order), Frequency (number of distinct orders), and Monetary value (total spend).
2. **Scoring:** Assign each metric a score from 1 to 5 using quintiles, then map score combinations to segments (Champions, Loyal, New / Promising, At Risk, Need Attention, Lost).
3. **Segment profiling:** Summarize customer count, average recency and frequency, and revenue contribution for each segment, then propose a campaign approach.

**Code:** [`src/rfm_analysis.py`](./src/rfm_analysis.py) · **SQL equivalent:** [`sql/rfm_analysis.sql`](./sql/rfm_analysis.sql)

## 6. Key Findings

Figures below are produced by running `src/rfm_analysis.py` (see `images/segment_summary.csv`).

| Segment | Customers | Share of revenue | Recommended action |
|---|---|---|---|
| Champions | [ ] | [ ]% | Reward loyalty with early access to new products and exclusive offers |
| At Risk | [ ] | [ ]% | Send time-limited win-back offers to recover previously valuable customers |
| Lost | [ ] | [ ]% | Limit spend; use low-cost channels such as periodic email |

![Revenue share by segment](./images/rfm_segments.png)

## 7. Business Recommendations

- **Protect high-value customers first.** Prioritize retention spend on Champions and Loyal customers, since losing them has the largest revenue impact.
- **Target At Risk customers with win-back offers.** These customers purchased frequently in the past but have gone quiet, making them the most promising group for reactivation.
- **Reduce spend on Lost customers.** Use low-cost channels rather than paid campaigns, as the expected return is lowest.
- **Nurture New / Promising customers.** Encourage a second purchase early, while repeat behavior is still forming.

## 8. Limitations

- The data is synthetic, so segment sizes and revenue shares reflect how the data was generated rather than real customer behavior. The value of this project lies in the method, which can be applied unchanged to real transaction data.
- RFM describes past behavior only and does not predict future purchases.
- Segment thresholds (quintile cut-offs) are a modeling choice and may be tuned for a specific business.

## 9. How to Run

```bash
git clone https://github.com/oum292929/data-analyst-portfolio.git
cd data-analyst-portfolio/01-marketing-rfm-segmentation
pip install -r requirements.txt
python src/rfm_analysis.py data/orders.csv
```
