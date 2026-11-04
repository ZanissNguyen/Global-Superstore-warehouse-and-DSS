# KẾ HOẠCH & BẢN ĐỐI CHIẾU NỘI DUNG BÁO CÁO TOÀN VĂN (TECHNICAL REPORT)
## PHÂN HỆ BIÊN SOẠN BÁO CÁO - CO4031 (HK261)
**Phụ trách:** Hoàng Giữ Tiến Nhất (Architect) & Trần Đức Phát (Lead Writer)

---

## 1. MỤC TIÊU & CHUẨN MỰC HỌC THUẬT

1. **Chuẩn văn phong kỹ sư Bách Khoa:** Trình bày gãy gọn, khoa học, có luận cứ kỹ thuật và công thức toán học minh chứng cụ thể. Tránh hoàn toàn lối hành văn mơ hồ, chung chung.
2. **Đối chiếu chặt chẽ với Chuẩn đầu ra (Course Learning Outcomes - L.O):** Toàn bộ nội dung báo cáo được thiết kế để bao phủ 100% các tiêu chí chấm điểm từ L.O.1.1 đến L.O.4.2 của môn học.
3. **Độ chính xác tài chính & kỹ thuật:** Tất cả số liệu trích dẫn trong báo cáo (Doanh số $12,642,501.91, Lợi nhuận $1,467,457.29, 51,290 dòng, MAE $14,820, MAPE 4.15%, Lift 315.57) đều trùng khớp 100% với dữ liệu thực tế đang chạy trên PostgreSQL và Python.

---

## 2. VỊ TRÍ TỆP BÁO CÁO BẢN THẢO TRONG DỰ ÁN

Bản nháp toàn văn chi tiết gồm đầy đủ 7 chương đã được biên soạn và lưu tại:
- **Tệp báo cáo toàn văn:** [reports/Bao_Cao_BTL_CO4031_Global_Superstore.md](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/Bao_Cao_BTL_CO4031_Global_Superstore.md)
- **Đề cương phân công:** [reports/todo.md](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/reports/todo.md)

---

## 3. MA TRẬN ĐỐI CHIẾU NỘI DUNG VỚI CHUẨN ĐẦU RA MÔN HỌC (L.O MATRIX)

| Mã Chuẩn đầu ra (L.O) | Yêu cầu chuẩn đầu ra | Chương tương ứng trong Báo cáo | Minh chứng kỹ thuật trong Dự án |
|:---:|---|:---:|---|
| **L.O.1.1** | Phân tích bài toán kinh doanh, xác định hệ thống chỉ số KPI | **Chương 1** | Bảng công thức 15+ KPIs cốt lõi (Sales, Profit, Margin, Discount, AOV, RFM). |
| **L.O.2.1** | Thiết kế mô hình Star Schema, định nghĩa Grain, Fact & Dims | **Chương 2** | Sơ đồ Star Schema 1 Fact 5 Dims, phân tích Grain 1 dòng đơn hàng, SCD Type 1. |
| **L.O.2.2** | Cài đặt và hiện thực CSDL trên hệ quản trị quan hệ | **Chương 2** | 24 file SQL DDL trong `src/sql/` khởi tạo 15 bảng trên PostgreSQL 17 Docker. |
| **L.O.3.1** | Xây dựng quy trình trích xuất, làm sạch và nạp dữ liệu (ETL) | **Chương 3** | Pipeline Medallion tự động (`bronze_to_gold.py`), Change Data Capture (CDC). |
| **L.O.3.2** | Kiểm định tính toàn vẹn và chất lượng dữ liệu kho dữ liệu | **Chương 3** | Suite validation (`silver/validate.py`, `gold/validate.py`) đối soát khớp 100%. |
| **L.O.4.1** | Hiện thực các câu truy vấn phân tích đa chiều (OLAP) & Data Marts | **Chương 4** | 7 câu truy vấn SQL mẫu (Roll-up, Drill-down, Slice, Dice, Pivot, Window, Cube) + 3 Materialized Views (<50ms). |
| **L.O.4.2** | Phân tích, thiết kế và hiện thực thành phần hỗ trợ quyết định (DSS) | **Chương 5** | Chu trình Simon 4 bước, What-If ($e$), Holt-Winters Forecasting, Apriori Association Mining. |

---

## 4. KẾ HOẠCH HOÀN THIỆN XUẤT BẢN FILE PDF (DEADLINE: 12/11/2026)

1. **Bước 1: Chụp ảnh minh chứng thực tế:**
   - Chụp sơ đồ quan hệ trong Model View của Power BI Desktop.
   - Chụp giao diện Streamlit Web App tại 4 tab (KPIs, What-if sliders, Forecast chart, Rules).
   - Chụp log chạy thành công của script nạp gia tăng `demo_incremental.py` và script đối soát `gold/validate.py`.
2. **Bước 2: Định dạng văn bản:**
   - Sử dụng template Word hoặc LaTeX của Trường ĐH Bách Khoa ĐHQG-HCM (Font Times New Roman 13pt, giãn dòng 1.3, căn lề chuẩn 3cm trái - 2cm phải/trên/dưới).
   - Chèn link Video YouTube và mã nguồn Github vào trang bìa.
3. **Bước 3: Xuất file PDF chính thức:**
   - Lưu vào `reports/Bao_Cao_BTL_CO4031_NhomXX.pdf` sẵn sàng đóng gói nộp bài.
