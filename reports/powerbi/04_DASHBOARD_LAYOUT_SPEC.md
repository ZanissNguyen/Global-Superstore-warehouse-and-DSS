# ĐẶC TẢ THIẾT KẾ DASHBOARD POWER BI (POWER BI DASHBOARD LAYOUT SPEC)
## ĐỒ ÁN CO4031 - KHO DỮ LIỆU & HỆ HỖ TRỢ QUYẾT ĐỊNH (HK261)
**Học viện:** Khoa KH&KT Máy Tính - Trường Đại học Bách Khoa ĐHQG-HCM  
**File báo cáo:** `reports/Global_Superstore_BI.pbix`  
**Bộ màu nhận diện:** File theme `reports/powerbi/hcmut_theme.json` (Xanh Bách Khoa `#003366`, Xanh ngọc `#10B981`, Cảnh báo đỏ `#EF4444`).

---

## 1. THIẾT LẬP MÔ HÌNH QUAN HỆ (DATA MODEL RELATIONSHIPS)

Trong cửa sổ **Model View** của Power BI Desktop, cấu hình các mối quan hệ 1-Nhiều (1 to Many, Single direction) từ Dimension sang Fact:
1. `gold dim_date[date_key]` $\xrightarrow{1 : N}$ `gold fact_sales[order_date_key]` (Active Relationship)
2. `gold dim_date[date_key]` $\xrightarrow{1 : N}$ `gold fact_sales[ship_date_key]` (Inactive Relationship - Role Playing)
3. `gold dim_customer[customer_key]` $\xrightarrow{1 : N}$ `gold fact_sales[customer_key]`
4. `gold dim_product[product_key]` $\xrightarrow{1 : N}$ `gold fact_sales[product_key]`
5. `gold dim_geography[geography_key]` $\xrightarrow{1 : N}$ `gold fact_sales[geography_key]`
6. `gold dim_ship_mode[ship_mode_key]` $\xrightarrow{1 : N}$ `gold fact_sales[ship_mode_key]`

---

## 2. TRANG 1: EXECUTIVE SALES PERFORMANCE (TỔNG QUAN HIỆU QUẢ KINH DOANH)

### 2.1. Thanh điều hướng & Bộ lọc (Top Header & Slicers):
- **Tiêu đề:** `GLOBAL SUPERSTORE - EXECUTIVE PERFORMANCE SCORECARD`
- **Slicers:**
  - Slicer 1: `Năm` (`dim_date[year]`) - Dạng Dropdown hoặc Tile (2011, 2012, 2013, 2014, 2015).
  - Slicer 2: `Thị trường` (`dim_geography[market]`) - Horizontal Buttons (APAC, EU, US, LATAM, EMEA, Africa).
  - Slicer 3: `Ngành hàng` (`dim_product[category]`).

### 2.2. Dải thẻ KPI Cards (Top Metrics Banner):
1. **Card 1: Tổng Doanh thu:** Measure `[Total Sales]` (Hiển thị dạng `$12.64M`, kèm chỉ số so sánh `[Sales YoY Growth %]`).
2. **Card 2: Tổng Lợi nhuận:** Measure `[Total Profit]` (Hiển thị dạng `$1.47M`).
3. **Card 3: Biên Lợi nhuận:** Measure `[Profit Margin %]` (Hiển thị `11.61%`, Conditional formatting màu xanh nếu $\ge 12\%$, vàng nếu 5-12%, đỏ nếu $< 5\%$).
4. **Card 4: Chiết khấu Trung bình:** Measure `[Average Discount %]` (Hiển thị `14.29%`).
5. **Card 5: Giá trị đơn trung bình (AOV):** Measure `[Average Order Value (AOV)]` (Hiển thị `$505.00`).

### 2.3. Khu vực biểu đồ phân tích (Analytical Visuals):
- **Visual 1 (Bên trái): Line & Clustered Column Chart:**
  - Trục X: `dim_date[year_month]`
  - Cột (Column): `[Total Sales]`
  - Đường (Line): `[Profit Margin %]`
  - Mục đích: Quan sát tính chu kỳ mùa vụ (Seasonality) tăng vọt vào Quý 3 và Quý 4 hàng năm.
- **Visual 2 (Bên phải): Map Visual (Bản đồ thế giới):**
  - Location: `dim_geography[country]`
  - Bubble Size: `[Total Sales]`
  - Bubble Color: `[Profit Margin %]` (Gradient từ Đỏ $\to$ Vàng $\to$ Xanh lá)
  - Mục đích: Phát hiện ngay các thị trường "Doanh số cao nhưng Lợi nhuận âm" (Risk Hotspots) tại Châu Phi hoặc Trung Đông.

---

## 3. TRANG 2: PRODUCT PORTFOLIO & PARETO ABC (DANH MỤC SẢN PHẨM & RỦI RO)

### 3.1. Dải KPI con:
- Tổng số SKU: `DISTINCTCOUNT(dim_product[product_id])` (~10,292 SKU)
- Số đơn hàng lỗ vốn: Measure `[Negative Profit Orders Count]`
- Doanh thu từ đơn hàng lỗ: Measure `[Loss Making Sales]`

### 3.2. Biểu đồ trọng tâm:
- **Visual 1: Scatter Plot (Ma trận Định vị Sản phẩm):**
  - Trục X: `[Total Sales]`
  - Trục Y: `[Total Profit]`
  - Kích thước bóng (Size): `[Total Quantity]`
  - Chi tiết (Details): `dim_product[sub_category]`
  - Phân vùng 4 góc phần tư:
    - Góc phải trên: *Ngôi sao (High Sales, High Profit)*: Copiers, Phones.
    - Góc phải dưới: *Rủi ro (High Sales, Low/Negative Profit)*: Tables.
- **Visual 2: Pareto 80/20 Chart:**
  - Trục X: `dim_product[sub_category]` sắp xếp giảm dần theo Sales.
  - Cột: `[Total Sales]`
  - Đường: `[Pareto %]`
  - Đường tham chiếu (Constant Line): $80\%$ để minh họa quy luật 20% danh mục đóng góp 80% doanh thu.
- **Visual 3: Matrix Table (Chi tiết Top 10 SKU lỗ nhiều nhất):**
  - Cột: `Product Name`, `Sub-Category`, `Units Sold`, `Total Sales`, `Total Profit`, `Avg Discount %`.

---

## 4. TRANG 3: CUSTOMER ANALYTICS & CROSS-SELLING (PHÂN KHÚC KHÁCH HÀNG & BÁN CHÉO)

### 4.1. Phân khúc Khách hàng:
- **Donut Chart:** Tỷ trọng doanh thu theo Phân khúc (`dim_customer[segment]`): Consumer (51.5%), Corporate (30.3%), Home Office (18.2%).
- **Stacked Bar Chart:** Doanh thu và Lợi nhuận theo `Ship Mode` (Standard Class chiếm 60%, Second Class 20%, First Class 15%, Same Day 5%).

### 4.2. Gợi ý Bán chéo từ Module DSS (Market Basket Recommender):
- **Visual: Table Visual lấy từ bảng `dss.association_rule`:**
  - Cột 1: `antecedent_names` (Sản phẩm khách hàng đang chọn mua)
  - Cột 2: `consequent_names` (Sản phẩm hệ thống đề xuất bán kèm)
  - Cột 3: `support` (Tần suất xuất hiện)
  - Cột 4: `confidence` (Độ tin cậy của gợi ý)
  - Cột 5: `lift` (Độ nâng vượt trội so với ngẫu nhiên - sắp xếp Giảm dần)
  - Cột 6: Gợi ý hành động nghiệp vụ (Ví dụ: Giảm giá combo 10% khi mua kèm phụ kiện).
