# HƯỚNG DẪN 05: VẬN HÀNH PIPELINE HỆ HỖ TRỢ QUYẾT ĐỊNH (DSS PIPELINE GUIDE)

---

## 1. MỤC TIÊU

Hướng dẫn thực thi các mô hình thuật toán hỗ trợ quyết định (DSS Engine) bao gồm:
1. **Sales & Demand Forecasting:** Dự báo chuỗi thời gian doanh thu và nhu cầu sản phẩm.
2. **What-If Simulation:** Mô phỏng sự biến thiên của Lợi nhuận khi thay đổi Tỷ lệ chiết khấu.
3. **Association Rule Mining:** Khai phá luật kết hợp sản phẩm mua kèm trong cùng giỏ hàng (Market Basket Analysis).

---

## 2. HƯỚNG DẪN CHẠY DỰ BÁO CHUỖI THỜI GIAN (PREDICTIVE PIPELINE)

### 2.1. Dự báo Doanh số Bán hàng Toàn cầu theo Tháng:
```powershell
python -m src.dss.predictive.run --target sales --horizon 6
```
- **Tham số:**
  - `--target`: Chỉ số mục tiêu (`sales` hoặc `quantity`).
  - `--horizon`: Số tháng tương lai cần dự báo (Mặc định: 6 tháng).
- **Quy trình xử lý tự động:**
  1. Trích xuất dữ liệu doanh số 48 tháng từ `gold.fact_sales` JOIN `gold.dim_date`.
  2. Chia tập dữ liệu Train / Test theo thứ tự thời gian (ví dụ: Train 2011–2013, Test 2014).
  3. Huấn luyện mô hình Exponential Smoothing (Holt-Winters) và mô hình Baseline Moving Average.
  4. Đánh giá sai số trên tập Test (`MAE`, `RMSE`, `MAPE`).
  5. Fit lại trên toàn bộ 48 tháng và dự báo 6 tháng tiếp theo (Nửa đầu năm 2015), kèm dải tin cậy 95%.
  6. Tự động ghi metadata vào `dss.forecast_run` và các điểm dự báo vào `dss.forecast_result`.

### 2.2. Kiểm tra kết quả dự báo trong PostgreSQL:
```sql
-- Xem thông tin lần chạy gần nhất và độ chính xác mô hình
SELECT * FROM dss.forecast_run ORDER BY run_id DESC LIMIT 1;

-- Xem các mốc dự báo tương lai
SELECT 
    forecast_date, 
    predicted_value, 
    lower_bound, 
    upper_bound 
FROM dss.forecast_result 
WHERE actual_value IS NULL 
ORDER BY forecast_date;
```

---

## 3. HƯỚNG DẪN CHẠY MÔ PHỎNG WHAT-IF (WHAT-IF SIMULATION ENGINE)

Để chạy kiểm thử công cụ mô phỏng What-if từ terminal:
```powershell
python -m src.dss.what_if.simulate --market "APAC" --category "Furniture" --discount 0.05 --elasticity 1.4
```
- **Ý nghĩa kịch bản:** Thử nghiệm tăng thêm **5% chiết khấu** cho ngành hàng **Furniture** tại thị trường **APAC**, với giả định hệ số co giãn cầu $e = 1.4$.
- **Kết quả hiển thị trên terminal:**
```text
============================================================
              WHAT-IF DECISION SIMULATION REPORT
============================================================
Target: Market = APAC | Category = Furniture
Parameters: Discount Adjustment = +5.0% | Elasticity = 1.40

[BASELINE CURRENT STATE]
  - Sales:        $1,240,000.00
  - Net Profit:     $438,421.00
  - Profit Margin:        35.35%

[SIMULATED SCENARIO]
  - Expected Sales:  $1,360,000.00 (+9.68%)
  - Expected Profit:   $392,110.00 (-10.56%)
  - Expected Margin:        28.83% (-6.52%)

[DECISION RECOMMENDATION]
  [!] WARNING / REJECT: Tăng chiết khấu làm xói mòn lợi nhuận ròng
      mặc dù doanh thu tăng trưởng. Không khuyến nghị áp dụng!
============================================================
```

---

## 4. HƯỚNG DẪN CHẠY KHAI PHÁ LUẬT KẾT HỢP (ASSOCIATION RULES)

Để tìm kiếm các sản phẩm thường được mua cùng nhau trong cùng một đơn hàng:
```powershell
python -m src.dss.association.run --algorithm apriori --min-support 0.005 --min-confidence 0.25 --min-lift 1.2
```
- **Quy trình xử lý:**
  1. Trích xuất các dòng đơn hàng gồm `order_id`, `product_id` từ `gold.fact_sales`.
  2. Tạo ma trận giỏ hàng (Basket Transaction Matrix).
  3. Áp dụng thuật toán Apriori hoặc FP-Growth để tìm tập mục phổ biến (Frequent Itemsets).
  4. Sinh các luật kết hợp $A \longrightarrow B$ và lọc theo ngưỡng: $\text{Support} \ge 0.5\%$, $\text{Confidence} \ge 25\%$, $\text{Lift} > 1.2$.
  5. Nối với `gold.dim_product` để lấy tên sản phẩm rõ nghĩa.
  6. Lưu trữ vào `dss.association_run` và `dss.association_rule`.

### Kiểm tra kết quả luật kết hợp trong CSDL:
```sql
SELECT 
    antecedent_names AS "San_Pham_Mua_Truoc",
    consequent_names AS "San_Pham_Goi_Y_Mua_Kem",
    ROUND(support * 100, 2) AS "Support_%",
    ROUND(confidence * 100, 2) AS "Confidence_%",
    ROUND(lift, 2) AS "Lift"
FROM dss.association_rule
ORDER BY lift DESC
LIMIT 10;
```
Những luật này sẽ được đưa thẳng lên giao diện Web DSS để gợi ý tạo gói combo khuyến mãi cho nhà quản trị.
