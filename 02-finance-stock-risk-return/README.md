# 📉 Stock Risk & Return Analysis

> วิเคราะห์ผลตอบแทนและความเสี่ยงของหุ้นหลายตัว เพื่อดูว่าตัวไหนให้ผลตอบแทนคุ้มความเสี่ยง และการกระจายพอร์ตช่วยลดความผันผวนได้แค่ไหน

⚠️ โปรเจคนี้ทำเพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุน

## 1. Business Question
1. หุ้นตัวไหนให้ผลตอบแทนปรับความเสี่ยงแล้ว (Sharpe Ratio) ดีที่สุด?
2. หุ้นแต่ละตัวเคยขาดทุนหนักสุดเท่าไร (Max Drawdown)?
3. หุ้นกลุ่มไหนเคลื่อนไหวสัมพันธ์กัน และการถือหลายตัวช่วยกระจายความเสี่ยงได้หรือไม่?

## 2. Data
- **แหล่งที่มา:** Yahoo Finance ผ่านไลบรารี `yfinance`
- **หุ้นที่เลือก:** [เช่น PTT.BK, CPALL.BK, AOT.BK, SCB.BK, ADVANC.BK หรือหุ้นสหรัฐ AAPL, MSFT]
- **ช่วงเวลา:** [เช่น 2021-01-01 ถึง 2025-12-31]

## 3. Tools
`Python (pandas, numpy, yfinance, matplotlib, seaborn)`

## 4. Metrics ที่คำนวณ
| Metric | ความหมาย |
|---|---|
| Annualized Return | ผลตอบแทนเฉลี่ยต่อปี |
| Annualized Volatility | ความผันผวนต่อปี (ตัวแทนความเสี่ยง) |
| Sharpe Ratio | ผลตอบแทนส่วนเกินต่อหน่วยความเสี่ยง |
| Max Drawdown | ขาดทุนสูงสุดจากจุดสูงสุดถึงจุดต่ำสุด |
| Correlation Matrix | ความสัมพันธ์ของผลตอบแทนระหว่างหุ้น |

โค้ด: [`src/stock_analysis.py`](./src/stock_analysis.py)

## 5. Key Findings
| # | Insight | Evidence |
|---|---|---|
| 1 | [หุ้นที่ Sharpe สูงสุด] | [ตัวเลข] |
| 2 | [หุ้นที่ drawdown หนักสุด] | [ตัวเลข] |
| 3 | [คู่หุ้นที่ correlation ต่ำ เหมาะกระจายความเสี่ยง] | [ตัวเลข] |

![cumulative returns](./images/cumulative_returns.png)
![correlation](./images/correlation.png)

## 6. Conclusion
[สรุป 2-3 ประโยค และข้อจำกัด เช่น ใช้ข้อมูลย้อนหลังเท่านั้น ไม่รวมค่าธรรมเนียม]

## 7. How to Run
```bash
git clone https://github.com/oum292929/data-analyst-portfolio.git
cd data-analyst-portfolio/02-finance-stock-risk-return
pip install -r requirements.txt
python src/stock_analysis.py
```
แก้รายชื่อหุ้นและช่วงเวลาที่ตัวแปร `TICKERS`, `START`, `END` ในไฟล์ `src/stock_analysis.py`
