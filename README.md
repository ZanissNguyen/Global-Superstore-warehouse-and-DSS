# Global Superstore Warehouse & DSS

Pipeline `CSV → Bronze → Silver → Gold → DSS` trên PostgreSQL, kèm giao diện Streamlit và REST API FastAPI. Chạy các lệnh dưới đây từ **thư mục gốc repo**.

## Yêu cầu

- Python 3.12, Docker Desktop (Windows) hoặc Docker Engine + Compose plugin (Linux).
- Dataset `dataset/superstore_dataset2011-2015.csv` có sẵn trong repo. Nếu chưa có, đặt file vào đúng đường dẫn này trước khi nạp dữ liệu.

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
python -m src.pipeline.flows.bronze_to_gold --input dataset/superstore_dataset2011-2015.csv
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

Truy cập **http://localhost:8501**. Muốn dùng REST API, mở terminal thứ hai, kích hoạt `.venv` và chạy:

```bash
python -m uvicorn src.app.api.main:app --reload --port 8000
```

## Những lần chạy sau

1. Mở Docker, chạy `docker compose up -d` trong thư mục repo. Dữ liệu PostgreSQL được giữ trong Docker volume `pgdata`.
2. Kích hoạt môi trường: Windows PowerShell `.\.venv\Scripts\Activate.ps1`; Linux `source .venv/bin/activate`.
3. Chạy lại `python -m streamlit run src/app/main.py`; nếu cần API, chạy lệnh `uvicorn` ở trên trong terminal khác. Không cần `--init-db` hoặc nạp lại dataset cũ.
4. Để demo file 500 dòng, dùng tab **Nạp dữ liệu & đối soát** trong UI; chọn file, xem trước rồi bấm **Xử lý dữ liệu và kích hoạt phiên**. Có thể thay file và chạy lại. Hệ thống tạo database ứng viên từ database nền, chạy ETL/DSS và chỉ chuyển UI sang phiên mới sau khi đối soát thành công. Bấm **Quay về dữ liệu nền** để mọi tab đọc lại database ban đầu; thao tác này không xóa phiên demo. Tải lại trang không tự chạy ETL.

Lệnh CLI `python -m src.pipeline.flows.bronze_to_gold --input "<file>"` vẫn dùng cho nạp dữ liệu trực tiếp vào database cấu hình trong `.env`; không dùng lệnh này để chuẩn bị lại demo vì nó cập nhật dữ liệu nền.
Các lần chạy demo tạo database `demo_<mã phiên>` riêng trong cùng PostgreSQL; phiên cũ được giữ để đối chiếu và hiện chưa có chức năng dọn dẹp tự động.

Để dừng UI/API, nhấn `Ctrl+C`; để dừng database, dùng `docker compose stop` (không xóa volume).

## Địa chỉ và endpoint

| Dịch vụ | Địa chỉ |
|---|---|
| Streamlit UI | http://localhost:8501 |
| PostgreSQL từ máy host | `localhost:${DB_PORT}` (mặc định `localhost:5432`), database `${DB_NAME}` |
| pgAdmin | http://localhost:5050; đăng nhập bằng `PGADMIN_EMAIL` / `PGADMIN_PASSWORD` trong `.env` |
| FastAPI / Swagger | http://localhost:8000/docs (chỉ có khi chạy `uvicorn`) |

Trong pgAdmin chạy bằng Docker, đăng ký server với **host `postgres`**, port `5432`, maintenance database và username theo `DB_NAME` / `DB_USER`, password theo `DB_PASSWORD` trong `.env`.

REST API: `GET /api/health/live`, `GET /api/health/ready`, `GET /api/health` (cùng kết quả với `ready`), `GET /api/kpi/summary`, `GET /api/olap/sales-trend`, `POST /api/dss/what-if`, `GET /api/dss/forecast`, `GET /api/dss/association-rules` (base URL: `http://localhost:8000`). `ready` kiểm tra database đang được UI chọn và các bảng Gold; khi chưa sẵn sàng trả HTTP 503. Healthcheck không nạp hay sửa dữ liệu.
