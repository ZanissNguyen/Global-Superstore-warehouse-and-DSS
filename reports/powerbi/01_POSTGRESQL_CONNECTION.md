# HƯỚNG DẪN KẾT NỐI POWER BI DESKTOP VỚI KHO DỮ LIỆU POSTGRESQL

## 1. THÔNG SỐ KẾT NỐI CHUẨN

Khi mở Power BI Desktop, vào **Get Data** $\to$ **PostgreSQL database**:

- **Server:** `localhost:5432` *(hoặc `localhost:5433` nếu máy bạn đổi cổng trong file `.env`)*
- **Database:** `global_superstore`
- **Data Connectivity mode:** 
  - Chọn **Import** (Khuyến nghị: Tốc độ render biểu đồ và tính toán hàm DAX Time Intelligence mượt mà nhất).
  - Hoặc **DirectQuery** (Nếu muốn dữ liệu trên dashboard phản chiếu tức thời khi chạy pipeline nạp gia tăng).

## 2. CHỌN CÁC BẢNG NẠP VÀO DATA MODEL

Trong cửa sổ **Navigator**, tích chọn các bảng sau:
- Tầng Gold:
  - `gold.fact_sales`
  - `gold.dim_date`
  - `gold.dim_customer`
  - `gold.dim_product`
  - `gold.dim_geography`
  - `gold.dim_ship_mode`
- Tầng DSS:
  - `dss.association_rule`
  - `dss.forecast_result`

Sau đó bấm nút **Transform Data** để kiểm tra kiểu dữ liệu hoặc bấm **Load** để nạp thẳng vào mô hình.

## 3. THAY ĐỔI THEME VÀ MÀU SẮC NHẬN DIỆN BÁCH KHOA
1. Trên thanh Ribbon Power BI, vào tab **View**.
2. Nhấp vào mũi tên xổ xuống ở mục **Themes**.
3. Chọn **Browse for themes...**
4. Trỏ tới file: `reports/powerbi/hcmut_theme.json`.
5. Toàn bộ bảng màu biểu đồ sẽ tự động chuyển sang phong cách nhận diện chính thống của Trường ĐH Bách Khoa ĐHQG-HCM!
