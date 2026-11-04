# SSOT 04: ĐẶC TẢ CÁC TRUY VẤN VÀ THAO TÁC OLAP (OLAP ANALYTICAL SPECIFICATION)

> **Mã tài liệu:** SSOT-04  
> **Phiên bản:** 1.0  
> **Trạng thái:** Chính thức (Approved)  
> **Người biên soạn:** Đức Phát & Thành Phát

---

## 1. TỔNG QUAN VỀ OLAP TRONG HỆ THỐNG GLOBAL SUPERSTORE

Trong kiến trúc Kho dữ liệu, thành phần **OLAP (Online Analytical Processing)** cho phép người dùng khai thác dữ liệu đa chiều, thực hiện các thao tác phân tích từ tổng quan đến chi tiết với thời gian phản hồi nhanh.

Dữ liệu được tổ chức dưới dạng **Data Cube đa chiều** với các chiều phân tích cốt lõi:
- **Chiều Thời gian (Time):** `Year` -> `Quarter` -> `Month` -> `Day`
- **Chiều Địa lý (Geography):** `Market` -> `Region` -> `Country` -> `State` -> `City`
- **Chiều Sản phẩm (Product):** `Category` -> `Sub-Category` -> `Product Name`
- **Chiều Khách hàng (Customer):** `Segment` -> `Customer Name`
- **Độ đo (Measures):** `Total Sales`, `Total Profit`, `Total Quantity`, `Avg Discount`, `Profit Margin %`

---

## 2. HIỆN THỰC CÁC THAO TÁC OLAP CỐT LÕI (SQL IMPLEMENTATION)

### 2.1. Thao tác ROLL-UP (Tổng hợp dữ liệu lên mức cao hơn)
*Bài toán:* Tổng hợp doanh số và lợi nhuận từ mức chi tiết Tháng lên mức Quý và Năm, hoặc từ Cấp Thành phố lên Cấp Quốc gia và Thị trường lớn.

```sql
-- OLAP 01: Roll-up từ Tháng -> Quý -> Năm và từ Quốc gia -> Thị trường
SELECT 
    d.year,
    d.quarter,
    g.market,
    g.country,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
GROUP BY ROLLUP (d.year, d.quarter, g.market, g.country)
ORDER BY d.year NULLS FIRST, d.quarter NULLS FIRST, g.market NULLS FIRST;
```

---

### 2.2. Thao tác DRILL-DOWN (Chi tiết hóa dữ liệu xuống mức sâu hơn)
*Bài toán:* Nhà quản trị thấy ngành hàng **Technology** có doanh số cao nhưng muốn "khoan sâu" xuống xem từng **Sub-Category** và từng **Mã sản phẩm (Product)** cụ thể xem sản phẩm nào đem lại lợi nhuận, sản phẩm nào bị lỗ.

```sql
-- OLAP 02: Drill-down từ Category -> Sub-Category -> Product Name
SELECT 
    p.category,
    p.sub_category,
    p.product_id,
    p.product_name,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(AVG(f.discount) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE p.category = 'Technology'
GROUP BY p.category, p.sub_category, p.product_id, p.product_name
ORDER BY total_profit ASC -- Tìm ra các sản phẩm lỗ nặng nhất
LIMIT 20;
```

---

### 2.3. Thao tác SLICE (Cắt một lát dữ liệu theo một chiều cụ thể)
*Bài toán:* Cố định một chiều phân tích cụ thể (ví dụ: chỉ quan sát năm **2014** hoặc chỉ quan sát thị trường **APAC**).

```sql
-- OLAP 03: Slice cố định thị trường 'APAC' trong năm 2014
SELECT 
    d.month_name,
    p.category,
    ROUND(SUM(f.sales), 2) AS apac_sales,
    ROUND(SUM(f.profit), 2) AS apac_profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE g.market = 'APAC' AND d.year = 2014
GROUP BY d.month, d.month_name, p.category
ORDER BY d.month, p.category;
```

---

### 2.4. Thao tác DICE (Cắt một khối lập phương con - Đa điều kiện)
*Bài toán:* Lọc dữ liệu thỏa mãn nhiều khoảng giá trị trên các chiều: Chỉ lấy thị trường thuộc `('APAC', 'EU')`, danh mục thuộc `('Furniture', 'Technology')` và trong các quý cuối năm `(Q3, Q4)` của năm `2014`.

```sql
-- OLAP 04: Dice khối dữ liệu đa chiều
SELECT 
    g.market,
    p.category,
    d.quarter,
    ROUND(SUM(f.sales), 2) AS diced_sales,
    ROUND(SUM(f.profit), 2) AS diced_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE g.market IN ('APAC', 'EU')
  AND p.category IN ('Furniture', 'Technology')
  AND d.year = 2014
  AND d.quarter IN (3, 4)
GROUP BY g.market, p.category, d.quarter
ORDER BY g.market, p.category, d.quarter;
```

---

### 2.5. Thao tác PIVOT (Xoay chiều dữ liệu / Cross-Tabulation)
*Bài toán:* Chuyển đổi các quý trong năm thành các cột ngang để so sánh trực diện doanh số của từng Phân nhóm sản phẩm (`Sub-Category`).

```sql
-- OLAP 05: Pivot doanh thu theo từng Quý của năm 2014
SELECT 
    p.sub_category,
    ROUND(SUM(CASE WHEN d.quarter = 1 THEN f.sales ELSE 0 END), 2) AS q1_sales,
    ROUND(SUM(CASE WHEN d.quarter = 2 THEN f.sales ELSE 0 END), 2) AS q2_sales,
    ROUND(SUM(CASE WHEN d.quarter = 3 THEN f.sales ELSE 0 END), 2) AS q3_sales,
    ROUND(SUM(CASE WHEN d.quarter = 4 THEN f.sales ELSE 0 END), 2) AS q4_sales,
    ROUND(SUM(f.sales), 2) AS total_year_sales
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE d.year = 2014
GROUP BY p.sub_category
ORDER BY total_year_sales DESC;
```

---

## 3. CÁC PHÉP PHÂN TÍCH OLAP NÂNG CAO (WINDOW FUNCTIONS & DATA CUBE)

### 3.1. Phân tích Tốc độ Tăng trưởng Doanh thu theo tháng (MoM Growth Rate)
```sql
-- OLAP 06: Tính Tăng trưởng MoM bằng LAG() Window Function
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        d.year_month,
        SUM(f.sales) AS current_sales
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    GROUP BY d.year, d.month, d.year_month
)
SELECT 
    year_month,
    ROUND(current_sales, 2) AS sales,
    ROUND(LAG(current_sales, 1) OVER (ORDER BY year, month), 2) AS prev_month_sales,
    ROUND(
        (current_sales - LAG(current_sales, 1) OVER (ORDER BY year, month)) 
        / NULLIF(LAG(current_sales, 1) OVER (ORDER BY year, month), 0) * 100, 
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY year, month;
```

---

### 3.2. Xếp hạng Top 5 Sản phẩm bán chạy nhất trong từng Ngành hàng
```sql
-- OLAP 07: DENSE_RANK() theo từng Category
WITH ranked_products AS (
    SELECT 
        p.category,
        p.product_name,
        ROUND(SUM(f.sales), 2) AS total_sales,
        ROUND(SUM(f.profit), 2) AS total_profit,
        DENSE_RANK() OVER (
            PARTITION BY p.category 
            ORDER BY SUM(f.sales) DESC
        ) AS sales_rank
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    GROUP BY p.category, p.product_name
)
SELECT * FROM ranked_products
WHERE sales_rank <= 5
ORDER BY category, sales_rank;
```

---

### 3.3. Phân tích Đa chiều toàn diện với GROUP BY CUBE
*Bài toán:* Tạo ra siêu lập phương tổng hợp dữ liệu tại mọi tổ hợp của `(Year, Category, Market)`.
```sql
-- OLAP 08: GROUP BY CUBE cho phép tính Subtotals và Grand Total tự động
SELECT 
    d.year,
    p.category,
    g.market,
    ROUND(SUM(f.sales), 2) AS sales,
    ROUND(SUM(f.profit), 2) AS profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_product p ON f.product_key = p.product_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
WHERE d.year IN (2013, 2014) AND g.market IN ('APAC', 'EU')
GROUP BY CUBE (d.year, p.category, g.market)
ORDER BY d.year NULLS FIRST, p.category NULLS FIRST, g.market NULLS FIRST;
```

---

## 4. HIỆN THỰC CÁC DATA MARTS BẰNG MATERIALIZED VIEWS

Để đảm bảo hiệu năng tối ưu cho Power BI và DSS Web App, hệ thống xây dựng 3 Materialized Views:

```sql
-- 1. Sales Performance Mart
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.mv_sales_mart AS
SELECT 
    d.year,
    d.quarter,
    d.month,
    d.year_month,
    g.market,
    g.region,
    g.country,
    c.segment,
    COUNT(DISTINCT f.order_id) AS order_count,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(SUM(f.quantity), 0) AS total_units,
    ROUND(AVG(f.discount), 4) AS avg_discount,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_customer c ON f.customer_key = c.customer_key
GROUP BY d.year, d.quarter, d.month, d.year_month, g.market, g.region, g.country, c.segment;

CREATE INDEX IF NOT EXISTS idx_mv_sales_mart_time ON gold.mv_sales_mart(year, month);
CREATE INDEX IF NOT EXISTS idx_mv_sales_mart_geo ON gold.mv_sales_mart(market, country);

-- 2. Product Performance Mart
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.mv_product_mart AS
SELECT 
    p.category,
    p.sub_category,
    p.product_id,
    p.product_name,
    g.market,
    d.year,
    SUM(f.quantity) AS total_quantity,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(AVG(f.discount), 4) AS avg_discount,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_date d ON f.order_date_key = d.date_key
GROUP BY p.category, p.sub_category, p.product_id, p.product_name, g.market, d.year;

-- 3. Customer RFM Mart
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.mv_customer_mart AS
WITH customer_summary AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment,
        MAX(d.full_date) AS last_order_date,
        COUNT(DISTINCT f.order_id) AS frequency,
        ROUND(SUM(f.sales), 2) AS monetary,
        ROUND(SUM(f.profit), 2) AS total_profit
    FROM gold.fact_sales f
    JOIN gold.dim_customer c ON f.customer_key = c.customer_key
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    GROUP BY c.customer_id, c.customer_name, c.segment
)
SELECT 
    customer_id,
    customer_name,
    segment,
    last_order_date,
    ('2015-01-01'::DATE - last_order_date) AS recency_days,
    frequency,
    monetary,
    total_profit,
    ROUND(monetary / NULLIF(frequency, 0), 2) AS avg_order_value
FROM customer_summary;
```
