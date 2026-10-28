-- RFM analysis in SQL (SQLite syntax; PostgreSQL notes in comments)
-- Assumed table: orders(invoice_no, invoice_date, quantity, unit_price, customer_id)

-- Step 1: clean rows and compute sales
WITH clean AS (
    SELECT
        customer_id,
        invoice_no,
        DATE(invoice_date) AS invoice_date,
        quantity * unit_price AS sales
    FROM orders
    WHERE customer_id IS NOT NULL
      AND quantity > 0
      AND unit_price > 0
),

-- Step 2: R, F, M per customer
rfm_raw AS (
    SELECT
        customer_id,
        CAST(JULIANDAY((SELECT MAX(invoice_date) FROM clean)) - JULIANDAY(MAX(invoice_date)) AS INTEGER) + 1 AS recency,
        -- PostgreSQL: (SELECT MAX(invoice_date) FROM clean) - MAX(invoice_date) + 1
        COUNT(DISTINCT invoice_no) AS frequency,
        ROUND(SUM(sales), 2)       AS monetary
    FROM clean
    GROUP BY customer_id
),

-- Step 3: quintile scores 1-5 (NTILE)
scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,   -- recent buyers get 5
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
    FROM rfm_raw
),

-- Step 4: segment labels
segmented AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Need Attention'
        END AS segment
    FROM scored
)

-- Step 5: segment summary
SELECT
    segment,
    COUNT(*)                         AS customers,
    ROUND(AVG(recency), 1)           AS avg_recency_days,
    ROUND(AVG(frequency), 1)         AS avg_orders,
    ROUND(SUM(monetary), 2)          AS total_revenue,
    ROUND(SUM(monetary) * 100.0 / SUM(SUM(monetary)) OVER (), 1) AS revenue_share_pct
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;
