# HƯỚNG DẪN 04: THỰC THI TRUY VẤN OLAP & DATA MARTS (OLAP & MARTS GUIDE)

---

## 1. MỤC TIÊU

Hướng dẫn cách thực thi các truy vấn phân tích đa chiều (OLAP) trên mô hình Star Schema tầng Gold, phục vụ trả lời các câu hỏi nghiệp vụ và chứng minh năng lực khai thác kho dữ liệu trước Hội đồng chấm thi.

---

## 2. CHẠY BỘ TRUY VẤN OLAP BẰNG PYTHON RUNNER

Nhóm đã đóng gói sẵn công cụ chạy tự động toàn bộ 8 câu truy vấn OLAP mẫu và in bảng kết quả trực tiếp ra màn hình terminal:
```powershell
python -m src.sql.gold.marts.run_olap_suite
```

---

## 3. DANH MỤC CÁC CÂU TRUY VẤN OLAP MẪU ĐỂ DEMO TRỰC TIẾP

### 3.1. Thao tác Roll-Up (Tổng hợp cấp cao)
- **File SQL:** `src/sql/gold/marts/olap_rollup.sql`
- **Mô tả:** Tổng hợp doanh thu và lợi nhuận từ mức Tháng -> Quý -> Năm, và từ Thành phố -> Quốc gia -> Thị trường.
- **Cách chạy trên pgAdmin:** Mở file và bấm `F5`.

### 3.2. Thao tác Drill-Down (Khoan sâu chi tiết)
- **File SQL:** `src/sql/gold/marts/olap_drilldown.sql`
- **Mô tả:** Đi sâu từ Ngành hàng `Technology` -> Danh mục con `Copiers` -> Từng mã sản phẩm SKU cụ thể để tìm ra sản phẩm đóng góp nhiều lợi nhuận nhất.

### 3.3. Thao tác Slice & Dice (Cắt lát & Lập phương con)
- **File SQL:** `src/sql/gold/marts/olap_slice_dice.sql`
- **Mô tả:** 
  - *Slice:* Cắt một lát dữ liệu duy nhất cho thị trường `APAC` trong năm `2014`.
  - *Dice:* Lập phương con đa điều kiện: `Market IN ('APAC', 'EU')`, `Category IN ('Furniture', 'Technology')` trong các quý cuối năm (`Q3, Q4`).

### 3.4. Thao tác Pivot (Xoay trục dữ liệu)
- **File SQL:** `src/sql/gold/marts/olap_pivot.sql`
- **Mô tả:** Xoay 4 Quý (Q1, Q2, Q3, Q4) thành 4 cột ngang để so sánh trực diện doanh số của 17 Phân nhóm sản phẩm trong năm 2014.

### 3.5. Phân tích Tăng trưởng MoM bằng Window Function
- **File SQL:** `src/sql/gold/marts/olap_growth_mom.sql`
- **Mô tả:** Sử dụng hàm `LAG()` để tính tốc độ tăng trưởng doanh số theo từng tháng liên tục qua 4 năm.

### 3.6. Xếp hạng Top Sản phẩm bằng DENSE_RANK()
- **File SQL:** `src/sql/gold/marts/olap_top_products.sql`
- **Mô tả:** Sử dụng `DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC)` để lấy Top 5 sản phẩm bán chạy nhất trong từng ngành hàng.

### 3.7. Siêu lập phương tổng hợp với GROUP BY CUBE
- **File SQL:** `src/sql/gold/marts/olap_cube.sql`
- **Mô tả:** Tạo ra bảng đa chiều đầy đủ mọi tổ hợp chiều `(Year, Category, Market)` kèm subtotal và grand total tự động.

---

## 4. TẠO VÀ LÀM MỚI CÁC DATA MARTS (MATERIALIZED VIEWS)

Chạy file khởi tạo 3 Materialized Views:
```powershell
python -m src.pipeline.executor --sql "src/sql/gold/marts/create_materialized_views.sql"
```

Khi có dữ liệu mới được nạp vào, làm mới Materialized Views bằng lệnh:
```sql
REFRESH MATERIALIZED VIEW gold.mv_sales_mart;
REFRESH MATERIALIZED VIEW gold.mv_product_mart;
REFRESH MATERIALIZED VIEW gold.mv_customer_mart;
```

---

## 5. ĐÁNH GIÁ HIỆU NĂNG TRUY VẤN (EXPLAIN ANALYZE)
Để kiểm tra tốc độ truy vấn trên Gold Star Schema có Index so với bảng thô:
```sql
EXPLAIN ANALYZE
SELECT 
    d.year,
    g.market,
    p.category,
    SUM(f.sales) AS total_sales,
    SUM(f.profit) AS total_profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
GROUP BY d.year, g.market, p.category;
```
Nhờ sử dụng khóa thay thế kiểu số nguyên (`INTEGER`) và các B-Tree Indexes trên các cột khóa ngoại, thời gian thực thi của câu truy vấn đa chiều trên hơn 51,000 bản ghi đạt dưới **50ms**.
