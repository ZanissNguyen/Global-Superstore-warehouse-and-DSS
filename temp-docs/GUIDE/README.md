# SỔ TAY HƯỚNG DẪN KHỞI CHẠY DỰ ÁN TOÀN DIỆN (PROJECT EXECUTION GUIDE)
## DỰ ÁN: GLOBAL SUPERSTORE DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
**Môn học:** Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031) - HK261, ĐH Bách Khoa ĐHQG-HCM

---

## 1. TỔNG QUAN HƯỚNG DẪN

Thư mục `temp-docs/GUIDE/` cung cấp tài liệu hướng dẫn từng bước (Step-by-Step) giúp bất kỳ thành viên nào trong nhóm hoặc Giảng viên / Trợ giảng có thể khởi chạy toàn bộ hệ thống từ con số không (Zero to Hero) trên máy tính cá nhân.

### Danh mục các tài liệu hướng dẫn chi tiết:

| Tài liệu | Nội dung hướng dẫn chính |
|---|---|
| [`01_ENVIRONMENT_SETUP.md`](./01_ENVIRONMENT_SETUP.md) | Cài đặt Python 3.12, các thư viện cần thiết (`requirements.txt`), Docker Compose, cấu hình file `.env`, và giải quyết xung đột cổng 5432. |
| [`02_DATABASE_AND_DDL_INIT.md`](./02_DATABASE_AND_DDL_INIT.md) | Khởi tạo CSDL PostgreSQL, tạo các schemas (`bronze`, `silver`, `gold`, `dss`), và thực thi toàn bộ script DDL tạo bảng. |
| [`03_ETL_EXECUTION_GUIDE.md`](./03_ETL_EXECUTION_GUIDE.md) | Chạy pipeline ETL tuần tự: Nạp dữ liệu thô (Bronze), Làm sạch & chuẩn hóa (Silver), Nạp mô hình Star Schema (Gold), và kiểm thử nạp gia tăng (Incremental Loading). |
| [`04_OLAP_AND_MARTS_GUIDE.md`](./04_OLAP_AND_MARTS_GUIDE.md) | Thực thi bộ truy vấn OLAP chuẩn (Roll-up, Drill-down, Slice, Dice, Pivot, Window Functions, Cube) và khởi tạo các Materialized Views (`mv_*_mart`). |
| [`05_DSS_PIPELINE_GUIDE.md`](./05_DSS_PIPELINE_GUIDE.md) | Chạy pipeline học máy và hỗ trợ quyết định: Dự báo doanh thu (Forecasting), Mô phỏng What-if (Discount/Profit), Khai phá luật kết hợp giỏ hàng (Apriori). |
| [`06_DASHBOARD_AND_UI_LAUNCH.md`](./06_DASHBOARD_AND_UI_LAUNCH.md) | Khởi chạy ứng dụng Web DSS tương tác (Streamlit / FastAPI) và kết nối Báo cáo Power BI (.pbix) vào PostgreSQL. |
| [`07_TROUBLESHOOTING.md`](./07_TROUBLESHOOTING.md) | Danh mục mã lỗi thường gặp (Xung đột cổng Docker, lỗi kết nối DB, lỗi mã hóa file CSV latin1/cp1252, lỗi định dạng ngày tháng, lỗi biểu đồ Power BI count = 1, lỗi Apriori 0 rules, lỗi SQL DISTINCT) và cách khắc phục dứt điểm. |
| [**`TỔNG HỢP TOÀN DIỆN HỆ THỐNG & ỨNG DỤNG`**](../../docs/TONG_HOP_TOAN_DIEN_HE_THONG_VA_UNG_DUNG.md) | **Bản tổng hợp hoàn thiện toàn diện về những gì hệ thống làm được, những cái hay/đột phá kỹ thuật, 5 kịch bản ứng dụng thực tiễn trong doanh nghiệp và cẩm nang vận hành.** |

---

## 2. QUY TRÌNH KHỞI CHẠY NHANH (QUICK-START CHEATSHEET)

Nếu môi trường máy tính đã cài đặt sẵn Python và Docker:

```powershell
# Bước 1: Sao chép file môi trường và điền thông tin kết nối
cp .env.example .env

# Bước 2: Cài đặt các thư viện Python
pip install -r requirements.txt

# Bước 3: Khởi động CSDL PostgreSQL và pgAdmin qua Docker
docker compose up -d

# Bước 4: Khởi tạo CSDL và toàn bộ DDL (Bronze, Silver, Gold, DSS)
python -m src.pipeline.cli --init-db

# Bước 5: Chạy quy trình nạp dữ liệu ETL (51k records)
python -m src.pipeline.flows.bronze_to_gold --input "dataset/superstore_dataset2011-2015.csv"

# Bước 6: Chạy Pipeline DSS (Huấn luyện mô hình và lưu kết quả vào PostgreSQL)
python -m src.dss.predictive.run --target sales --horizon 6
python -m src.dss.association.run --level product --min-count 3

# Bước 7: Mở ứng dụng Web DSS tương tác
python -m streamlit run src/app/main.py
```

---

## 3. THÔNG TIN BẢNG DỮ LIỆU & NGUỒN DỮ LIỆU CHUẨN

- File nguồn 51,290 bản ghi chuẩn: `dataset/superstore_dataset2011-2015.csv` (đặt sẵn trong thư mục `dataset/` của dự án).
- File nguồn Excel gốc: `Global Superstore.xls` (Bao gồm 3 sheet: `Orders`, `Returns`, `People`).
- Cấu hình cổng kết nối mặc định:
  - PostgreSQL: `5432` (hoặc `5433` nếu cổng 5432 bị chiếm dụng).
  - pgAdmin 4: `5050` (`http://localhost:5050`).
  - Streamlit Web App: `8501` (`http://localhost:8501`).
  - FastAPI Swagger: `8000` (`http://localhost:8000/docs`).
