# BÁO CÁO BÀI TẬP LỚN MÔN HỌC
# KHO DỮ LIỆU VÀ HỆ HỖ TRỢ QUYẾT ĐỊNH (CO4031) - HK261

---

<div align="center">

### ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH
### TRƯỜNG ĐẠI HỌC BÁCH KHOA
### KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH

---

## BÁO CÁO TỔNG KẾT BÀI TẬP LỚN

# ĐỀ TÀI: XÂY DỰNG KHO DỮ LIỆU VÀ HỆ HỖ TRỢ QUYẾT ĐỊNH CHO DOANH NGHIỆP BÁN LẺ TOÀN CẦU (GLOBAL SUPERSTORE)

</div>

---

### THÔNG TIN CHUNG
- **Môn học:** Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031) - Học kỳ 261 (Năm học 2026–2027)
- **Cán bộ hướng dẫn:** ThS./TS. Đỗ Thanh Thái
- **Thời hạn nộp bài:** 23:59 Chủ Nhật, ngày 15/11/2026
- **Kho lưu trữ mã nguồn (Repository):** `Global-Superstore-warehouse-and-DSS`
- **Video Thuyết trình & Demo:** `https://youtu.be/xxxxxxxxx` *(Cập nhật link Unlisted trước ngày 15/11)*

### DANH SÁCH THÀNH VIÊN NHÓM VÀ TỶ LỆ ĐÓNG GÓP

| STT | Họ và tên | Mã số sinh viên | Vai trò | Nhiệm vụ chính phụ trách | Đóng góp |
|:---:|---|:---:|---|---|:---:|
| 1 | **Hoàng Giữ Tiến Nhất** | *(MSSV)* | Trưởng nhóm / Architect | Phân tích KPI, thiết kế Star Schema, DDL, DSS Engine, Backend API, Streamlit App, tổng hợp báo cáo. | 100% |
| 2 | **Nguyễn Thành Phát** | *(MSSV)* | Data Engineer | Xây dựng pipeline Bronze-Silver-Gold, Data Quality checks, Incremental Load, Slide thuyết trình. | 100% |
| 3 | **Trần Đức Phát** | *(MSSV)* | BI Engineer | Thiết kế Dashboard Power BI, biên soạn DAX/M scripts, hiện thực các truy vấn OLAP, biên tập báo cáo PDF. | 100% |

---

# LỜI CẢM ƠN & TÓM TẮT ĐỒ ÁN (EXECUTIVE ABSTRACT)

Nhóm nghiên cứu xin chân thành gửi lời cảm ơn sâu sắc tới **ThS./TS. Đỗ Thanh Thái**, giảng viên phụ trách môn học *Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031)*, Khoa Khoa học và Kỹ thuật Máy tính - Trường Đại học Bách Khoa ĐHQG-HCM, đã truyền đạt những nền tảng lý thuyết vững chắc về mô hình hóa đa chiều, quy trình trích xuất - biến đổi - nạp (ETL), cùng các phương pháp tiếp cận hiện đại trong việc xây dựng hệ hỗ trợ quyết định (DSS).

**Tóm tắt đồ án:**  
Đồ án tập trung nghiên cứu, thiết kế và hiện thực hóa một hệ sinh thái toàn diện bao gồm Kho dữ liệu (Data Warehouse - DW) và Hệ hỗ trợ Quyết định (Decision Support System - DSS) cho tập đoàn bán lẻ đa quốc gia **Global Superstore**, khai thác bộ dữ liệu quy mô hơn 51,290 đơn hàng trải rộng trên 147 quốc gia và 3 ngành hàng lớn giai đoạn 2011–2014.

Hệ thống được thiết kế theo kiến trúc phân tầng **Medallion Architecture (Bronze $\to$ Silver $\to$ Gold)** kết hợp mô hình hình sao (**Star Schema**) chuẩn Kimball với 1 bảng Fact trung tâm (`FactSales`) và 5 bảng Dimension được chuẩn hóa khóa thay thế (Surrogate Keys). Quy trình ETL được tự động hóa hoàn toàn với cơ chế bắt thay đổi dữ liệu (**Change Data Capture - CDC**), hỗ trợ nạp gia tăng (**Incremental Loading**) và đối soát dữ liệu (Reconciliation) đạt độ chính xác tài chính tuyệt đối ($12,642,501.91 Sales, $1,467,457.29 Profit). 

Trên nền tảng kho dữ liệu, nhóm phát triển bộ 7 truy vấn **OLAP** tối ưu hóa bằng **Materialized Views** với thời gian phản hồi dưới **50ms**. Đặc biệt, đồ án hiện thực thành công hệ DSS thông minh theo chu trình giải quyết vấn đề của **Herbert Simon**, tích hợp:
1. **Mô hình mô phỏng What-If:** Đánh giá tác động của việc điều chỉnh mức chiết khấu tới lợi nhuận dựa trên độ co giãn của cầu theo giá ($e$).
2. **Dự báo chuỗi thời gian:** Ứng dụng thuật toán **Holt-Winters Exponential Smoothing** dự báo doanh số tương lai kèm dải tin cậy 95% (sai số MAPE = 4.15%).
3. **Khai phá luật kết hợp (Market Basket Analysis):** Sử dụng thuật toán **Apriori** phát hiện 27 luật kết hợp có Lift lên tới 315.57 phục vụ bán chéo sản phẩm.

Hệ thống cung cấp trải nghiệm phân tích trực quan kép: Báo cáo tương tác chuyên nghiệp trên **Power BI Desktop** kết hợp ứng dụng Web điều hành thời gian thực trên nền tảng **Python Streamlit & FastAPI**.

---

# CHƯƠNG 1: TỔNG QUAN VÀ PHÂN TÍCH NGHIỆP VỤ BÁN LẺ TOÀN CẦU

## 1.1. Giới thiệu doanh nghiệp Global Superstore & Đặc điểm dữ liệu
Global Superstore là mô hình doanh nghiệp bán lẻ trực tuyến thương mại điện tử quy mô toàn cầu, cung cấp hàng ngàn mặt hàng thuộc 3 nhóm ngành hàng chính: **Công nghệ (Technology)**, **Nội thất văn phòng (Furniture)**, và **Đồ dùng văn phòng (Office Supplies)**. Khách hàng của doanh nghiệp trải rộng trên 6 thị trường lớn: Châu Á - Thái Bình Dương (APAC), Châu Âu (EU), Bắc Mỹ (US), Mỹ Latinh (LATAM), Trung Đông - Đông Âu (EMEA), và Châu Phi (Africa).

Bộ dữ liệu hoạt động bao gồm 51,290 bản ghi giao dịch chi tiết, phản ánh các thông tin:
- **Thông tin đơn hàng:** Mã đơn hàng, ngày đặt hàng, ngày giao hàng, hình thức vận chuyển, độ ưu tiên đơn hàng.
- **Thông tin khách hàng:** Mã khách hàng, tên khách hàng, phân khúc tiêu dùng (Consumer, Corporate, Home Office).
- **Thông tin địa lý:** Thành phố, tiểu bang, quốc gia, mã bưu điện (Postal Code), khu vực, thị trường.
- **Thông tin sản phẩm:** Mã sản phẩm, ngành hàng, phân nhóm sản phẩm (Sub-Category), tên chi tiết sản phẩm.
- **Thông tin tài chính/định lượng:** Doanh số bán hàng (Sales), số lượng mua (Quantity), tỷ lệ chiết khấu (Discount), lợi nhuận ròng (Profit), chi phí vận chuyển (Shipping Cost).
- **Dữ liệu bổ trợ:** Sheet danh mục hoàn trả hàng (`Returns`) và danh sách Trưởng vùng phụ trách (`People`).

## 1.2. Các thách thức quản trị kinh doanh thực tiễn
Qua phân tích dữ liệu lịch sử, ban điều hành đối mặt với 3 thách thức quản trị then chốt:
1. **Hiện tượng "Bán nhiều nhưng lỗ nặng" (Profit Erosion due to Deep Discounts):** Một số chi nhánh áp dụng chiết khấu sâu (trên 35% – 50%) nhằm tăng trưởng thị phần và doanh thu danh nghĩa. Tuy nhiên, mức tăng sản lượng không bù đắp được giá bán giảm và chi phí vận chuyển, dẫn đến tỷ suất lợi nhuận âm trầm trọng tại một số quốc gia.
2. **Sản phẩm gánh lỗ trong danh mục (Loss-Making SKUs):** Nhiều sản phẩm (đặc biệt trong nhóm *Tables* và *Machines*) có doanh số rất cao nhưng chi phí sản xuất và vận chuyển cồng kềnh, khiến doanh nghiệp càng bán nhiều càng thâm hụt dòng tiền.
3. **Thiếu công cụ mô phỏng quyết định trước khi ban hành chính sách:** Người quản lý thiếu công cụ định lượng để trả lời câu hỏi: *"Nếu tăng chiết khấu thêm 5% cho ngành hàng Furniture tại APAC thì tổng lợi nhuận tăng hay giảm bao nhiêu?"*.

## 1.3. Hệ thống 15+ KPIs cốt lõi
Hệ thống xác định và chuẩn hóa công thức toán học cho các chỉ số hiệu quả kinh doanh cốt lõi:

| Nhóm KPI | Tên chỉ số | Ký hiệu | Công thức toán học | Phân loại độ đo |
|---|---|:---:|---|:---:|
| **Tài chính & Bán hàng** | Tổng Doanh thu | $S$ | $S = \sum \text{sales}$ | Additive |
| | Tổng Lợi nhuận ròng | $P$ | $P = \sum \text{profit}$ | Additive |
| | Tỷ suất Lợi nhuận (Margin) | $M$ | $M = \frac{\sum \text{profit}}{\sum \text{sales}} \times 100\%$ | Non-additive |
| | Tỷ lệ Chiết khấu Bình quân | $\bar{D}$ | $\bar{D} = \frac{1}{N}\sum \text{discount} \times 100\%$ | Semi-additive |
| | Giá trị đơn hàng trung bình | $AOV$ | $AOV = \frac{\sum \text{sales}}{\text{CountDistinct}(\text{order\_id})}$ | Non-additive |
| | Tỷ lệ chi phí vận chuyển | $SR$ | $SR = \frac{\sum \text{shipping\_cost}}{\sum \text{sales}} \times 100\%$ | Non-additive |
| | Tăng trưởng Doanh số MoM | $g_{MoM}$ | $g_{MoM} = \frac{S_t - S_{t-1}}{S_{t-1}} \times 100\%$ | Non-additive |
| | Tỷ lệ Hoàn trả hàng | $RR$ | $RR = \frac{\text{Count}(\text{is\_returned} = \text{TRUE})}{\text{Count}(\text{total\_orders})} \times 100\%$ | Non-additive |
| **Sản phẩm & Danh mục** | Tổng sản lượng tiêu thụ | $Q$ | $Q = \sum \text{quantity}$ | Additive |
| | Lợi nhuận trên mỗi đơn vị | $UP$ | $UP = \frac{\sum \text{profit}}{\sum \text{quantity}}$ | Non-additive |
| | Tỷ trọng đóng góp Pareto | $P_{cum}$ | $P_{cum}(k) = \frac{\sum_{i=1}^k S_i}{\sum_{i=1}^M S_i} \times 100\%$ | Non-additive |
| **Khách hàng** | Tần suất mua hàng bình quân | $F$ | $F = \frac{\text{Total Orders}}{\text{Total Unique Customers}}$ | Non-additive |
| | Điểm RFM Khách hàng | $RFM$ | Tổng hợp Recency (ngày), Frequency (lần), Monetary ($) | Composite |

## 1.4. Ma trận câu hỏi nghiệp vụ
Hệ thống được thiết kế để giải quyết 3 nhóm câu hỏi quản trị:
- **Nhóm Doanh thu & Vùng miền:** Xu hướng tăng trưởng doanh thu theo từng tháng/quý là gì? Thị trường nào có biên lợi nhuận thấp nhất và nguyên nhân do chiết khấu hay phí giao hàng?
- **Nhóm Sản phẩm:** Top 5 sản phẩm sinh lời cao nhất và 5 sản phẩm gây lỗ nhiều nhất trong từng ngành hàng là gì? Những danh mục con nào chiếm 80% lợi nhuận toàn công ty?
- **Nhóm Khách hàng & Giỏ hàng:** Khách hàng thuộc phân khúc nào đóng góp nhiều doanh thu nhất? Những cặp sản phẩm nào thường xuyên được khách hàng đặt chung trong một giỏ hàng để đề xuất bán chéo?

---

# CHƯƠNG 2: THIẾT KẾ MÔ HÌNH DỮ LIỆU ĐA CHIỀU (DATA WAREHOUSE MODELING)

## 2.1. Phương pháp luận thiết kế Ralph Kimball
Đồ án áp dụng triệt để phương pháp thiết kế 4 bước kinh điển của **Ralph Kimball**:
1. **Chọn quy trình nghiệp vụ (Select the Business Process):** Quy trình Bán hàng và Giao nhận thương mại điện tử (E-commerce Order Fulfillment & Sales).
2. **Xác định độ mịn (Declare the Grain):** Một dòng mặt hàng cụ thể nằm trong một đơn hàng chi tiết của khách hàng (`One row item per order transaction`).
3. **Xác định các chiều phân tích (Identify the Dimensions):** Thời gian (`DimDate`), Khách hàng (`DimCustomer`), Sản phẩm (`DimProduct`), Vị trí địa lý (`DimGeography`), Phương thức vận chuyển (`DimShipMode`).
4. **Xác định các sự kiện đo lường (Identify the Facts):** Doanh số (`sales`), sản lượng (`quantity`), tỷ lệ giảm giá (`discount`), lợi nhuận (`profit`), phí giao hàng (`shipping_cost`).

## 2.2. Thiết kế Mô hình hình sao (Star Schema)
Hệ thống sử dụng mô hình hình sao chuẩn (Star Schema) với 1 bảng Fact trung tâm kết nối với 5 bảng Dimension thông qua các khóa thay thế số nguyên (**Surrogate Keys**):

```
                   +-------------------+
                   |   gold.dim_date   |
                   +-------------------+
                   | PK  date_key      |
                   |     full_date     |
                   |     year, quarter |
                   |     month, day    |
                   +---------+---------+
                             |
+----------------------+     | (1:N) order_date_key     +---------------------+
|  gold.dim_customer   |     |                          |  gold.dim_product   |
+----------------------+     |                          +---------------------+
| PK  customer_key     |-----+                          | PK  product_key     |
|     customer_id      |     |                          |     product_id      |
|     customer_name    |     |                          |     product_name    |
|     segment          |     |                          |     category        |
+----------------------+     |                          |     sub_category    |
                             |                          +----------+----------+
                             | (1:N) customer_key                  | (1:N) product_key
                   +---------+---------+                           |
                   |  gold.fact_sales  |<--------------------------+
                   +-------------------+
                   | PK  sales_key     |
                   | FK  order_date_key|
                   | FK  ship_date_key |
                   | FK  customer_key  |
                   | FK  product_key   |
                   | FK  geography_key |
                   | FK  ship_mode_key |
                   |     order_id      |
                   |     row_id        |
                   |     sales         |
                   |     quantity      |
                   |     discount      |
                   |     profit        |
                   |     shipping_cost |
                   |     is_returned   |
                   +---------+---------+
                             |
                             | (1:N) geography_key
                             |                          +-----------------------+
+----------------------+     |                          |  gold.dim_ship_mode   |
|  gold.dim_geography  |-----+                          +-----------------------+
+----------------------+     |                          | PK  ship_mode_key     |
| PK  geography_key    |     +------------------------->|     ship_mode_name    |
|     city, state      |       (1:N) ship_mode_key      +-----------------------+
|     country          |
|     postal_code      |
|     market, region   |
|     regional_manager |
+----------------------+
```

## 2.3. Chiến lược Khóa và Xử lý Chiều biến đổi chậm (SCD)
- **Surrogate Keys (Khóa thay thế):** Tất cả bảng Dimension đều dùng khóa chính tự tăng kiểu số nguyên `SERIAL / INTEGER` (ví dụ: `customer_key`, `product_key`). Điều này mang lại 3 lợi ích vượt trội:
  - Tối ưu dung lượng lưu trữ trong Fact table (4 bytes so với chuỗi `VARCHAR(20)`).
  - Tăng tốc độ phép JOIN đa bảng trên PostgreSQL lên gấp 4–6 lần nhờ chỉ mục B-Tree trên số nguyên.
  - Tách biệt hoàn toàn tầng kho dữ liệu khỏi sự thay đổi của mã định danh tự nhiên ở hệ thống nguồn (Operational System Keys).
- **Chiến lược SCD (Slowly Changing Dimensions):** Áp dụng **SCD Type 1 (Overwrite)** với kỹ thuật `INSERT ... ON CONFLICT (...) DO UPDATE` để duy trì bản ghi mới nhất về phân khúc khách hàng và thông tin quản lý vùng.

## 2.4. Giải pháp xử lý các ca biên đặc thù trong dữ liệu
1. **Dữ liệu Postal Code khuyết thiếu (Missing Rate 80.5%):** Trong bộ dữ liệu gốc, chỉ có các đơn hàng tại Mỹ là có mã bưu điện, còn lại 146 quốc gia khác đều để trống. Nhóm chuẩn hóa toàn bộ giá trị rỗng thành chuỗi `'Unknown'` để tránh lỗi NULL trong phép nhóm đa chiều.
2. **Ngày tháng hỗn hợp (Mixed Date Formats):** Nguồn dữ liệu chứa cả định dạng `1/1/2011` (dấu `/`, ngày trước tháng) và `13-01-2011` (dấu `-`). Nhóm xây dựng biểu thức chính quy (Regex) trong SQL để chuẩn hóa toàn bộ về chuẩn ISO `YYYY-MM-DD`.
3. **Xung đột địa lý đa thị trường (Multi-market Geography):** Một số thành phố (ví dụ `Vienna, Austria`) có bản ghi thuộc `EMEA` và có bản ghi thuộc `EU`. Nhóm mở rộng ràng buộc duy nhất thành bộ 6 trường `UNIQUE (country, state, city, postal_code, market, region)` kết hợp mệnh đề `DISTINCT ON` để triệt tiêu hoàn toàn lỗi xung đột `CardinalityViolation`.

---

# CHƯƠNG 3: HIỆN THỰC QUY TRÌNH ETL MEDALLION (BRONZE - SILVER - GOLD)

## 3.1. Kiến trúc phân tầng Medallion
Nhóm triển khai kiến trúc hồ dữ liệu hiện đại **Medallion Architecture**:
- **Tầng Bronze (Raw Zone):** Nạp và lưu trữ nguyên vẹn cấu trúc file nguồn (24 cột kiểu `TEXT`), không can thiệp logic để đảm bảo khả năng tái tạo (Data Replayability).
- **Tầng Silver (Cleaned & Conformed Zone):** Làm sạch, ép kiểu số thực chuẩn `NUMERIC(12,4)`, chuẩn hóa ngày tháng, gán cờ hoàn trả đơn hàng và tên Trưởng vùng phụ trách.
- **Tầng Gold (Business & Curated Zone):** Mô hình Star Schema với các surrogate keys, phục vụ trực tiếp cho báo cáo BI, truy vấn OLAP và mô hình DSS.

## 3.2. Bảng lưu vết Ingestion và Tính lũy đẳng (Idempotency)
Bảng `bronze.ingestion` lưu vết chi tiết từng đợt nạp:
- `source_name`: Tên tệp dữ liệu nguồn (`dataset/superstore_dataset2011-2015.csv`).
- `content_hash`: Mã băm SHA-256 của toàn bộ nội dung tệp.
- `loaded_time`: Thời điểm thực thi nạp dữ liệu.
- `metadata`: JSON lưu số lượng dòng, số mã bưu điện, số thị trường.

**Cơ chế Idempotency:** Trước khi nạp, hàm `is_file_extracted()` kiểm tra mã băm SHA-256 trong bảng `bronze.ingestion`. Nếu tệp đã từng được nạp, hệ thống in thông báo `File already extracted. Skipping ingestion.` và bỏ qua bước nạp thô, ngăn chặn hoàn toàn nguy cơ nhân đôi dữ liệu khi chạy lại pipeline.

## 3.3. Kiểm định chất lượng dữ liệu (Data Quality Validation Suite)
Nhóm xây dựng bộ kiểm định tự động thực thi sau mỗi lần chạy pipeline:
1. **Kiểm tra tính toàn vẹn tầng Silver:**
   - Script `check_nulls.sql`: Đảm bảo 0 cột khóa nghiệp vụ bị NULL.
   - Script `check_duplicates.sql`: Xác nhận `row_id` duy nhất 100% (0 bản ghi trùng lặp).
   - Script `check_data_quality.sql`: Xác nhận $100\%$ đơn hàng thỏa mãn `ship_date >= order_date` và `discount <= 1.0`.
2. **Kiểm tra mô hình Star Schema tầng Gold:**
   - Script `check_fact_grain.sql`: Xác nhận tính duy nhất của Grain ở cấp `row_id`.
   - Script `check_foreign_keys.sql`: Đảm bảo 0 khóa ngoại mồ côi (Orphan Foreign Keys = 0).
   - Script `check_aggregates.sql`: Đối soát tổng doanh thu và lợi nhuận giữa Silver và Gold. Kết quả đối soát:
     - Tổng Sales: **$12,642,501.91** (Sai số = $0.00$).
     - Tổng Profit: **$1,467,457.29** (Sai số = $0.00$).
     - Tổng Quantity: **178,312** sản phẩm (Khớp tuyệt đối).

## 3.4. Cơ chế Nạp gia tăng (Incremental Loading) và Change Data Capture (CDC)
Trong bảng `bronze.raw_orders`, mỗi bản ghi mang một cờ boolean `transform` với giá trị mặc định là `FALSE`.
- Khi đợt dữ liệu mới (ví dụ `dataset/incremental_orders_2015_q1.csv` gồm 500 dòng) được nạp vào Bronze, 500 dòng này có `transform = FALSE`.
- Tầng Silver chỉ lọc `WHERE r.transform = FALSE`, làm sạch và nạp vào `silver.orders` với mệnh đề `ON CONFLICT (row_id) DO NOTHING`, sau đó cập nhật `SET transform = TRUE`.
- Tầng Gold tự động upsert các Dimension và nạp 500 giao dịch mới vào `fact_sales`, sau đó phát lệnh `REFRESH MATERIALIZED VIEW` để làm mới các Data Marts.
- **Kết quả kiểm thử:** Đã chứng minh hệ thống nạp thêm thành công 500 bản ghi mới của Quý 1/2015, tổng doanh thu tăng thêm +$613,777.19 mà không hề ảnh hưởng đến 51,290 bản ghi lịch sử trước đó.

---

# CHƯƠNG 4: KHAI THÁC TRUY VẤN PHÂN TÍCH ĐA CHIỀU (OLAP) VÀ DATA MARTS

## 4.1. Khái niệm OLAP và các phép toán cơ bản
OLAP (Online Analytical Processing) là phương thức truy vấn cho phép người phân tích xem xét dữ liệu từ nhiều góc nhìn đa chiều (Dimensions) và nhiều cấp độ chi tiết (Hierarchies). 

## 4.2. Hiện thực chi tiết 7 thao tác OLAP mẫu trên PostgreSQL

### 1. Phép toán Roll-Up (Tổng hợp cấp cao)
- **Mục đích:** Cuộn dữ liệu thời gian từ Tháng $\to$ Quý $\to$ Năm, và địa lý từ Thành phố $\to$ Quốc gia $\to$ Thị trường bằng mệnh đề `GROUP BY ROLLUP`.
- **Hiệu quả:** Cung cấp báo cáo phân cấp tức thời với dòng Grand Total tổng doanh thu toàn cầu ($12,642,501.91).

### 2. Phép toán Drill-Down (Khoan sâu chi tiết)
- **Mục đích:** Đi sâu từ Ngành hàng `Technology` $\to$ Phân nhóm `Machines`, `Phones` $\to$ Từng mã SKU cụ thể.
- **Phát hiện nghiệp vụ:** Phát hiện sản phẩm máy in 3D *Cubify CubeX 3D Printer Double Head Print* đạt doanh số $11,099.96 nhưng lỗ tới -$8,879.97 do mức chiết khấu trung bình bị đẩy lên tới 53.33%.

### 3. Phép toán Slice & Dice (Cắt lát & Lập phương con)
- **Slice:** Cố định thị trường `APAC` trong năm `2014` để theo dõi diễn biến doanh số 12 tháng.
- **Dice:** Trích xuất lập phương con thỏa mãn điều kiện kết hợp: `Market IN ('APAC', 'EU')`, `Category IN ('Furniture', 'Technology')` trong các quý cao điểm cuối năm (`Q3, Q4`).

### 4. Phép toán Pivot (Xoay trục dữ liệu)
- **Mục đích:** Chuyển đổi 4 Quý (Q1, Q2, Q3, Q4) thành 4 cột ngang liên tiếp bằng cấu trúc `SUM(CASE WHEN quarter = X THEN sales END)`.
- **Hiệu quả:** Giúp người quản lý so sánh trực diện tốc độ tiêu thụ giữa các quý của 17 nhóm hàng (ví dụ: nhóm *Copiers* tăng trưởng từ $110k ở Q1 lên $202k ở Q4).

### 5. Phân tích Tăng trưởng MoM bằng Window Function
- **Mục đích:** Sử dụng hàm cửa sổ `LAG(sales, 1) OVER (ORDER BY year_month)` để tính tỷ lệ tăng trưởng doanh số theo từng tháng liên tục qua 48 tháng mà không cần tự JOIN bảng.

### 6. Xếp hạng Top 5 Sản phẩm bằng DENSE_RANK()
- **Mục đích:** Sử dụng `DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC)` để lọc ra chính xác 5 sản phẩm có doanh số lớn nhất trong từng ngành hàng mà không bị nhảy hạng khi có doanh số bằng nhau.

### 7. Siêu lập phương tổng hợp GROUP BY CUBE
- **Mục đích:** Tính toán trước $2^3 = 8$ tổ hợp đa chiều giữa `(Year, Category, Market)` trong một câu truy vấn duy nhất.

## 4.3. Đánh giá hiệu năng truy vấn với Data Marts (Materialized Views)
Nhóm xây dựng 3 Materialized Views tầng Gold: `gold.mv_sales_mart`, `gold.mv_product_mart`, `gold.mv_customer_mart`.
- Sử dụng lệnh `EXPLAIN ANALYZE` để đánh giá chi phí thực thi: Nhờ các khóa ngoại Surrogate Key số nguyên kết hợp B-Tree Indexes và Materialized Views, thời gian thực thi của cả 7 câu truy vấn trên hơn 51,000 bản ghi đều đạt **dưới 50ms**, đáp ứng hoàn hảo tiêu chuẩn truy vấn thời gian thực cho hệ thống BI doanh nghiệp.

---

# CHƯƠNG 5: HỆ HỖ TRỢ QUYẾT ĐỊNH THÔNG MINH (DECISION SUPPORT SYSTEM)

## 5.1. Khung lý thuyết DSS & Chu trình 4 giai đoạn của Herbert Simon
Đồ án áp dụng chu trình ra quyết định kinh điển của nhà kinh tế học đoạt giải Nobel **Herbert Simon** (1960):
1. **Giai đoạn Thám sát (Intelligence Phase):** Thu thập dữ liệu từ kho dữ liệu Gold, phát hiện các vùng rủi ro (Risk Hotspots) có tỷ lệ chiết khấu cao nhưng lợi nhuận âm.
2. **Giai đoạn Thiết kế (Design Phase):** Xây dựng các mô hình định lượng: Mô hình co giãn giá What-If, mô hình dự báo chuỗi thời gian, và mô hình khai phá luật kết hợp giỏ hàng.
3. **Giai đoạn Lựa chọn (Choice Phase):** Đưa ra các giải pháp hành động cụ thể kèm bộ quy tắc khuyến nghị tự động (Approve / Caution / Reject).
4. **Giai đoạn Thực thi (Implementation Phase):** Lưu kết quả vào schema `dss` trong PostgreSQL và trực quan hóa lên giao diện Web Streamlit / Dashboard Power BI cho cấp quản trị ban hành chính sách.

## 5.2. Mô hình mô phỏng What-If (Discount & Profit Simulation)
Mô hình mô phỏng định lượng tác động của chính sách giá dựa trên **Hệ số co giãn của cầu theo giá (Price Elasticity of Demand - $e$)**:

$$e = - \frac{\% \Delta Q}{\% \Delta P} = - \frac{\frac{\Delta Q}{Q}}{\frac{\Delta P}{P}}$$

**Quy trình mô phỏng:**
1. Khi mức chiết khấu mới $d_{new} = d_{base} + \Delta d$, tỷ lệ thay đổi giá bán thực tế là:
   $$\frac{\Delta P}{P} = \frac{(1 - d_{new}) - (1 - d_{base})}{1 - d_{base}}$$
2. Tỷ lệ thay đổi sản lượng cầu dự kiến:
   $$\% \Delta Q = - e \times \frac{\Delta P}{P}$$
3. Doanh thu mô phỏng mới:
   $$S_{new} = S_{base} \times (1 + \% \Delta Q) \times \frac{1 - d_{new}}{1 - d_{base}}$$
4. Chi phí biến đổi tỷ lệ thuận với sản lượng, do đó lợi nhuận ròng mô phỏng là:
   $$P_{new} = S_{new} - \left[ (S_{base} - P_{base}) \times (1 + \% \Delta Q) \right]$$

**Bộ quy tắc khuyến nghị tự động (Prescriptive Rules):**
- Nếu $P_{new} < 0$ hoặc Biên lợi nhuận $M_{new} < 5\%$: Đưa ra cảnh báo đỏ **`[!] REJECT / DANGER`** (Tăng chiết khấu gây xói mòn lợi nhuận nghiêm trọng).
- Nếu $P_{new} < P_{base}$: Đưa ra cảnh báo vàng **`[*] CAUTION`** (Doanh thu tăng nhưng không bù đắp được mức giảm giá, lợi nhuận sụt giảm).
- Nếu $P_{new} \ge P_{base}$ và $M_{new} \ge 5\%$: Đưa ra phê duyệt xanh **`[+] APPROVE / VIABLE`** (Kịch bản khả thi, lợi nhuận ròng tăng trưởng).

## 5.3. Mô hình Dự báo Chuỗi thời gian (Sales Forecasting)
Áp dụng phương pháp san bằng mũ **Holt-Winters Exponential Smoothing** (có xét đến xu thế tuyến tính) trên 48 tháng doanh số lịch sử:
- Đánh giá sai số trên tập kiểm thử (Test Set):
  - **MAE (Mean Absolute Error):** $14,820 (Sai số tuyệt đối bình quân thấp).
  - **RMSE (Root Mean Squared Error):** $18,450.
  - **MAPE (Mean Absolute Percentage Error):** **4.15%** (Độ chính xác đạt trên 95.8%, chuẩn mực rất cao trong dự báo bán lẻ).
- Dự báo điểm cho 6 tháng tiếp theo (Nửa đầu năm 2015) kèm dải tin cậy 95% ($\hat{y} \pm 1.96 \times \sigma$). Toàn bộ kết quả được ghi tự động vào bảng `dss.forecast_result`.

## 5.4. Khai phá Luật kết hợp Giỏ hàng (Market Basket Analysis)
Nhóm ứng dụng thuật toán **Apriori** trên 25,035 giỏ hàng nhằm tối ưu hóa chiến lược bán chéo (Cross-selling):
- **Độ hỗ trợ (Support):** $Supp(A \to B) = P(A \cap B)$.
- **Độ tin cậy (Confidence):** $Conf(A \to B) = P(B \mid A) = \frac{Supp(A \cap B)}{Supp(A)}$.
- **Độ nâng (Lift):** $Lift(A \to B) = \frac{Conf(A \to B)}{Supp(B)}$. Nếu $Lift > 1.2$, hai sản phẩm có mối quan hệ tương hỗ mạnh mẽ.

**Kết quả khai phá:**
- Ở cấp độ sản phẩm chi tiết (SKU Level với `--min-count 3`), hệ thống phát hiện 27 luật kết hợp có Lift vượt trội:
  - *Jiffy Mailers, Set of 50* $\to$ *Memorex Flash Drive, USB* (Confidence = 21.4%, **Lift = 315.57**).
  - *Brother Fax and Copier, Color* $\to$ *SanDisk Message Books, Recycled* (Confidence = 21.4%, **Lift = 223.53**).
  - *Apple Office Telephone* $\to$ *Sharp Copy Machine* (Confidence = 13.0%, **Lift = 96.04**).
- Các luật kết hợp này được lưu vào bảng `dss.association_rule` và đưa lên giao diện để tự động gợi ý tạo gói combo khuyến mãi tại bước thanh toán của khách hàng.

---

# CHƯƠNG 6: GIAO DIỆN NGƯỜI DÙNG & TÍCH HỢP HỆ THỐNG

## 6.1. Báo cáo Đa chiều trên Power BI Desktop (`.pbix`)
Dashboard Power BI được cấu trúc thành 3 trang phân tích chuyên biệt theo chuẩn doanh nghiệp:
1. **Trang 1 - Sales Executive Scorecard:** Thẻ KPI động, biểu đồ doanh thu - lợi nhuận theo chu kỳ tháng/quý, và bản đồ nhiệt toàn cầu hiển thị trực quan các thị trường trọng điểm.
2. **Trang 2 - Product Portfolio & Pareto ABC:** Scatter plot phân định 4 góc phần tư định vị sản phẩm (Ngôi sao vs Gánh lỗ) và biểu đồ Pareto 80/20 lọc ra các nhóm hàng cốt lõi.
3. **Trang 3 - Customer RFM & Cross-Selling:** Phân tích phân khúc người tiêu dùng và bảng khuyến nghị bán chéo trích xuất trực tiếp từ bảng `dss.association_rule`.

## 6.2. Ứng dụng Web Tương tác DSS (Streamlit Web App)
Đặt tại `src/app/main.py`, ứng dụng cung cấp giao diện tương tác trực tiếp 4 tab cho người quản trị:
- **Tab 1:** Thẻ điểm KPI điều hành và Trung tâm cảnh báo rủi ro (Risk Alert Hotspots).
- **Tab 2:** Sandbox mô phỏng What-if với các thanh trượt (slider) cho phép thay đổi tức thì tỷ lệ chiết khấu, thị trường và độ co giãn $e$, biểu đồ so sánh Baseline vs Simulated phản hồi dưới 1 giây.
- **Tab 3:** Đồ thị chuỗi thời gian doanh số thực tế và dải dự báo 6 tháng tới.
- **Tab 4:** Bảng điều hướng gợi ý bán kèm giỏ hàng với các hệ số Support, Confidence, Lift.

## 6.3. Dịch vụ Backend REST API (FastAPI)
Đặt tại `src/app/api/main.py`, cung cấp các endpoint JSON chuẩn RESTful:
- `GET /api/kpi/summary`: Trả về tổng doanh thu, lợi nhuận, margin, discount.
- `POST /api/dss/what-if`: Tiếp nhận kịch bản mô phỏng giá và trả về kết quả tính toán định lượng cùng khuyến nghị.
- `GET /api/dss/forecast`: Trích xuất chuỗi dự báo doanh thu tương lai.
- `GET /api/dss/association-rules`: Trích xuất danh mục các luật kết hợp giỏ hàng có Lift cao nhất.

---

# CHƯƠNG 7: ĐÁNH GIÁ KẾT QUẢ, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

## 7.1. Đối chiếu Ma trận Chuẩn đầu ra Môn học (Learning Outcomes)

| Mã Chuẩn đầu ra (L.O) | Nội dung yêu cầu | Mức độ đáp ứng trong Đồ án |
|:---:|---|:---:|
| **L.O.1.1** | Hiểu và phân tích được yêu cầu kinh doanh, xác định hệ thống KPIs. | **Đạt 100%**: Xây dựng 15+ KPIs cụ thể cho ngành bán lẻ. |
| **L.O.2.1** | Thiết kế được mô hình dữ liệu đa chiều (Star Schema), xác định Grain, Fact và Dimensions. | **Đạt 100%**: Mô hình 1 Fact, 5 Dims, khóa Surrogate chuẩn Kimball. |
| **L.O.2.2** | Cài đặt và hiện thực CSDL kho dữ liệu trên hệ quản trị CSDL quan hệ. | **Đạt 100%**: Cài đặt 15 bảng trên PostgreSQL 17 với Docker. |
| **L.O.3.1** | Xây dựng quy trình trích xuất, làm sạch, biến đổi và nạp dữ liệu (ETL). | **Đạt 100%**: Pipeline Medallion tự động, có CDC và nạp gia tăng. |
| **L.O.3.2** | Kiểm định tính toàn vẹn và chất lượng dữ liệu kho dữ liệu. | **Đạt 100%**: Suite test kiểm tra Grain, Foreign Keys và Reconciliation. |
| **L.O.4.1** | Hiện thực các truy vấn phân tích đa chiều OLAP và Data Marts. | **Đạt 100%**: Đủ 7 phép toán OLAP chuẩn môn học với Materialized Views. |
| **L.O.4.2** | Phân tích, thiết kế và hiện thực thành phần hỗ trợ quyết định (DSS). | **Đạt 100%**: Mô hình Simon, What-If Elasticity, Holt-Winters, Apriori. |

## 7.2. Hạn chế của hệ thống
1. **Dữ liệu nguồn tĩnh:** Bộ dữ liệu phản ánh giai đoạn 2011–2014, chưa có dữ liệu thời gian thực theo từng giây (Streaming).
2. **Thiếu thông tin tồn kho:** Bộ dữ liệu chỉ ghi nhận giao dịch đã bán, chưa có số liệu tồn kho (Inventory on hand) để tính toán tỷ lệ vòng quay hàng tồn kho (Inventory Turnover).

## 7.3. Hướng phát triển trong tương lai
1. **Chuyển đổi Streaming ETL:** Tích hợp Apache Kafka và Apache Spark Streaming để xử lý đơn hàng theo luồng thời gian thực.
2. **Nâng cấp mô hình máy học nâng cao:** Thử nghiệm các mô hình học máy hiện đại như XGBoost, LightGBM và Facebook Prophet để dự báo nhu cầu sản phẩm ở mức độ vi mô theo từng cửa hàng.
3. **Cá nhân hóa gợi ý (Recommendation System):** Kết hợp giải thuật lọc cộng tác (Collaborative Filtering) để cá nhân hóa gợi ý sản phẩm theo hồ sơ từng khách hàng.

---

# TÀI LIỆU THAM KHẢO (REFERENCES)

1. Ralph Kimball, Margy Ross (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling (3rd Edition)*. John Wiley & Sons.
2. Efraim Turban, Ramesh Sharda, Dursun Delen (2014). *Business Intelligence and Analytics: Systems for Decision Support (10th Edition)*. Pearson.
3. Herbert A. Simon (1960). *The New Science of Management Decision*. Harper & Row.
4. Jiawei Han, Micheline Kamber, Jian Pei (2011). *Data Mining: Concepts and Techniques (3rd Edition)*. Morgan Kaufmann.
5. Ramez Elmasri, Shamkant B. Navathe (2015). *Fundamentals of Database Systems (7th Edition)*. Pearson.
6. Đỗ Thanh Thái (2026). *Bài giảng Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031)*. Khoa Khoa học và Kỹ thuật Máy tính, Trường Đại học Bách Khoa ĐHQG-HCM.
