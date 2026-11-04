# HƯỚNG DẪN 03: THỰC THI PIPELINE ETL PHÂN TẦNG (ETL PIPELINE EXECUTION)

---

## 1. TỔNG QUAN LUỒNG ETL

Pipeline ETL xử lý dữ liệu qua 3 giai đoạn phân tầng:
$$\mathbf{Bronze\ (Raw)} \xrightarrow{\text{Transform \& Clean}} \mathbf{Silver\ (Standardized)} \xrightarrow{\text{Dimensional Load}} \mathbf{Gold\ (Star\ Schema)}$$

---

## 2. CHẠY TOÀN BỘ PIPELINE TỰ ĐỘNG (FULL PIPELINE RUN)

Để chạy tự động toàn bộ luồng từ file nguồn đến các bảng Fact/Dimension tầng Gold:
```powershell
python -m src.pipeline.flows.bronze_to_gold --input "dataset/superstore_dataset2011-2015.csv"
```
*(File dataset chuẩn đã được tích hợp sẵn ngay trong thư mục `dataset/` của dự án để đảm bảo tính đồng bộ và di động khi clone repo).*

---

## 3. CHẠY TỪNG BƯỚC ĐỂ KIỂM THỬ VÀ DEBUG (STEP-BY-STEP RUN)

### Bước 1: Nạp dữ liệu thô vào tầng Bronze
```powershell
python -m src.etl.bronze.data_to_bronze --input "dataset/superstore_dataset2011-2015.csv"
```
- **Kiểm tra kết quả Bronze:**
  ```sql
  SELECT COUNT(*) FROM bronze.raw_orders;  -- Mong đợi: 51,290 dòng
  SELECT * FROM bronze.ingestion;          -- Xem mã băm SHA-256 và metadata
  ```
- **Thử nghiệm Idempotency:** Chạy lại lệnh trên lần thứ 2, hệ thống sẽ in ra:
  ```text
  File already extracted. Skipping ingestion.
  ```

---

### Bước 2: Chuyển đổi và làm sạch dữ liệu vào tầng Silver
```powershell
python -m src.etl.silver.transform
```
- Quá trình này sẽ:
  - Parse ngày tháng đa định dạng (`d/m/Y`, `d-m-Y`) thành kiểu `DATE` chuẩn.
  - Ép kiểu số thực `NUMERIC(12, 4)` cho `sales`, `profit`, `shipping_cost`.
  - Thay thế giá trị NULL trong `Postal Code` thành `'Unknown'`.
  - Nối với sheet `Returns` để đánh dấu cờ `is_returned`.
  - Nối với sheet `People` để gán `regional_manager`.
- **Chạy kiểm định chất lượng dữ liệu Silver:**
  ```powershell
  python -m src.etl.silver.validate
  ```
  Script sẽ tự động chạy:
  - `check_nulls.sql`: Đảm bảo 0 cột bắt buộc bị NULL.
  - `check_duplicates.sql`: Đảm bảo `row_id` duy nhất 100%.
  - `check_data_quality.sql`: Đảm bảo `ship_date >= order_date` và `discount <= 1.0`.

---

### Bước 3: Nạp mô hình Star Schema tầng Gold
```powershell
# 3.1 Nạp các bảng Chiều (Dimensions)
python -m src.etl.gold.load_dimensions

# 3.2 Nạp bảng Fact (FactSales)
python -m src.etl.gold.load_facts
```

- **Chạy kiểm định chất lượng dữ liệu Gold:**
  ```powershell
  python -m src.etl.gold.validate
  ```
  Script sẽ đối soát:
  - `check_fact_grain.sql`: Xác nhận mỗi dòng trong `fact_sales` tương ứng đúng 1 dòng đơn hàng gốc.
  - `check_foreign_keys.sql`: Đảm bảo không có dòng nào có khóa ngoại bị NULL.
  - `check_aggregates.sql`: So sánh tổng Sales và Profit giữa Silver và Gold. Sai số cho phép: $0.0000$.

---

## 4. HƯỚNG DẪN KIỂM THỬ NẠP GIA TĂNG (INCREMENTAL LOAD DEMO)

Để chứng minh hệ thống có khả năng tiếp nhận đợt nhập dữ liệu mới định kỳ:
1. Chuẩn bị file dữ liệu gia tăng (ví dụ: `Sample - Superstore.csv` khoảng 10,000 dòng giai đoạn 2014–2018).
2. Chạy lệnh nạp gia tăng:
   ```powershell
   python -m src.pipeline.flows.bronze_to_gold --input "data/sample/Sample - Superstore.csv"
   ```
3. Hệ thống sẽ:
   - Ghi nhận batch mới vào `bronze.ingestion`.
   - Nạp các đơn hàng mới vào `silver.orders` mà không ghi đè dữ liệu cũ.
   - Thêm các khách hàng hoặc sản phẩm mới vào `dim_customer`, `dim_product`.
   - Nạp các giao dịch mới vào `gold.fact_sales`.
   - Tự động làm mới Materialized Views bằng lệnh:
     ```sql
     REFRESH MATERIALIZED VIEW gold.mv_sales_mart;
     REFRESH MATERIALIZED VIEW gold.mv_product_mart;
     REFRESH MATERIALIZED VIEW gold.mv_customer_mart;
     ```
