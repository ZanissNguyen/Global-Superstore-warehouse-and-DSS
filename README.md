# Global Superstore Warehouse & DSS

Pipeline `CSV/Excel → Bronze → Silver → Gold → DSS` trên PostgreSQL, kèm giao diện Streamlit. Chạy các lệnh dưới đây từ **thư mục gốc repo**.

## Yêu cầu

- Python 3.12, Docker Desktop (Windows) hoặc Docker Engine + Compose plugin (Linux).
- Dataset `data/raw/Global_Superstore.xls` có sẵn trong repo. Nếu chưa có, đặt file vào đúng đường dẫn này trước khi nạp dữ liệu.

## Chạy lần đầu

**1. Tạo môi trường Python và cấu hình `.env`.** Nếu chưa có `.env`, sao chép `.env.example`, sau đó đổi `DB_PASSWORD` và `PGADMIN_PASSWORD` thành mật khẩu của bạn. Giữ `DB_HOST=localhost` khi chạy Python trên máy host. Nếu cổng 5432 đã được dùng, đổi `DB_PORT` sang cổng trống (ví dụ `5433`).

Windows PowerShell:

```powershell
Copy-Item .env.example .env
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
```

Linux:

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Nếu đã có `.env`, bỏ qua lệnh sao chép tương ứng. Nếu PowerShell chặn `Activate.ps1`, dùng `.\.venv\Scripts\python.exe` thay cho `python` trong các lệnh tiếp theo.

**2. Khởi động PostgreSQL và pgAdmin.**

```bash
docker compose up -d
docker compose ps
```

Đợi service `postgres` báo `healthy`, rồi chạy lần lượt:

```bash
python -m src.pipeline.cli --init-db
python -m src.pipeline.flows.bronze_to_gold --input data/raw/Global_Superstore.xls
python -m src.dss.predictive.run --target sales --horizon 3
python -m src.dss.predictive.run --target sales --horizon 6
python -m src.dss.association.run --level product --min-count 3
```

Lệnh ETL nạp dữ liệu vào Bronze/Silver/Gold và tạo các materialized view; các lệnh DSS lưu dự báo và luật kết hợp vào schema `dss`.
Có thể kiểm tra trong pgAdmin bằng `SELECT COUNT(*) FROM gold.fact_sales;`, `SELECT COUNT(*) FROM dss.forecast_result;` và `SELECT COUNT(*) FROM dss.association_rule;`.

**3. Mở giao diện.** Chạy trong terminal đang kích hoạt `.venv`:

```bash
python -m streamlit run src/app/main.py
```

Truy cập **http://localhost:8501**.

## Những lần chạy sau

1. Mở Docker, chạy `docker compose up -d` trong thư mục repo. Dữ liệu PostgreSQL được giữ trong Docker volume `pgdata`.
2. Kích hoạt môi trường: Windows PowerShell `.\.venv\Scripts\Activate.ps1`; Linux `source .venv/bin/activate`.
3. Chạy lại `python -m streamlit run src/app/main.py`. Không cần `--init-db` hoặc nạp lại dataset cũ.
4. Để demo nạp dữ liệu (file mẫu 500 dòng; hệ thống không còn giới hạn số dòng), dùng tab **Nạp dữ liệu & đối soát** trong UI; chọn file, xem trước rồi bấm **Xử lý dữ liệu và kích hoạt phiên**. Có thể thay file và chạy lại. Hệ thống tạo database ứng viên từ database nền, chạy ETL/DSS và chỉ chuyển UI sang phiên mới sau khi đối soát thành công. Bấm **Quay về dữ liệu nền** để mọi tab đọc lại database ban đầu; thao tác này không xóa phiên demo. Tải lại trang không tự chạy ETL.

Lệnh CLI `python -m src.pipeline.flows.bronze_to_gold --input "<file>"` vẫn dùng cho nạp dữ liệu trực tiếp vào database cấu hình trong `.env`; không dùng lệnh này để chuẩn bị lại demo vì nó cập nhật dữ liệu nền.
Các lần chạy demo tạo database `demo_<mã phiên>` riêng trong cùng PostgreSQL; phiên cũ được giữ để đối chiếu và hiện chưa có chức năng dọn dẹp tự động.

Để dừng UI, nhấn `Ctrl+C`; để dừng database, dùng `docker compose stop` (không xóa volume).

## Tái lập số liệu báo cáo (REPRODUCE)

Mỗi mục dưới đây tái lập đúng một kết quả/bảng của báo cáo. Chạy từ thư mục gốc repo, **sau khi đã nạp ETL** (mục "Chạy lần đầu") và Docker đang `healthy`.

**1. EDA** — notebook phân tích khám phá dữ liệu:

```bash
jupyter lab src/notebooks/eda.ipynb
```

**2. OLAP** — 7 truy vấn Roll-up, Drill-down, Slice/Dice, Pivot, MoM, Top-N, Cube:

```bash
python -m src.sql.gold.marts.run_olap_suite                   # chạy hết 7 truy vấn OLAP
python -m src.sql.gold.marts.run_olap_suite --check-dashboard # đối soát tổng với truy vấn dashboard
```

**3. DSS Dự báo** — bảng so sánh Holt-Winters với Seasonal naive (backtest 3 fold theo thứ tự thời gian, **`--dry-run` chỉ in metric, không ghi database**):

```bash
python -m src.dss.predictive.run --dry-run                # horizon 6 tháng (mặc định)
python -m src.dss.predictive.run --dry-run --horizon 3    # horizon 3 tháng
```

| Horizon | Mô hình | MAE | RMSE | MAPE % | WMAPE % |
|---|---|---:|---:|---:|---:|
| 6 | Holt-Winters additive (chọn) | 31.060,46 | 48.238,43 | 7,79 | 8,87 |
| 6 | Seasonal naive | 69.307,15 | 82.707,09 | 19,12 | 19,78 |
| 3 | Holt-Winters additive (chọn) | 27.275,03 | 40.727,53 | 7,95 | 8,71 |
| 3 | Seasonal naive | 64.766,79 | 74.728,42 | 20,00 | 20,68 |

**4. DSS Luật kết hợp** — chạy **2 lần** cho 2 cấp (mỗi lần tạo một `association_run` mới):

```bash
# Lần 1 — cấp danh mục con (14 luật)
python -m src.dss.association.run --level sub_category --min-support 0.005 --min-confidence 0.10 --min-lift 1.05

# Lần 2 — cấp sản phẩm SKU (27 luật; dùng ngưỡng mặc định 0.0001 / 0.10 / 1.2)
python -m src.dss.association.run --level product
```

**5. DSS What-If** — mô phỏng APAC × Furniture, thay đổi chiết khấu ±5 điểm phần trăm (baseline lấy từ Gold theo bộ lọc, `e = 1,4`):

```bash
python -m src.dss.what_if.simulate --market APAC --category Furniture --discount 0.05
python -m src.dss.what_if.simulate --market APAC --category Furniture --discount -0.05
```

| Kịch bản | Chiết khấu | Doanh thu (USD) | Lợi nhuận (USD) | Biên LN | Quyết định |
|---|---|---:|---:|---:|---|
| Baseline (2.429 dòng) | 13,82% | 1.343.934,07 | 125.896,15 | 9,37% | tham chiếu |
| Tăng CK +5pp | 18,82% | 1.368.789,75 (+1,85%) | 51.816,18 (−58,84%) | 3,79% | REJECT |
| Giảm CK −5pp | 8,82% | 1.306.411,68 (−2,79%) | 187.309,41 (+48,78%) | 14,34% | APPROVE (+61.413,26) |

What-If là kịch bản giả định, **không ghi kết quả vào Gold**; số liệu dao động nhẹ nếu bộ lọc kỳ/thị trường/ngành hàng trên UI khác đi.

## Địa chỉ và endpoint

| Dịch vụ | Địa chỉ |
|---|---|
| Streamlit UI | http://localhost:8501 |
| PostgreSQL từ máy host | `localhost:${DB_PORT}` (mặc định `localhost:5432`), database `${DB_NAME}` |
| pgAdmin | http://localhost:5050; đăng nhập bằng `PGADMIN_EMAIL` / `PGADMIN_PASSWORD` trong `.env` |

Trong pgAdmin chạy bằng Docker, đăng ký server với **host `postgres`**, port `5432`, maintenance database và username theo `DB_NAME` / `DB_USER`, password theo `DB_PASSWORD` trong `.env`.
