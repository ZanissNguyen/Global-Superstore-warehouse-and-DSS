# KẾ HOẠCH & KỊCH BẢN THỬ NGHIỆM NẠP GIA TĂNG (INCREMENTAL LOADING)
## PHÂN HỆ DATA PIPELINE - CO4031 (HK261)
**Phụ trách:** Nguyễn Thành Phát (Data Engineer) & Hoàng Giữ Tiến Nhất (Architect)

---

## 1. MỤC TIÊU NGHIỆP VỤ & KỸ THUẬT

1. **Chứng minh năng lực vận hành thực tế:** Kho dữ liệu doanh nghiệp không phải là hệ thống tĩnh mà liên tục tiếp nhận các giao dịch mới hàng ngày/hàng tuần. Hệ thống phải có khả năng nạp thêm dữ liệu mới (**Incremental Batch Ingestion**) mà không cần xóa đi nạp lại toàn bộ dữ liệu lịch sử (**Full Reload Avoidance**).
2. **Bảo toàn dữ liệu cũ & Chống trùng lặp:** Đảm bảo 51,290 bản ghi lịch sử (2011–2014) được bảo toàn nguyên vẹn, các bản ghi mới (Quý 1/2015) được gán khóa thay thế (Surrogate Keys) mới và tích hợp trơn tru vào Star Schema.
3. **Cập nhật tức thời Data Marts:** Tự động làm mới 3 Materialized Views (`mv_sales_mart`, `mv_product_mart`, `mv_customer_mart`) ngay sau khi đợt nạp gia tăng hoàn tất.

---

## 2. KIẾN TRÚC VÀ CƠ CHẾ CHANGE DATA CAPTURE (CDC) ĐÃ HIỆN THỰC

### 2.1. Tầng Bronze: Ingestion Audit & Checksum
- Khi một file dữ liệu mới được đưa vào:
  - Hệ thống tính toán mã băm SHA-256 nội dung file.
  - Bảng `bronze.ingestion` sinh mã `id` tự tăng (Batch #2), lưu tên file, thời gian nạp và metadata số dòng.
  - Các dòng đơn hàng mới được nạp vào `bronze.raw_orders` mang cờ `transform = FALSE`.

### 2.2. Tầng Silver: Watermark Processing
- Câu lệnh [transform_orders.sql](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/src/sql/silver/transform/transform_orders.sql) chỉ lọc các bản ghi chưa được chuyển đổi:
  ```sql
  WHERE r.transform = FALSE
  ON CONFLICT (row_id) DO NOTHING;
  ```
- Sau khi nạp thành công vào `silver.orders`, cờ trong Bronze được lật sang `TRUE`:
  ```sql
  UPDATE bronze.raw_orders SET transform = TRUE WHERE transform = FALSE;
  ```

### 2.3. Tầng Gold: SCD Type 1 Upsert & Fact Insertion
- Bảng Dimension sử dụng `ON CONFLICT (...) DO UPDATE` để cập nhật thông tin khách hàng/sản phẩm nếu có thay đổi hoặc tự động thêm khách hàng/sản phẩm mới (SCD Type 1).
- Bảng Fact thực thi `INSERT INTO gold.fact_sales ... ON CONFLICT (row_id) DO NOTHING;` chỉ nạp các đơn hàng mới.
- Phát lệnh tự động làm mới Data Marts: `REFRESH MATERIALIZED VIEW gold.mv_sales_mart;`

---

## 3. DỮ LIỆU THỬ NGHIỆM ĐÃ CHUẨN BỊ

Nhóm đã lập trình script tự động sinh tệp dữ liệu gia tăng:
- **Tệp dữ liệu:** `dataset/incremental_orders_2015_q1.csv`
- **Quy mô:** 500 bản ghi chi tiết đơn hàng thuộc Quý 1 năm 2015.
- **Mã Row ID:** Bắt đầu từ `60001` đến `60500` (tách biệt hoàn toàn với dải 1 đến 51290 của dữ liệu gốc).
- **Tổng doanh số bổ sung:** `$613,777.19`
- **Tổng lợi nhuận bổ sung:** `$138,840.67`

---

## 4. KỊCH BẢN THAO TÁC DEMO TRỰC TIẾP (DEMO RUNBOOK)

Khi thuyết trình trước Giảng viên hoặc Hội đồng phản biện, thành viên chỉ cần mở PowerShell tại thư mục dự án và thực hiện các bước sau:

### Bước 1: Khởi chạy lệnh Demo Tự động
```powershell
python -m src.etl.incremental.demo_incremental
```

### Bước 2: Quan sát và thuyết minh kết quả trên màn hình
Hệ thống sẽ tự động in ra 5 bước đối soát trước - sau trực quan:

```text
=================================================================
   DEMO NẠP GIA TĂNG KHO DỮ LIỆU (INCREMENTAL LOADING DEMO)
   CO4031 - Kho dữ liệu & Hệ hỗ trợ Quyết định | Bách Khoa TP.HCM
=================================================================

[BƯỚC 1: TRẠNG THÁI HIỆN TẠI TRƯỚC KHI NẠP GIA TĂNG]
  - Số đợt Ingestion đã nạp:   1
  - Tổng số dòng Bronze:       51,290
  - Tổng số dòng Silver:       51,290
  - Tổng số dòng FactSales:    51,290
  - Tổng Doanh thu hiện tại:   $12,642,501.91
  - Tổng Lợi nhuận hiện tại:   $1,467,457.29

[BƯỚC 2: TIẾN HÀNH NẠP ĐỢT DỮ LIỆU MỚI: dataset/incremental_orders_2015_q1.csv]
... (Tiến trình ETL Bronze -> Silver -> Gold chạy trong ~1.5 giây) ...

[BƯỚC 3: TRẠNG THÁI SAU KHI NẠP GIA TĂNG]
  - Số đợt Ingestion mới:      2 (Lần nạp mới: #2)
  - Số dòng mới nạp vào Fact:  +500 dòng
  - Tổng số dòng FactSales:    51,790
  - Doanh thu mới bổ sung:     +$613,777.19
  - Tổng Doanh thu mới:        $13,256,279.10
  - Lợi nhuận mới bổ sung:     +$138,840.67
  - Tổng Lợi nhuận mới:        $1,606,297.96

[BƯỚC 4: XÁC MINH TRỰC QUAN DOANH SỐ PHÂN BỔ THEO NĂM TRONG GOLD SCHEMA]
 Năm  Số dòng đơn hàng Doanh thu ($) Lợi nhuận ($) Chiết khấu BQ (%)
2011              8998    2259450.90     248940.81             14.82
2012             10962    2677438.69     307415.28             14.13
2013             13799    3405746.45     406935.23             14.03
2014             17531    4299865.87     504165.97             14.33
2015               500     613777.19     138840.67             13.22

[BƯỚC 5: LỊCH SỬ CÁC ĐỢT NẠP TRONG BẢNG BRONZE.INGESTION]
 id                     source_name         loaded_time                                               metadata
  2  incremental_orders_2015_q1.csv 2026-11-04 23:20:54     {'rows': 500, 'pin_count': 23, 'market_count': 52}
  1 superstore_dataset2011-2015.csv 2026-11-04 22:11:35 {'rows': 51290, 'pin_count': 632, 'market_count': 149}
```

### Bước 3: Lệnh Khôi phục trạng thái gốc (Reset to Baseline)
Sau khi kết thúc phiên demo, để đưa kho dữ liệu về trạng thái ban đầu (51,290 dòng) phục vụ lượt demo tiếp theo:
```powershell
python -m src.etl.incremental.demo_incremental --reset
```
Script sẽ tự động dọn dẹp các dòng thử nghiệm, hoàn nguyên `bronze.ingestion` và làm mới lại các Materialized Views.
