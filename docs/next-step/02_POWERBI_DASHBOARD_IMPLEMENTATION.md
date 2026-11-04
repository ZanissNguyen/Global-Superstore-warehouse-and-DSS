# KẾ HOẠCH & HƯỚNG DẪN HIỆN THỰC DASHBOARD POWER BI (.PBIX)
## PHÂN HỆ TRỰC QUAN HÓA & BI - CO4031 (HK261)
**Phụ trách:** Trần Đức Phát (BI Engineer)

---

## 1. MỤC TIÊU & BỘ TÀI NGUYÊN ĐÃ CHUẨN BỊ

Nhóm đã xây dựng hoàn chỉnh toàn bộ tài nguyên nền tảng trong thư mục `reports/powerbi/` và `data/powerbi_export/` để việc thiết kế file `.pbix` trên Power BI Desktop diễn ra nhanh chóng, chính xác và đồng nhất:

| Tài nguyên | Vị trí file trong dự án | Mục đích sử dụng |
|---|---|---|
| **Theme Bách Khoa** | [hcmut_theme.json](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/powerbi/hcmut_theme.json) | Tự động đồng bộ bảng màu chuẩn Bách Khoa (`#003366`, `#10B981`, `#EF4444`) cho toàn bộ visuals |
| **Catalog DAX Measures** | [03_DAX_MEASURES.dax](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/powerbi/03_DAX_MEASURES.dax) | 20+ công thức DAX chia 4 nhóm: Doanh thu, Time Intelligence, Cảnh báo rủi ro, Pareto 80/20 |
| **Power Query M Script** | [02_POWER_QUERY_M_SCRIPTS.m](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/powerbi/02_POWER_QUERY_M_SCRIPTS.m) | Kết nối PostgreSQL schema `gold` và `dss` |
| **Đặc tả Visual Layout** | [04_DASHBOARD_LAYOUT_SPEC.md](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/powerbi/04_DASHBOARD_LAYOUT_SPEC.md) | Bản vẽ thiết kế chi tiết từng visual trên 3 trang dashboard |
| **Dữ liệu CSV Export** | `data/powerbi_export/` | 8 file CSV sạch sẵn sàng nạp thẳng vào Power BI nếu không dùng PostgreSQL trực tiếp |

---

## 2. QUY TRÌNH HIỆN THỰC CHI TIẾT TRÊN POWER BI DESKTOP

### Bước 1: Kết nối Nguồn dữ liệu & Nạp Model
1. Mở phần mềm **Power BI Desktop**.
2. Chọn phương thức kết nối:
   - **Cách 1 (Khuyến nghị): Kết nối CSDL PostgreSQL đang chạy trên Docker:**
     - **Server:** `localhost:5432` *(hoặc `localhost:5433` nếu máy bạn đổi cổng)*.
     - **Database:** `global_superstore`.
     - **Mode:** `Import`.
     - Chọn 6 bảng tầng Gold (`fact_sales`, `dim_date`, `dim_customer`, `dim_product`, `dim_geography`, `dim_ship_mode`) và 2 bảng tầng DSS (`association_rule`, `forecast_result`).
   - **Cách 2: Nạp từ thư mục CSV đã xuất:**
     - Chạy lệnh `python -m src.app.export_for_powerbi` để tạo 8 file CSV trong `data/powerbi_export/`.
     - Trong Power BI Desktop, chọn **Get Data** $\to$ **Folder** hoặc **Text/CSV** và nạp 8 file này.

### Bước 2: Cấu hình Quan hệ Mô hình (Model View)
Kiểm tra và nối các quan hệ 1-Nhiều (1 to Many, Single Direction) từ các Dimension sang Fact:
- `dim_date[date_key]` $\xrightarrow{1 : N}$ `fact_sales[order_date_key]` (Active)
- `dim_date[date_key]` $\xrightarrow{1 : N}$ `fact_sales[ship_date_key]` (Inactive)
- `dim_customer[customer_key]` $\xrightarrow{1 : N}$ `fact_sales[customer_key]`
- `dim_product[product_key]` $\xrightarrow{1 : N}$ `fact_sales[product_key]`
- `dim_geography[geography_key]` $\xrightarrow{1 : N}$ `fact_sales[geography_key]`
- `dim_ship_mode[ship_mode_key]` $\xrightarrow{1 : N}$ `fact_sales[ship_mode_key]`

### Bước 3: Áp dụng Theme Bách Khoa
- Trên thanh công cụ, chọn tab **View** $\to$ Mũi tên xổ xuống ở **Themes** $\to$ **Browse for themes...**
- Chọn file: `reports/powerbi/hcmut_theme.json`.

### Bước 4: Tạo bảng chứa Measures (Measure Table)
1. Bấm nút **Enter Data** trên thanh Home, đặt tên bảng là `_All_Measures`.
2. Tạo lần lượt các công thức DAX đã được chuẩn hóa trong file [03_DAX_MEASURES.dax](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/powerbi/03_DAX_MEASURES.dax):
   - `Total Sales`, `Total Profit`, `Profit Margin %`, `Total Orders`, `Average Order Value (AOV)`
   - `Sales YoY Growth %`, `Profit YoY Growth %`, `Sales MoM Growth %`
   - `Negative Profit Orders Count`, `Loss Making Sales`, `Pareto %`

### Bước 5: Thiết kế 3 Trang Báo cáo theo Đặc tả
- **Trang 1: Executive Sales Performance**
  - Thẻ KPI Cards: Sales ($12.64M), Profit ($1.47M), Margin (11.61%), Avg Discount (14.29%).
  - Biểu đồ Clustered Column & Line: Doanh số & Biên lợi nhuận theo từng tháng qua 4 năm.
  - Bản đồ thế giới (Map visual): Bong bóng doanh thu và màu sắc theo tỷ suất lợi nhuận.
- **Trang 2: Product Portfolio & Pareto ABC**
  - Scatter Plot: Trục X (Sales) vs Trục Y (Profit) với 4 góc phần tư định vị 17 ngành hàng.
  - Pareto 80/20 Chart: Chứng minh quy luật 20% ngành hàng mang lại 80% lợi nhuận.
  - Bảng cảnh báo Top 10 sản phẩm gây lỗ nhiều nhất do chiết khấu cao.
- **Trang 3: Customer Segment & Cross-Selling**
  - Donut Chart: Phân khúc khách hàng (Consumer 51.5%, Corporate 30.3%, Home Office 18.2%).
  - Bảng gợi ý bán chéo (Cross-Selling Recommender) trích xuất trực tiếp từ bảng `dss.association_rule`.

### Bước 6: Lưu tệp báo cáo
- Lưu tệp hoàn thiện vào đúng đường dẫn quy định của đồ án:
  `reports/Global_Superstore_BI.pbix`
