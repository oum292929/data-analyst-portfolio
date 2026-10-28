-- RFM analysis in SQL (SQLite syntax; PostgreSQL alternatives in comments)
--
-- Assumed table: orders(order_id, order_date, customer_id, sales)
--   sales = order amount for the row. If your data has quantity and price
--   instead, use quantity * price AS sales in the first CTE below.
-- Rename the columns in the "clean" CTE to match your table.

-- Step 1: data cleaning
WITH clean AS (
    SELECT DISTINCT                                  -- removes exact duplicate rows
        customer_id,
        order_id,
        DATE(order_date) AS order_date,
        sales
    FROM orders
    WHERE customer_id IS NOT NULL                    -- missing values
      AND order_id    IS NOT NULL
      AND order_date  IS NOT NULL
      AND sales > 0                                  -- invalid values / returns
),

-- Step 2: R, F, M per customer
rfm_raw AS (
    SELECT
        customer_id,
        CAST(JULIANDAY((SELECT MAX(order_date) FROM clean)) - JULIANDAY(MAX(order_date)) AS INTEGER) + 1 AS recency,
        -- PostgreSQL: (SELECT MAX(order_date) FROM clean) - MAX(order_date) + 1
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(sales), 2)     AS monetary
    FROM clean
    GROUP BY customer_id
),

-- Step 3: quintile scores 1-5 (NTILE)
scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,   -- most recent buyers get 5
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
    COUNT(*)                 AS customers,
    ROUND(AVG(recency), 1)   AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_orders,
    ROUND(SUM(monetary), 2)  AS total_revenue,
    ROUND(SUM(monetary) * 100.0 / SUM(SUM(monetary)) OVER (), 1) AS revenue_share_pct
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;
