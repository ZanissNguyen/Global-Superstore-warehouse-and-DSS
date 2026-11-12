# Kế hoạch chuẩn hoá bộ truy vấn OLAP cho trang "Tổng quan kinh doanh"

> **Cập nhật triển khai:** SQL phục vụ UI đã nằm trong `src/sql/gold/dashboard/`
> và được `src/app/executive.py` đọc bằng `read_sql()`. Bảy ví dụ
> `src/sql/gold/marts/olap_*.sql` đã nhận tham số ngày/địa lý;
> `run_olap_suite.py` có `--check-dashboard` để đối chiếu các tổng doanh thu,
> lợi nhuận với KPI. Các ví dụ Pivot, MoM và Cube vẫn không phải chart UI.
> Những phần bên dưới mô tả khảo sát và thiết kế ban đầu; các nhận định rằng
> dashboard còn chứa SQL inline hoặc OLAP mẫu còn hardcode đã cũ.

> **Phạm vi:** chỉ trang tổng quan (`src/app/executive.py`, tab `Tổng quan kinh doanh` trong `src/app/main.py`).
> **Loại trừ:** `whatif.py` (Quyết định giá), `forecast.py` (dự báo), `crosssell.py` (association rule), `upload.py`.
> **Nguồn khảo sát:** `src/app/executive.py`, `src/sql/gold/marts/*.sql`, `src/sql/gold/marts/create_materialized_views.sql`, `src/sql/gold/schema/*`, `src/sql/gold/marts/run_olap_suite.py`.
> **Ngày khảo sát:** 12/11/2026. Database snapshot dùng khi đối chiếu: `global_superstore` (PostgreSQL, `gold` schema).
> **Trạng thái DB lúc viết:** Docker daemon đang tắt → không re-chạy được các câu đối soát live; các mục cần xác minh được đánh dấu ⏳ ở cuối tài liệu.

---

## 0. Tóm tắt kết luận (TL;DR)

| Câu hỏi | Trả lời |
|---|---|
| `marts/` có đủ logic OLAP cho trang tổng quan? | **Không.** Trang tổng quan có **11 logic**; **không logic nào khớp đủ**: 6 logic chỉ khớp **một phần** (L1, L3, L4, L6, L7, L9 — đều thiếu filter kỳ/phạm vi), **5 logic chưa có file nào** (L2, L5, L8, L10, L11). |
| Các file hiện tại có tổng quát hoá (có tham số) không? | **Không.** 7/7 file OLAP đều **hardcode** một action cụ thể (`category='Technology'`, `year=2014`, `market IN ('APAC','EU')`, `LIMIT 20`, `sales_rank <= 5`...) và **không có filter kỳ/phạm vi địa lý**. |
| Dashboard có thể đọc từ materialized view không? | **Chỉ một phần.** Không có logic nào chạy hoàn toàn trên MV với đủ filter của dashboard: **L7** và **một phần L1/L2/L3/L8** dùng được `mv_sales_mart` khi kỳ là **đầu tháng → cuối tháng** (L3 chỉ ở grain Tháng); **L4/L6/L9** chỉ có biến thể `mv_product_mart` (chỉ lọc `year` + `market`, thiếu `region/country`); **L5** chỉ nhánh `market/country`; **L10/L11** phải đọc `dim_*`. Các measure `line_count`, `COUNT(DISTINCT customer_id)`, `order_count` theo ngành hàng và grain **ngày/tuần** bắt buộc đọc `fact_sales`. |
| Việc cần làm | Viết **10 file SQL mục tiêu (Nhóm A)** parameterized cho dashboard + **chuẩn hoá lại 7 file OLAP mẫu (Nhóm B)**; `executive.py` chuyển sang `read_sql(path)` + params; `run_olap_suite.py` truyền params. |

---

## Bước 1 — Xác định các logic OLAP đang có ở dashboard

Tất cả nằm trong `src/app/executive.py`; tham số filter dùng chung kiểu `:start_key`, `:end_key` (INT `YYYYMMDD`), `:market/:region/:country` (`NULL` = Tất cả) — convention `sqlalchemy.text()`.

| ID | Hàm (`executive.py`) | Logic OLAP | Tham số | Measure / output |
|---|---|---|---|---|
| **L1** | `load_period_kpis` (dòng 139) | **SLICE + AGGREGATE** trên một kỳ + phạm vi địa lý | `start_key, end_key, market, region, country` | `line_count, order_count, sales, profit, avg_discount` → 5 thẻ metric |
| **L2** | `load_period_kpis` gọi lại với `prior_year_period` (dòng 442) | **PERIOD COMPARISON / YoY** — tính tăng trưởng giữa 2 kỳ (Python làm phép chia) | cùng L1 với kỳ năm trước | `% YoY` cho doanh thu/lợi nhuận/số đơn; `điểm %` cho biên & chiết khấu |
| **L3** | `load_period_trend` (dòng 163) | **ROLL-UP thời gian** `date_trunc(:grain, ...)` — day / week / month | `start_key, end_key, grain ∈ {day,week,month}, scope` | `period, order_count, sales, profit` → biểu đồ cột + đường |
| **L4** | `load_period_categories` (dòng 185) | **ROLL-UP** theo hierarchy sản phẩm, cấp `category` | `start_key, end_key, scope` | `category, quantity, sales, profit, margin_pct` → bảng + cột nhóm + biểu đồ quạt tỷ trọng |
| **L5** | `load_risk_hotspots` (dòng 206) | **SLICE + GROUP BY + HAVING + BOTTOM-N** — `UNION ALL` 2 cách nhóm | `start_key, end_key, scope`, hằng `>= 3 đơn`, `LIMIT 5` | nhóm `market/country` và `category/sub_category` có `orders>=3 AND profit<0`, sắp `profit ASC` |
| **L6** | `load_period_products` + `rank_products` (dòng 244, 320) | **DRILL-DOWN** `category → sub_category → SKU` + **TOP-N** + tỷ trọng | `start_key, end_key, category, scope`, `metric ∈ {quantity,sales}`, `top_n ∈ 5..10` | `product_id, product_name, quantity, sales, share_pct` (share & top-N đang tính ở **Python**) |
| **L7** | `load_geo_summary` (dòng 265) | **ROLL-UP / DRILL-DOWN** địa lý `market → region → country` | `start_key, end_key, scope, level ∈ {market,region,country}` (f-string!) | `area, orders, sales, profit, margin_pct` |
| **L8** | `load_customer_segments` (dòng 284) | **ROLL-UP** theo hierarchy khách hàng, cấp `segment` | `start_key, end_key, scope` | `customers = COUNT(DISTINCT customer_id)`, `orders`, `sales`, `profit`, `margin_pct`, `avg_order_value` |
| **L9** | `load_subcategories` (dòng 303) | **ROLL-UP** `category → sub_category` | `start_key, end_key, scope` | `orders, quantity, sales, profit, margin_pct`; phát hiện nhóm lỗ (`profit<0 & orders>=3`) xử lý ở Python |
| **L10** | `load_geo_options` (dòng 58) | **DISTINCT trên slice** — phục vụ bộ lọc cascade (market → region → country) | `start_key, end_key` | danh sách `market, region, country` |
| **L11** | `load_order_date_bounds` (dòng 70) | **AGGREGATE thời gian toàn cục** `MIN/MAX` | không có | `first_date, last_date` (định nghĩa miền bộ lọc) |

**Lưu ý:** trang tổng quan **không dùng** PIVOT (cross-tab theo quý), **không dùng** MoM growth qua `LAG()`, **không dùng** `GROUP BY CUBE` — 3 kiểu này chỉ tồn tại trong thư viện `marts/` dạng demo.

Cấu trúc filter dùng chung (hiện đang nối chuỗi `GEO_FILTER` trong Python):

```sql
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
```

---

## Bước 2 — Đối chiếu với các file trong `src/sql/gold/marts/`

### 2.1 Bảng đối chiếu

| File | Operator OLAP | Giá trị hardcode | Logic tương ứng ở dashboard | Mức khớp |
|---|---|---|---|---|
| `olap_rollup.sql` | `GROUP BY ROLLUP (year, quarter, market, country)` | không filter kỳ/phạm vi; luôn rollup **4 cấp một lúc** | **L7** (geo) + **L3** (thời gian) — nhưng dashboard lấy **1 cấp/lúc**, có filter kỳ và 3 lớp địa lý, grain `day/week/month` | ⚠️ một phần |
| `olap_drilldown.sql` | drill-down `category → sub_category → SKU` | `WHERE p.category = 'Technology'`, `ORDER BY total_profit ASC`, `LIMIT 20` | **L6** (drill theo `category` param, rank theo `quantity|sales`, `top_n` 5..10, `ORDER DESC`, có scope) | ⚠️ một phần |
| `olap_slice_dice.sql` | `SLICE` + `DICE` | `market='APAC' AND year=2014`; dice `market IN ('APAC','EU') AND category IN (...) AND quarter IN (3,4)` | **L1/L4/L6...** — khái niệm slice đúng, nhưng dashboard slice theo **khoảng ngày tùy ý** + scope 3 lớp | ⚠️ khái niệm đúng, giá trị hardcode |
| `olap_pivot.sql` | cross-tab `sub_category × quarter` | `WHERE d.year = 2014` | **không có logic nào** ở trang tổng quan dùng pivot | ❌ không dùng (giữ làm thư viện) |
| `olap_growth_mom.sql` | window `LAG()` MoM | toàn cục, **không filter** kỳ/phạm vi; chỉ tháng | Dashboard làm **YoY giữa 2 kỳ tùy ý (L2)**, tính ở Python; không có MoM | ❌ khác logic |
| `olap_top_products.sql` | `DENSE_RANK() OVER (PARTITION BY category)` | `sales_rank <= 5`, chỉ theo **sales**, không scope | **L6**: `top_n` param, `metric ∈ {quantity,sales}`, `category` param, filter kỳ + địa lý, có `share_pct` | ⚠️ một phần |
| `olap_cube.sql` | `GROUP BY CUBE (year, category, market)` | `year IN (2013,2014)`, `market IN ('APAC','EU')` | không có logic nào | ❌ không dùng |
| `create_materialized_views.sql` | 3 MV pre-aggregate | – | nguồn cho Bước 3 | ✅ nền tảng |
| `run_olap_suite.py` | runner | list file hardcode, **không truyền params**, `split(';')` rồi chạy | – | ⚠️ cần nâng cấp theo file mới |

### 2.2 Logic **chưa có file nào** trong `marts/`

| ID | Logic chưa có file tương ứng | Ghi chú |
|---|---|---|
| L2 | So sánh YoY 2 kỳ | `olap_growth_mom.sql` khác logic (MoM chuỗi tháng toàn cục, không so 2 kỳ tùy ý) |
| L5 | Risk hotspots (`HAVING orders>=3 AND profit<0`, union 2 cấp, bottom-5) | không có file nào làm `HAVING` + bottom-N |
| L8 | Segment summary kèm `COUNT(DISTINCT customer_id)` + AOV | không có (MV `mv_customer_mart` làm RFM cấp khách lẻ, không cấp segment với số khách) |
| L10 | `DISTINCT` địa lý cho bộ lọc cascade | không có |
| L11 | `MIN/MAX` ngày (miền bộ lọc) | không có |

**Lưu ý — 6 logic chỉ khớp một phần** (chi tiết ở 2.1): **L1** & **L7** ↔ `olap_rollup.sql` (không có filter kỳ/phạm vi, `ROLLUP` bulk thay vì 1 cấp/lúc); **L3** ↔ `olap_rollup.sql` (chỉ `year/quarter`, thiếu `day/week`); **L4** & **L9** ↔ `olap_drilldown.sql` (hardcode `'Technology'`, **thiếu measure `orders`**); **L6** ↔ `olap_drilldown.sql` + `olap_top_products.sql` (hardcode `LIMIT 20` / `sales_rank <= 5`, chỉ theo `sales`).

### 2.3 Vấn đề "chưa tổng quát hoá" gặp ở cả 7 file

1. **Không có filter kỳ** (`order_date_key BETWEEN`) → mọi file luôn quét toàn bộ lịch sử.
2. **Không có filter phạm vi địa lý** (`market/region/country`) → không tái sử dụng được cho từng lượt chọn của người dùng.
3. **Giá trị nghiệp vụ hardcode trong SQL**: `'Technology'`, `2014`, `2013`, `'APAC'`, `'EU'`, `'Furniture'`, quý `3,4`, `LIMIT 20`, `<= 5`.
4. **Một file = một action duy nhất** → không nhận `:level`, `:grain`, `:metric`, `:top_n`, `:category`.
5. **Đầu ra không khớp cột mà `executive.py` mong đợi** (ví dụ `total_sales` vs `sales`, thiếu `line_count`, thiếu `share_pct`).
6. **`olap_rollup` dùng `ROLLUP` bulk** → trả cả dòng tổng rỗng (`NULLS FIRST`), dashboard cần **một cấp tại một thời điểm** (do đó phải `GROUP BY` thường + tham số `:level`).

---

## Bước 3 — Đánh dấu logic có thể truy vấn từ materialized view

### 3.1 Grain & measure của 3 MV hiện có

| MV | Grain (các cột chiều) | Measure | Rows (snapshot) |
|---|---|---|---|
| `gold.mv_sales_mart` | `year, quarter, month, year_month, market, region, country, segment` | `order_count, total_sales, total_profit, total_units, avg_discount, margin_pct` | 7.424 |
| `gold.mv_product_mart` | `category, sub_category, product_id, product_name, market, year` | `total_quantity, total_sales, total_profit, avg_discount, margin_pct` | 29.363 |
| `gold.mv_customer_mart` | `customer_id, customer_name, segment` (RFM) | `last_order_date, recency_days, frequency, monetary, total_profit, avg_order_value` | 1.590 |

> Hiện **không file nào trong `src/app` đọc 3 MV này** (chỉ `refresh_warehouse.py`, `demo_incremental.py`, `demo_backend.py` refresh chúng).

### 3.2 Ma trận đánh dấu

Ký hiệu: ✅ đọc được từ MV (điều kiện nêu kèm) · ⚠️ một phần · ❌ bắt buộc đọc `fact_sales`.

| ID | Logic | MV khả dụng | Đánh dấu & điều kiện |
|---|---|---|---|
| L1 | KPI kỳ | `mv_sales_mart` | ⚠️ `total_sales/total_profit` ✅ theo `year_month`; **`line_count` không có ở MV nào** ❌; `order_count = SUM(...)` ⚠️ (xem C1); `avg_discount = AVG(avg_discount)` ⚠️ (xem C2) |
| L2 | YoY 2 kỳ | như L1 | ⚠️ — chỉ khi **cả 2 kỳ đều month-aligned**; kỳ "Tùy chọn" không month-aligned → ❌ |
| L3 | Trend `day/week/month` | `mv_sales_mart` (`year_month`) | ⚠️ **chỉ `grain=Tháng`** (và `Năm`, `Quý`); `day`/`week` ❌ (không có ngày trong MV) |
| L4 | Category summary | `mv_product_mart` | ⚠️ có `total_quantity/total_sales/total_profit/margin_pct` ✅ nhưng **chỉ lọc theo `year`** (không theo khoảng ngày), **không có `region/country`** → không đủ scope của dashboard |
| L5 | Risk hotspots | `mv_sales_mart` + `mv_product_mart` | ⚠️ nhánh `market/country` ✅ (đủ `order_count`, `total_profit`, `country`); nhánh `category/sub_category` ❌ vì **`mv_product_mart` không có `order_id`/`order_count`** → không diễn đạt được `HAVING orders >= 3` |
| L6 | Top-N sản phẩm | `mv_product_mart` | ⚠️ `total_quantity`/`total_sales` ✅ theo `year + market`; ❌ thiếu `region/country`, thiếu khoảng ngày tùy ý; `share_pct` tính lại được ✅ (SUM OVER) |
| L7 | Geo summary (`market/region/country`) | `mv_sales_mart` | ⚠️ `total_sales/total_profit` ✅; `orders = SUM(order_count)` ⚠️ (C1); điều kiện **month-aligned** |
| L8 | Segment summary | `mv_sales_mart` | ⚠️ `sales/profit/orders/AOV` ✅; **`customers = COUNT(DISTINCT customer_id)` ❌** (MV không có `customer_key`) |
| L9 | Sub-category summary | `mv_product_mart` | ⚠️ `quantity/sales/profit/margin` ✅ (theo `year`); **`orders` ❌** → mất cột "Số đơn" và mất ngưỡng `>=3 đơn` ở phần "nhóm lỗ" |
| L10 | Geo options (filter cascade) | dim | ❌ **nên đọc `dim_geography`** (đúng chuẩn star schema; MV là kết quả tổng hợp, không dùng làm danh sách master) |
| L11 | Date bounds | dim/fact | ❌ đọc `dim_date`/`fact_sales` (1 câu rất rẻ) |

**Kết luận Bước 3:** *không có logic nào chạy hoàn toàn trên MV với đầy đủ filter của dashboard.* Chỉ **L7** và **một phần L1/L3/L8** đủ điều kiện dùng MV khi kỳ được chọn là **đầu tháng → cuối tháng**; phần còn lại phải đọc `fact_sales` (hoặc cần mở rộng MV).

### 3.3 Ràng buộc kỹ thuật phải tính tới (C1..C10)

| # | Ràng buộc | Ảnh hưởng |
|---|---|---|
| **C1** | `SUM(order_count)` từ MV chỉ bằng `COUNT(DISTINCT order_id)` khi **không có chiều phụ nào chia tách 1 đơn hàng** sang nhiều nhóm con (tháng/segment thì đúng vì 1 đơn thuộc 1 tháng, 1 khách); **`region`/`country` có thể chia được** nếu một đơn giao nhiều thành phố/khác vùng | KPI `Số đơn hàng` và `orders` ở L7/L8 cần đối soát ⏳ |
| **C2** | `AVG(avg_discount)` (lấy trung bình trung bình theo nhóm) **không bằng** `AVG(discount)` của dòng lẻ → lệch trọng số | L1 `Chiết khấu trung bình` ⚠️ sai số nhỏ |
| **C3** | `line_count` (dòng fact) **không tồn tại** trong MV nào | L1 luôn cần `fact_sales` (dùng làm cột "không có đơn hàng trong kỳ") |
| **C4** | `mv_sales_mart` không có khóa khách hàng | L8 `customers` ❌ |
| **C5** | `mv_product_mart` không có `order_id` → không có `order_count` | L5 nhánh ngành hàng, L9 `orders` ❌ |
| **C6** | `mv_sales_mart` chỉ có `month/quarter/year` (**không có ngày, không có tuần**) | L3 chỉ chạy MV ở grain Tháng |
| **C7** | Khoảng ngày **không căn chỉnh tháng** (vd `05/03/2014 → 17/09/2014`) không thể lọc chính xác trên `year_month` | MV chỉ dùng khi `start` = ngày đầu tháng và `end` = ngày cuối tháng (hoặc chấp nhận sai số) |
| **C8** | `mv_product_mart` chỉ có `year` và `market` | L4/L6/L9 không lọc theo `region/country` và theo ngày được |
| **C9** | MV chỉ đúng **sau `REFRESH MATERIALIZED VIEW`** (đã có trong `refresh_warehouse.py`) | Dashboard có filter tùy ý → **bắt buộc có fallback sang fact** |
| **C10** | `margin_pct` đã pre-aggregate theo nhóm | Khi tổng hợp tiếp phải `SUM(profit)/SUM(sales)`, **không** dùng `AVG(margin_pct)` |

### 3.4 Chiến lược đề xuất (2 lớp)

```
┌─ Lớp A: olap_*.sql đọc fact_sales/dim_*  → nguồn sự thật, đủ filter, mọi trường hợp (mặc định)
└─ Lớp B: *_mv.sql đọc mv_*_mart           → chỉ dùng khi kỳ month-aligned + ngữ cảnh cho phép
             └─ fallback tự động về Lớp A khi không thỏa điều kiện (đóng gói trong helper Python)
```

---

## Bước 4 — Nội dung các file SQL mục tiêu

### 4.0 Nguyên tắc chung (P1..P7)

* **P1** — Một file = một logic OLAP của dashboard; tên file khớp tên hàm trong `executive.py`.
* **P2** — Toàn bộ dùng bind param `:name` (đã là convention của `query_sql(engine, sql, params)` / `sqlalchemy.text`), **không** nối f-string vào SQL (sửa lỗi tiềm ẩn injection ở `load_geo_summary` dùng `f"... g.{level} ..."`).
* **P3** — Không hardcode giá trị nghiệp vụ; hằng nghiệp vụ (ví dụ `>= 3 đơn`) vẫn là **tham số** (`:min_orders`) có giá trị mặc định do Python truyền.
* **P4** — Khoảng ngày thống nhất `:start_key/:end_key` (`INT YYYYMMDD`) để khớp `dim_date.date_key`.
* **P5** — **Cột kết quả giữ nguyên tên** mà `executive.py` đang đọc (`line_count, order_count, sales, profit, avg_discount, period, category, quantity, margin_pct, customers, orders, area, segment, product_id, product_name, share_pct, kind, orders, first_date, last_date...`) → giảm số thay đổi phía app.
* **P6** — Header mỗi file ghi rõ: `params`, nguồn (fact/MV), điều kiện dùng MV, file logic tương ứng.
* **P7** — Filter địa lý thống nhất một mẫu duy nhất (`(:market IS NULL OR g.market = :market)` ...) để tái sử dụng.

### 4.1 Nhóm A — 10 file phục vụ trang tổng quan (mục tiêu chính)

| # | File mục tiêu | Thay cho | Tham số | Nguồn |
|---|---|---|---|---|
| A1 | `olap_kpi_period.sql` | `load_period_kpis` (L1 + L2) | `start_key, end_key, market, region, country` | fact |
| A2 | `olap_trend_period.sql` | `load_period_trend` (L3) | `+ grain` | fact |
| A3 | `olap_geo_summary.sql` | `load_geo_summary` (L7) | `+ level` | fact |
| A4 | `olap_segment_summary.sql` | `load_customer_segments` (L8) | scope + kỳ | fact |
| A5 | `olap_category_summary.sql` | `load_period_categories` (L4) | scope + kỳ | fact |
| A6 | `olap_subcategory_summary.sql` | `load_subcategories` (L9) | scope + kỳ | fact |
| A7 | `olap_product_topn.sql` | `load_period_products` + `rank_products` (L6) | `+ category, metric, top_n` | fact |
| A8 | `olap_risk_hotspots.sql` | `load_risk_hotspots` (L5) | `+ min_orders, top_n` | fact |
| A9 | `olap_geo_options.sql` | `load_geo_options` (L10) | `start_key, end_key` | fact + dim |
| A10 | `olap_date_bounds.sql` | `load_order_date_bounds` (L11) | – | fact + dim |

---

#### A1 — `olap_kpi_period.sql`

```sql
-- =============================================================================
-- OLAP: KPI theo kỳ (SLICE + AGGREGATE)          [Nhóm A - trang Tổng quan]
-- Thay cho: executive.load_period_kpis (L1) và so sánh YoY (L2)
-- params   : :start_key INT, :end_key INT (YYYYMMDD)
--            :market, :region, :country VARCHAR | NULL
-- Nguồn    : gold.fact_sales + gold.dim_geography  (KHÔNG dùng MV: cần line_count)
-- Gọi      : 2 lần/cập nhật - 1 lần kỳ hiện tại, 1 lần kỳ năm trước (để ra % YoY)
-- MV-variant: xem olap_kpi_period_mv.sql (chỉ khi kỳ month-aligned)
-- =============================================================================
SELECT
    COUNT(*)                                             AS line_count,
    COUNT(DISTINCT f.order_id)                           AS order_count,
    COALESCE(SUM(f.sales), 0)                            AS sales,
    COALESCE(SUM(f.profit), 0)                           AS profit,
    COALESCE(AVG(f.discount), 0)                         AS avg_discount
FROM gold.fact_sales f
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country);
```

**Biến thể MV (tùy chọn) — `olap_kpi_period_mv.sql`:**

```sql
-- CHỈ dùng khi :start_key là ngày đầu tháng và :end_key là ngày cuối tháng.
-- Thiếu line_count -> Python phải dùng một truy vấn fact riêng để kiểm "kỳ rỗng".
-- order_count: cộng dồn theo nhóm -> xem ràng buộc C1; avg_discount -> C2.
SELECT
    NULL::BIGINT                                        AS line_count,
    SUM(m.order_count)                                  AS order_count,
    COALESCE(SUM(m.total_sales), 0)                     AS sales,
    COALESCE(SUM(m.total_profit), 0)                    AS profit,
    COALESCE(SUM(m.avg_discount * m.total_sales)
             / NULLIF(SUM(m.total_sales), 0), 0)        AS avg_discount   -- weighted, tránh C2
FROM gold.mv_sales_mart m
WHERE m.year_month BETWEEN :start_month AND :end_month
  AND (:market IS NULL OR m.market = :market)
  AND (:region  IS NULL OR m.region  = :region)
  AND (:country IS NULL OR m.country = :country);
```

#### A2 — `olap_trend_period.sql`

```sql
-- =============================================================================
-- OLAP: Xu hướng theo grain thời gian (ROLL-UP day/week/month)   [Nhóm A]
-- Thay cho: executive.load_period_trend (L3)
-- params   : :start_key, :end_key, :grain ('day'|'week'|'month' - validate trước ở Python),
--            :market, :region, :country
-- Nguồn    : gold.fact_sales + gold.dim_date + gold.dim_geography
-- MV       : KHÔNG (mv_sales_mart chỉ có month/quarter/year -> chỉ grain 'month' mới thay được)
-- =============================================================================
SELECT
    CAST(date_trunc(:grain, d.full_date) AS date)       AS period,
    COUNT(DISTINCT f.order_id)                          AS order_count,
    ROUND(SUM(f.sales), 2)                              AS sales,
    ROUND(SUM(f.profit), 2)                             AS profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY 1
ORDER BY 1;
```

#### A3 — `olap_geo_summary.sql`

```sql
-- =============================================================================
-- OLAP: Tổng hợp theo cấp địa lý (ROLL-UP / DRILL-DOWN market->region->country)
-- Thay cho: executive.load_geo_summary (L7)
-- params   : :level ('market'|'region'|'country'), :start_key, :end_key,
--            :market, :region, :country
-- Ghi chú  : dùng CASE thay cho f-string "g.{level}" -> không còn nối chuỗi vào SQL
-- MV-variant: olap_geo_summary_mv.sql (khi kỳ month-aligned)
-- =============================================================================
SELECT
    CASE :level
        WHEN 'market'  THEN g.market
        WHEN 'region'  THEN g.region
        ELSE g.country
    END                                                   AS area,
    COUNT(DISTINCT f.order_id)                            AS orders,
    SUM(f.sales)::float                                   AS sales,
    SUM(f.profit)::float                                  AS profit,
    (SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100)::float AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY 1
ORDER BY sales DESC;
```

**Biến thể MV — `olap_geo_summary_mv.sql`:**

```sql
-- CHỈ khi kỳ month-aligned. `orders` = SUM(order_count) -> xem ràng buộc C1.
SELECT
    CASE :level WHEN 'market' THEN m.market
                WHEN 'region' THEN m.region
                ELSE m.country END                        AS area,
    SUM(m.order_count)                                    AS orders,
    SUM(m.total_sales)::float                             AS sales,
    SUM(m.total_profit)::float                            AS profit,
    (SUM(m.total_profit) / NULLIF(SUM(m.total_sales), 0) * 100)::float AS margin_pct
FROM gold.mv_sales_mart m
WHERE m.year_month BETWEEN :start_month AND :end_month
  AND (:market IS NULL OR m.market = :market)
  AND (:region  IS NULL OR m.region  = :region)
  AND (:country IS NULL OR m.country = :country)
GROUP BY 1
ORDER BY sales DESC;
```

#### A4 — `olap_segment_summary.sql`

```sql
-- =============================================================================
-- OLAP: Tổng hợp theo phân khúc khách hàng (ROLL-UP cấp segment)   [Nhóm A]
-- Thay cho: executive.load_customer_segments (L8)
-- params   : :start_key, :end_key, :market, :region, :country
-- MV       : CHỈ MỘT PHẦN - mv_sales_mart không có khóa khách
--            -> customers = COUNT(DISTINCT customer_id) bắt buộc đọc dim_customer
-- =============================================================================
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)                         AS customers,
    COUNT(DISTINCT f.order_id)                            AS orders,
    SUM(f.sales)::float                                   AS sales,
    SUM(f.profit)::float                                  AS profit,
    (SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100)::float AS margin_pct,
    (SUM(f.sales) / NULLIF(COUNT(DISTINCT f.order_id), 0))::float AS avg_order_value
FROM gold.fact_sales f
JOIN gold.dim_customer c ON c.customer_key = f.customer_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY c.segment
ORDER BY sales DESC;
```

#### A5 — `olap_category_summary.sql`

```sql
-- =============================================================================
-- OLAP: Tổng hợp theo danh mục (ROLL-UP cấp category)            [Nhóm A]
-- Thay cho: executive.load_period_categories (L4) - dùng cho bảng, cột và biểu đồ quạt
-- params   : :start_key, :end_key, :market, :region, :country
-- MV       : MỘT PHẦN - mv_product_mart chỉ có year + market, không region/country
-- =============================================================================
SELECT
    p.category,
    SUM(f.quantity)                                       AS quantity,
    ROUND(SUM(f.sales), 2)                                AS sales,
    ROUND(SUM(f.profit), 2)                               AS profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY p.category
ORDER BY sales DESC;
```

#### A6 — `olap_subcategory_summary.sql`

```sql
-- =============================================================================
-- OLAP: Tổng hợp theo ngành hàng con (ROLL-UP category -> sub_category) [Nhóm A]
-- Thay cho: executive.load_subcategories (L9) - cột "orders" phục vụ quy tắc
--           nhóm lỗ (profit < 0 VÀ orders >= 3) đang lọc ở Python
-- params   : :start_key, :end_key, :market, :region, :country
-- MV       : KHÔNG - mv_product_mart không có order_id/order_count (C5)
-- =============================================================================
SELECT
    p.category,
    p.sub_category,
    COUNT(DISTINCT f.order_id)                            AS orders,
    SUM(f.quantity)                                       AS quantity,
    SUM(f.sales)::float                                   AS sales,
    SUM(f.profit)::float                                  AS profit,
    (SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100)::float AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON p.product_key = f.product_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY p.category, p.sub_category
ORDER BY sales DESC;
```

#### A7 — `olap_product_topn.sql`

```sql
-- =============================================================================
-- OLAP: Drill-down tới SKU + TOP-N + tỷ trọng (thay rank_products ở Python) [Nhóm A]
-- Thay cho: executive.load_period_products + rank_products (L6)
-- params   : :start_key, :end_key, :category VARCHAR|NULL,
--            :metric ('quantity'|'sales'), :top_n INT (5..10 - validate ở Python),
--            :market, :region, :country
-- Ghi chú  : share_pct tính trên TOÀN BỘ tập lọc trước khi LIMIT -> đúng như Python
-- MV       : MỘT PHẦN - mv_product_mart (chỉ year + market)
-- =============================================================================
WITH agg AS (
    SELECT
        p.product_id,
        p.product_name,
        SUM(f.quantity)                                    AS quantity,
        ROUND(SUM(f.sales), 2)                             AS sales
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON p.product_key = f.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:category IS NULL OR p.category = :category)
      AND (:market IS NULL OR g.market = :market)
      AND (:region  IS NULL OR g.region  = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY p.product_id, p.product_name
),
scored AS (
    SELECT
        product_id,
        product_name,
        quantity,
        sales,
        CASE :metric WHEN 'quantity' THEN quantity ELSE sales END AS score
    FROM agg
)
SELECT
    product_id,
    product_name,
    quantity,
    sales,
    score,
    ROUND(100.0 * score / NULLIF(SUM(score) OVER (), 0), 3) AS share_pct
FROM scored
ORDER BY score DESC, product_name ASC, product_id ASC
LIMIT :top_n;
```

#### A8 — `olap_risk_hotspots.sql`

```sql
-- =============================================================================
-- OLAP: Điểm rủi ro - nhóm lợi nhuận âm (SLICE + HAVING + BOTTOM-N)  [Nhóm A]
-- Thay cho: executive.load_risk_hotspots (L5)
-- params   : :start_key, :end_key, :market, :region, :country,
--            :min_orders INT (mặc định 3), :top_n INT (mặc định 5)
-- Ghi chú  : nhãn 'Thị trường'/'Ngành hàng con' là chuỗi hiển thị (kind) - giữ như app
-- MV       : MỘT PHẦN - nhánh geo đọc mv_sales_mart được; nhánh product KHÔNG (C5)
-- =============================================================================
WITH geo AS (
    SELECT
        'Thị trường'::VARCHAR            AS kind,
        CONCAT(g.market, ' / ', g.country) AS segment,
        COUNT(DISTINCT f.order_id)         AS orders,
        ROUND(SUM(f.sales), 2)             AS sales,
        ROUND(SUM(f.profit), 2)            AS profit
    FROM gold.fact_sales f
    JOIN gold.dim_geography g ON f.geography_key = g.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:market IS NULL OR g.market = :market)
      AND (:region  IS NULL OR g.region  = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY g.market, g.country
    HAVING COUNT(DISTINCT f.order_id) >= :min_orders AND SUM(f.profit) < 0
),
product AS (
    SELECT
        'Ngành hàng con'::VARCHAR          AS kind,
        CONCAT(p.category, ' / ', p.sub_category) AS segment,
        COUNT(DISTINCT f.order_id)         AS orders,
        ROUND(SUM(f.sales), 2)             AS sales,
        ROUND(SUM(f.profit), 2)            AS profit
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:market IS NULL OR g.market = :market)
      AND (:region  IS NULL OR g.region  = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY p.category, p.sub_category
    HAVING COUNT(DISTINCT f.order_id) >= :min_orders AND SUM(f.profit) < 0
)
SELECT * FROM geo
UNION ALL
SELECT * FROM product
ORDER BY profit ASC
LIMIT :top_n;
```

#### A9 — `olap_geo_options.sql`

```sql
-- =============================================================================
-- OLAP: Danh sách địa lý trong kỳ (DISTINCT trên slice)           [Nhóm A]
-- Thay cho: executive.load_geo_options (L10) - nguồn cho bộ lọc cascade
-- params   : :start_key, :end_key
-- Nguồn    : fact + dim_geography (KHÔNG đọc MV: cần danh sách master đầy đủ)
-- =============================================================================
SELECT DISTINCT g.market, g.region, g.country
FROM gold.fact_sales f
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
ORDER BY g.market, g.region, g.country;
```

#### A10 — `olap_date_bounds.sql`

```sql
-- =============================================================================
-- OLAP: Miền thời gian của dữ liệu (MIN/MAX)                        [Nhóm A]
-- Thay cho: executive.load_order_date_bounds (L11)
-- params   : không có
-- =============================================================================
SELECT
    MIN(d.full_date) AS first_date,
    MAX(d.full_date) AS last_date
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key;
```

---

### 4.2 Nhóm B — chuẩn hoá 7 file OLAP mẫu hiện có (giữ vai trò thư viện/demo)

Mục tiêu: **giữ nguyên operator OLAP** nhưng bỏ hardcode, thêm filter kỳ + phạm vi.

#### B1 — `olap_rollup.sql` (mới)

```sql
-- params: :start_key, :end_key, :market, :region, :country
-- Dòng NULLS FIRST = subtotal của ROLLUP; giữ nguyên hành vi demo.
SELECT
    d.year,
    d.quarter,
    g.market,
    g.country,
    COUNT(DISTINCT f.order_id)                            AS total_orders,
    ROUND(SUM(f.sales), 2)                                AS total_sales,
    ROUND(SUM(f.profit), 2)                               AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region  IS NULL OR g.region  = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY ROLLUP (d.year, d.quarter, g.market, g.country)
ORDER BY d.year NULLS FIRST, d.quarter NULLS FIRST, g.market NULLS FIRST;
```

#### B2 — `olap_drilldown.sql` (mới)

```sql
-- params: :category VARCHAR|NULL (bỏ hardcode 'Technology'), :top_n INT (mặc định 20),
--         :sort_by ('profit_asc'|'profit_desc'|'sales_desc'), :start_key, :end_key
SELECT
    p.category,
    p.sub_category,
    p.product_id,
    p.product_name,
    SUM(f.quantity)                                       AS total_units_sold,
    ROUND(SUM(f.sales), 2)                                AS total_sales,
    ROUND(SUM(f.profit), 2)                               AS total_profit,
    ROUND(AVG(f.discount) * 100, 2)                       AS avg_discount_pct,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE (:category IS NULL OR p.category = :category)
  AND f.order_date_key BETWEEN :start_key AND :end_key
GROUP BY p.category, p.sub_category, p.product_id, p.product_name
ORDER BY
    CASE :sort_by
        WHEN 'profit_asc'  THEN  total_profit
        WHEN 'profit_desc' THEN -total_profit
        ELSE -total_sales
    END,
    p.product_name
LIMIT :top_n;
```

#### B3 — `olap_slice_dice.sql` (mới)

```sql
-- params: :markets VARCHAR[], :categories VARCHAR[], :years INT[], :quarters INT[]
--         (mảng = FULL LIST; slice = mảng 1 phần tử), :start_key, :end_key
-- Lưu ý: = ANY(:param) với list của psycopg2 -> ARRAY[...] , không nối chuỗi.

-- 1. SLICE (vd markets = ARRAY['APAC'], years = ARRAY[2014])
SELECT
    d.month,
    d.month_name,
    p.category,
    ROUND(SUM(f.sales), 2)                                AS sliced_sales,
    ROUND(SUM(f.profit), 2)                               AS sliced_profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND g.market  = ANY(:markets)
  AND p.category = ANY(:categories)
GROUP BY d.month, d.month_name, p.category
ORDER BY d.month, p.category;

-- 2. DICE (vd markets = ARRAY['APAC','EU'], categories = ARRAY['Furniture','Technology'],
--          quarters = ARRAY[3,4])
SELECT
    g.market,
    p.category,
    d.quarter,
    ROUND(SUM(f.sales), 2)                                AS diced_sales,
    ROUND(SUM(f.profit), 2)                               AS diced_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND g.market   = ANY(:markets)
  AND p.category = ANY(:categories)
  AND d.quarter  = ANY(:quarters)
GROUP BY g.market, p.category, d.quarter
ORDER BY g.market, p.category, d.quarter;
```

#### B4 — `olap_pivot.sql` (mới)

```sql
-- params: :year INT (bỏ hardcode 2014), :start_key, :end_key (fallback nếu không dùng :year)
SELECT
    p.sub_category,
    ROUND(SUM(CASE WHEN d.quarter = 1 THEN f.sales ELSE 0 END), 2) AS q1_sales,
    ROUND(SUM(CASE WHEN d.quarter = 2 THEN f.sales ELSE 0 END), 2) AS q2_sales,
    ROUND(SUM(CASE WHEN d.quarter = 3 THEN f.sales ELSE 0 END), 2) AS q3_sales,
    ROUND(SUM(CASE WHEN d.quarter = 4 THEN f.sales ELSE 0 END), 2) AS q4_sales,
    ROUND(SUM(f.sales), 2)                                     AS total_year_sales
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE d.year = :year
  AND f.order_date_key BETWEEN :start_key AND :end_key
GROUP BY p.sub_category
ORDER BY total_year_sales DESC;
```

#### B5 — `olap_growth_mom.sql` (mới)

```sql
-- params: :start_month VARCHAR(7) 'YYYY-MM', :end_month VARCHAR(7),
--         :market, :region, :country
-- Giữ LAG() MoM; bổ sung scope để so được MoM theo từng thị trường/phân khúc.
WITH monthly_sales AS (
    SELECT
        d.year,
        d.month,
        d.year_month,
        SUM(f.sales) AS current_sales
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    JOIN gold.dim_geography g ON f.geography_key = g.geography_key
    WHERE d.year_month BETWEEN :start_month AND :end_month
      AND (:market IS NULL OR g.market = :market)
      AND (:region  IS NULL OR g.region  = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY d.year, d.month, d.year_month
)
SELECT
    year_month,
    ROUND(current_sales, 2) AS sales,
    ROUND(LAG(current_sales, 1) OVER (ORDER BY year, month), 2) AS prev_month_sales,
    ROUND(
        (current_sales - LAG(current_sales, 1) OVER (ORDER BY year, month))
        / NULLIF(LAG(current_sales, 1) OVER (ORDER BY year, month), 0) * 100,
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY year, month;
```

#### B6 — `olap_top_products.sql` (mới)

```sql
-- params: :top_n INT (bỏ hardcode 5), :metric ('sales'|'quantity'),
--         :category VARCHAR|NULL, :start_key, :end_key, :market, :region, :country
WITH product_agg AS (
    SELECT
        p.category,
        p.product_name,
        ROUND(SUM(f.sales), 2)    AS total_sales,
        ROUND(SUM(f.quantity), 0) AS total_quantity,
        ROUND(SUM(f.profit), 2)   AS total_profit
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:category IS NULL OR p.category = :category)
      AND (:market IS NULL OR g.market = :market)
      AND (:region  IS NULL OR g.region  = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY p.category, p.product_name
),
ranked AS (
    SELECT
        *,
        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY CASE :metric WHEN 'quantity' THEN total_quantity ELSE total_sales END DESC
        ) AS sales_rank
    FROM product_agg
)
SELECT category, sales_rank, product_name, total_sales, total_quantity, total_profit
FROM ranked
WHERE sales_rank <= :top_n
ORDER BY category, sales_rank;
```

#### B7 — `olap_cube.sql` (mới)

```sql
-- params: :years INT[], :markets VARCHAR[], :start_key, :end_key
SELECT
    d.year,
    p.category,
    g.market,
    ROUND(SUM(f.sales), 2)  AS sales,
    ROUND(SUM(f.profit), 2) AS profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_product p ON f.product_key = p.product_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND d.year    = ANY(:years)
  AND g.market = ANY(:markets)
GROUP BY CUBE (d.year, p.category, g.market)
ORDER BY d.year NULLS FIRST, p.category NULLS FIRST, g.market NULLS FIRST;
```

---

### 4.3 Thay đổi đi kèm (ngoài SQL)

| Thành phần | Thay đổi |
|---|---|
| `src/app/executive.py` | Thêm helper `_query_file(name, params)` → `query_sql(engine, read_sql(f"gold/marts/{name}"), params)`; **10/10 hàm `load_*`** gọi file thay vì chứa SQL inline; `load_geo_options`/`load_order_date_bounds` → A9/A10; **bỏ f-string `g.{level}`** ở L7 → bind `:level`; `rank_products` (Python) → trả về `share_pct` từ A7 |
| `src/pipeline/reader.py` | Không đổi (`read_sql` đã trả nội dung file) |
| `src/sql/gold/marts/run_olap_suite.py` | Chuyển list thành `(title, path, params)`; **bỏ `split(';')`** (mỗi file giờ là 1 statement có params); thêm case demo Nhóm B với params ví dụ (`category=NULL`, `top_n=10`, `year=2014`...) |
| `src/app/demo_backend.py` | Giữ nguyên `refresh_all_marts()` — điều kiện tiên quyết nếu sau này bật Lớp B (`*_mv.sql`) |
| Fallback Lớp B | Helper `_query_period(path, params)` tự chọn `*_mv.sql` khi kỳ month-aligned **và** logic thuộc nhóm ✅/⚠️ ở Bước 3, ngược lại quay về file Nhóm A |

### 4.4 Tiêu chí nghiệm thu

1. `python -m src.sql.gold.marts.run_olap_suite` chạy hết Nhóm A + B không lỗi, không còn giá trị hardcode `'Technology'/2014/'APAC'` trong SQL.
2. Kết quả của **10/10 hàm `load_*`** mới (gọi A1..A10) **trùng số với bản inline hiện tại** cho 3 bộ filter: (a) toàn kỳ + tất cả địa lý, (b) `2014-01-01→2014-12-31` + `market=APAC`, (c) kỳ tuỳ chọn `2014-03-05→2014-09-17`.
3. Không còn nối f-string vào SQL trong `executive.py` (`grep -n 'f"""' src/app/executive.py` = 0 kết quả).
4. Trang tổng quan hiển thị đủ 5 thẻ metric, 7 khối biểu đồ/bảng, không regression về giá trị hiển thị.
5. Biến thể `*_mv.sql` (nếu bật) cho số **bằng 0.01%** so với Nhóm A ở kỳ month-aligned; khác biệt `order_count` (C1) phải được ghi nhận/nếu >0 thì tắt Lớp B cho metric `orders`.

---

## Mục chờ xác minh khi DB chạy (⏳)

Docker daemon đang tắt (PostgreSQL chưa khởi động) nên chưa chạy được các câu đối soát sau:

1. **C1** — 1 đơn hàng có bị chia nhiều `market/country` không (ảnh hưởng `SUM(order_count)`):
   ```sql
   WITH per_order AS (
     SELECT f.order_id,
            COUNT(DISTINCT g.market)  AS markets,
            COUNT(DISTINCT g.country) AS countries
     FROM gold.fact_sales f
     JOIN gold.dim_geography g ON g.geography_key = f.geography_key
     GROUP BY f.order_id)
   SELECT COUNT(*) FILTER (WHERE markets  > 1) AS multi_market,
          COUNT(*) FILTER (WHERE countries > 1) AS multi_country,
          COUNT(*) AS total_orders
   FROM per_order;
   ```
   → Nếu `multi_market`/`multi_country` = 0 thì L7/L8 chuyển sang Lớp B an toàn.
2. **C2** — so `AVG(discount)` (fact) vs `AVG(avg_discount)` và weighted version (A1 MV).
3. **Chứng minh Lớp B**: so `SUM(total_sales)` từ `mv_sales_mart` (`year_month` full range) với `SUM(sales)` từ `fact_sales`.
4. **Lệch range không month-aligned**: `mv` lọc `year_month BETWEEN '2014-03' AND '2014-09'` vs `fact` `BETWEEN 20140305 AND 20140917` → dùng để khẳng định ràng buộc C7 (kỳ vọng lệch rõ).
5. Số liệu snapshot đã ghi nhận khi DB còn chạy (12/11): `mv_sales_mart` 7.424 rows, `mv_product_mart` 29.363 rows, `mv_customer_mart` 1.590 rows; gold base tables = `dim_customer, dim_date, dim_geography, dim_product, dim_ship_mode, fact_sales`.

---

## Lộ trình đề xuất

| Giai đoạn | Việc làm | Kết quả |
|---|---|---|
| **1** | Viết 10 file Nhóm A (nội dung ở §4.1) + chạy suite đối chiếu với SQL inline hiện tại | SQL tách khỏi Python, đủ tham số |
| **2** | Refactor `executive.py` dùng `_query_file`, bỏ f-string `:level` | Sửa luôn lỗ hổng tiềm ẩn từ việc nối chuỗi ở `load_geo_summary`, dashboard đọc file SQL |
| **3** | Nâng cấp 7 file Nhóm B + `run_olap_suite.py` có params | Thư viện OLAP không còn hardcode |
| **4** | Chạy các câu ⏳ ở trên; nếu đạt điều kiện → viết `*_mv.sql` + helper fallback | Tốc độ đọc nhanh ở kỳ chuẩn, vẫn đúng ở kỳ tuỳ chọn |
