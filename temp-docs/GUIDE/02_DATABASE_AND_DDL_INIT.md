# HƯỚNG DẪN 02: KHỞI TẠO CƠ SỞ DỮ LIỆU & DDL (DATABASE INITIALIZATION)

---

## 1. MỤC TIÊU

Khởi tạo cấu trúc hoàn chỉnh của Kho dữ liệu trong PostgreSQL với 4 schema độc lập:
1. `bronze`: Chứa các bảng nạp thô và bảng lưu vết ingestion.
2. `silver`: Chứa bảng dữ liệu đã làm sạch và chuẩn hóa kiểu dữ liệu.
3. `gold`: Chứa mô hình hình sao (Star Schema gồm 1 Fact table và 5 Dimension tables) cùng các Materialized Views.
4. `dss`: Chứa các bảng lưu trữ kết quả chạy mô hình dự báo và khai phá luật kết hợp.

---

## 2. DANH MỤC CÁC SCRIPT DDL TRONG DỰ ÁN

| Đường dẫn file DDL | Trách nhiệm khởi tạo |
|---|---|
| `src/sql/bronze/schema/create_schema.sql` | `CREATE SCHEMA IF NOT EXISTS bronze;` |
| `src/sql/bronze/schema/create_ingestion.sql` | Bảng `bronze.ingestion` (Lưu vết file, hash SHA-256, thời điểm nạp) |
| `src/sql/bronze/schema/create_raw_orders.sql` | Bảng `bronze.raw_orders` (Lưu 24 cột thô kiểu `TEXT`) |
| `src/sql/bronze/schema/create_postal_code.sql` | Bảng `bronze.postal_code` |
| `src/sql/bronze/schema/create_market.sql` | Bảng `bronze.market` |
| `src/sql/silver/schema/create_orders.sql` | `CREATE SCHEMA silver;` và bảng `silver.orders` (Cleaned schema) |
| `src/sql/gold/schema/create_dim_date.sql` | Bảng `gold.dim_date` |
| `src/sql/gold/schema/create_dim_customer.sql` | Bảng `gold.dim_customer` |
| `src/sql/gold/schema/create_dim_product.sql` | Bảng `gold.dim_product` |
| `src/sql/gold/schema/create_dim_geography.sql` | Bảng `gold.dim_geography` |
| `src/sql/gold/schema/create_dim_ship_mode.sql` | Bảng `gold.dim_ship_mode` |
| `src/sql/gold/schema/create_fact_sales.sql` | Bảng `gold.fact_sales` (Grain chi tiết dòng đơn hàng) |
| `src/sql/gold/schema/create_dss_schema.sql` | `CREATE SCHEMA dss;` và các bảng `forecast_run`, `forecast_result`, `association_run`, `association_rule` |

---

## 3. CÁCH THỰC THI KHỞI TẠO DDL

### Cách 1: Sử dụng Script Python tự động (Khuyến nghị)
Nhóm đã tích hợp sẵn script Python khởi tạo toàn bộ cấu trúc CSDL chỉ với một câu lệnh:
```powershell
python -m src.pipeline.cli --init-db
```
Script sẽ tự động đọc từng file DDL theo đúng thứ tự ràng buộc khóa ngoại, in ra log xác nhận tiến trình:
```text
[INFO] Initializing Bronze Schema & Tables... OK
[INFO] Initializing Silver Schema & Tables... OK
[INFO] Initializing Gold Star Schema (Dimensions & Fact)... OK
[INFO] Initializing DSS Schema & Result Tables... OK
[SUCCESS] All Database Schemas and Tables initialized successfully!
```

### Cách 2: Thực thi thủ công qua pgAdmin hoặc DBeaver
1. Mở pgAdmin 4 tại `http://localhost:5050`.
2. Mở cửa sổ **Query Tool** tại CSDL `global_superstore`.
3. Mở và thực thi lần lượt các file SQL theo thứ tự:
   - Bronze DDL -> Silver DDL -> Gold Dimensions DDL -> Gold Fact DDL -> DSS Schema DDL.

---

## 4. KIỂM TRA SAU KHI KHỞI TẠO (VERIFICATION)
Chạy câu truy vấn kiểm tra danh sách các bảng đã được tạo:
```sql
SELECT 
    table_schema, 
    table_name 
FROM information_schema.tables 
WHERE table_schema IN ('bronze', 'silver', 'gold', 'dss')
ORDER BY table_schema, table_name;
```

Kết quả mong đợi gồm đầy đủ các bảng:
- `bronze`: `ingestion`, `market`, `postal_code`, `raw_orders`
- `silver`: `orders`
- `gold`: `dim_customer`, `dim_date`, `dim_geography`, `dim_product`, `dim_ship_mode`, `fact_sales`
- `dss`: `association_rule`, `association_run`, `forecast_result`, `forecast_run`
