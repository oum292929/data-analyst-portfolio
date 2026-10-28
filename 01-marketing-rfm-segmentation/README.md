# 🛍 Customer Segmentation with RFM Analysis

> แบ่งกลุ่มลูกค้าด้วย RFM (Recency, Frequency, Monetary) เพื่อให้ทีมการตลาดรู้ว่าควรทำแคมเปญแบบไหนกับลูกค้ากลุ่มไหน

## 1. Business Problem
[อธิบาย 2-3 ประโยค เช่น: ร้านค้าออนไลน์มีลูกค้าจำนวนมากแต่ส่งโปรโมชันเหมือนกันทุกคน ต้องการรู้ว่าใครคือลูกค้าที่ควรรักษาไว้ และใครกำลังจะหายไป]

**คำถามที่ต้องการตอบ**
1. ลูกค้ากลุ่มไหนสร้างรายได้สูงสุด?
2. ลูกค้ากลุ่มไหนเสี่ยงหายไปและควรทำ win-back campaign?
3. ควรแบ่งงบการตลาดให้แต่ละกลุ่มอย่างไร?

## 2. Dataset
- **แหล่งที่มา:** [Online Retail (UCI / Kaggle)] · [ใส่ลิงก์ที่ดาวน์โหลดจริง]
- **คอลัมน์ที่ใช้:** InvoiceNo, InvoiceDate, Quantity, UnitPrice, CustomerID
- **ขนาด/ช่วงเวลา:** [จำนวนแถว] แถว · [ช่วงเวลา]

> วางไฟล์ข้อมูลไว้ที่ `data/online_retail.csv` (ถ้าไฟล์ใหญ่ ไม่ต้องอัปโหลดขึ้น GitHub ให้ใส่ลิงก์ดาวน์โหลดไว้ที่นี่แทน)

## 3. Tools
`SQL` · `Python (pandas, matplotlib)`

## 4. Method
1. **Data Cleaning** – ตัดแถวที่ไม่มี CustomerID, ตัดรายการคืนสินค้า (Quantity ≤ 0), สร้างคอลัมน์ยอดขาย
2. **คำนวณ RFM** – Recency (วันนับจากซื้อล่าสุด), Frequency (จำนวนใบสั่งซื้อ), Monetary (ยอดซื้อรวม)
3. **ให้คะแนน 1-5** ด้วย quintile แล้วจัดกลุ่ม เช่น Champions, Loyal, At Risk, Lost
4. **สรุปแต่ละกลุ่ม** และเสนอแนวทางแคมเปญ

โค้ด: [`src/rfm_analysis.py`](./src/rfm_analysis.py) · SQL: [`sql/rfm_analysis.sql`](./sql/rfm_analysis.sql)

## 5. Key Findings
| กลุ่มลูกค้า | จำนวน | สัดส่วนรายได้ | ข้อเสนอแนะ |
|---|---|---|---|
| Champions | [ ] | [ ]% | [เช่น ให้สิทธิพิเศษ/early access] |
| At Risk | [ ] | [ ]% | [เช่น ส่งคูปองดึงกลับ] |
| Lost | [ ] | [ ]% | [เช่น ลดงบหรือส่งแบบประหยัดต้นทุน] |

![segment chart](./images/rfm_segments.png)

## 6. Business Recommendations
- [ข้อเสนอแนะ 1 พร้อมเหตุผลจากข้อมูล]
- [ข้อเสนอแนะ 2]

## 7. How to Run
```bash
git clone https://github.com/oum292929/data-analyst-portfolio.git
cd data-analyst-portfolio/01-marketing-rfm-segmentation
pip install -r requirements.txt
python src/rfm_analysis.py data/online_retail.csv
```
