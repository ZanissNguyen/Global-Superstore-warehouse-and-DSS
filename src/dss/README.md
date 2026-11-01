DSS cho bài tập Data Warehouse (Global Superstore)

## 1. Mục tiêu và phạm vi

Tài liệu này mô tả hai phương án có thể chọn để triển khai thành phần
Decision Support System (DSS):

1.  **Predictive Analytics:** Dự báo doanh thu (Sales Forecasting) và
    Product Demand Forecasting ở mức cơ bản.
2.  **Association Rule Mining:** Khai phá luật kết hợp để tìm các sản
    phẩm thường xuất hiện cùng nhau trong một đơn hàng.

**Chỉ chọn một trong hai phương án để triển khai.** Không cần tạo cả hai
module hoặc cả hai nhóm bảng kết quả. Mỗi phương án bên dưới được mô tả
độc lập để nhóm có thể cân nhắc và lựa chọn.

DSS được tổ chức thành pipeline riêng dưới `src/dss/`, đọc dữ liệu đã
được ETL vào Data Warehouse, sau đó lưu kết quả vào PostgreSQL để Power
BI/giao diện DSS sử dụng. DSS không thay thế Bronze/Silver/Gold và không
được tự ý sửa dữ liệu ở các layer này.

## 2. Vị trí DSS trong kiến trúc tổng thể

``` text
Data Source
    |
    v
Bronze  -- nạp và lưu vết dữ liệu nguồn
    |
    v
Silver  -- làm sạch, chuẩn hóa dữ liệu
    |
    v
Gold    -- Fact/Dimension phục vụ phân tích
    |
    v
src/dss/ -- xử lý dữ liệu, huấn luyện mô hình hoặc khai phá luật
    |
    v
PostgreSQL (schema dss) -- lưu kết quả và metadata
    |
    v
Power BI / DSS Interface -- trực quan hóa và hỗ trợ quyết định
```

### 2.1. Chọn layer dữ liệu nào?

  -----------------------------------------------------------------------
  Công việc               Layer đề xuất           Lý do
  ----------------------- ----------------------- -----------------------
  Dashboard/KPI           Gold                    Dữ liệu đã được tổ chức
                                                  theo mô hình phân tích

  Huấn luyện dự báo doanh Gold                    Có FactSales và
  thu                                             DimDate, thuận tiện
                                                  tổng hợp theo thời gian

  Dự báo nhu cầu sản phẩm Gold                    Có thể tổng hợp
                                                  Quantity theo thời gian
                                                  và sản phẩm/danh mục

  Khai phá luật kết hợp   Silver hoặc Gold        Cần dữ liệu giao dịch ở
                          FactSales               grain dòng sản phẩm,
                                                  giữ Order ID và Product
                                                  ID

  Dùng dữ liệu thô để     Không khuyến nghị       Bronze chưa đảm bảo
  huấn luyện trực tiếp                            chất lượng và ngữ nghĩa
                                                  dữ liệu
  -----------------------------------------------------------------------

**Lưu ý:** Gold không đồng nghĩa mọi bảng đều đã được tổng hợp.
`gold.fact_sales` cần giữ grain một dòng sản phẩm trong một đơn hàng nếu
muốn dùng nó cho Association Rule Mining. Nếu chỉ còn dữ liệu tổng hợp
theo tháng/danh mục thì không thể khôi phục quan hệ sản phẩm trong từng
đơn hàng.

### 2.2. Giả định về bảng và cột

Tên bảng dưới đây là tên đề xuất, cần điều chỉnh theo schema thực tế của
repository:

  -----------------------------------------------------------------------
  Bảng                                Cột quan trọng
  ----------------------------------- -----------------------------------
  `silver.sales_cleaned`              `order_id`, `product_id`,
                                      `order_date`, `quantity`, `sales`

  `gold.fact_sales`                   `order_id` (hoặc degenerate order
                                      identifier), `product_key`,
                                      `date_key`, `quantity`, `sales`

  `gold.dim_date`                     `date_key`, `full_date`, `year`,
                                      `month`, `year_month`

  `gold.dim_product`                  `product_key`, `product_id`,
                                      `category`, `sub_category`,
                                      `product_name`
  -----------------------------------------------------------------------

Nếu `fact_sales` không giữ `order_id`, hoặc `dim_product` không có mã
sản phẩm để nối, cần điều chỉnh Gold trước khi dùng fact table cho
Association Rule Mining.

------------------------------------------------------------------------

# PHƯƠNG ÁN A -- PREDICTIVE ANALYTICS

## 3. Mục tiêu và phạm vi

Xây dựng pipeline dự báo đơn giản từ dữ liệu bán hàng lịch sử.

Phạm vi đề xuất:

-   **Sales Forecasting:** Dự báo tổng doanh thu theo tháng.
-   **Product Demand Forecasting:** Dự báo số lượng bán (`Quantity`)
    theo tháng cho một số danh mục sản phẩm (`Category`), ở mức cơ bản.

Không nên bắt đầu bằng dự báo từng `Product ID`: nhiều sản phẩm có chuỗi
thời gian thưa, ít giao dịch và dễ cho kết quả thiếu ổn định. Global
Superstore có khoảng bốn năm dữ liệu, tương đương khoảng 48 điểm dữ liệu
nếu tổng hợp theo tháng. Vì vậy nên giữ mô hình đơn giản, đánh giá cẩn
thận và không tuyên bố độ chính xác quá mức.

## 4. Dữ liệu đầu vào

### 4.1. Sales Forecasting

**Nguồn:** `gold.fact_sales` JOIN `gold.dim_date`.

Tạo dataset theo tháng, mỗi tháng một dòng:

  year_month     total_sales
  ------------ -------------
  2011-01                ...
  2011-02                ...
  2011-03                ...

Phép biến đổi:

1.  Nối FactSales với DimDate bằng `date_key`.
2.  Nhóm theo tháng của **Order Date**.
3.  Tính `SUM(sales)` thành `total_sales`.
4.  Sắp xếp tăng dần theo thời gian.
5.  Kiểm tra các tháng bị thiếu. Chỉ bổ sung tháng với doanh thu `0` nếu
    thực sự không có giao dịch trong tháng đó, không phải do lỗi thiếu
    dữ liệu ETL.

Dùng `Order Date` làm trục thời gian vì mục tiêu là dự báo doanh thu
theo thời điểm phát sinh đơn hàng. Không thay bằng `Ship Date`.

### 4.2. Product Demand Forecasting cơ bản

**Nguồn:** `gold.fact_sales` JOIN `gold.dim_date` JOIN
`gold.dim_product`.

Tạo dataset theo tháng và Category:

  year_month   category       total_quantity
  ------------ ------------ ----------------
  2011-01      Furniture                 ...
  2011-01      Technology                ...
  2011-02      Furniture                 ...

Phép biến đổi:

1.  Nối FactSales với DimDate và DimProduct.
2.  Nhóm theo tháng của Order Date và `category`.
3.  Tính `SUM(quantity)` thành `total_quantity`.
4.  Tạo chuỗi thời gian riêng cho từng Category.

Bắt đầu ở mức `Category`; chỉ chuyển sang `Sub-Category` nếu dữ liệu đủ
dày và kết quả có ý nghĩa. Đây là dự báo nhu cầu ở mức danh mục, không
phải dự báo tồn kho hay lượng cần đặt hàng vì dataset không có tồn kho,
lead time và đơn hàng chưa đáp ứng.

### 4.3. Trường dữ liệu không cần cho phiên bản cơ bản

Không cần đưa toàn bộ Customer, Geography, Ship Mode hoặc Discount vào
mô hình dự báo tổng doanh thu theo tháng. Có thể mở rộng sau, nhưng
không cần thiết để hoàn thành phạm vi cơ bản.

## 5. Xử lý, huấn luyện và đánh giá

Pipeline đề xuất:

1.  **Extract:** Đọc dữ liệu Gold bằng SQL.
2.  **Transform:** Tổng hợp theo tháng, tạo chuỗi thời gian liên tục,
    kiểm tra null, kiểu dữ liệu và thứ tự ngày.
3.  **Split:** Chia train/test theo thứ tự thời gian; không shuffle ngẫu
    nhiên.
4.  **Train:** Huấn luyện baseline và mô hình dự báo đơn giản.
5.  **Evaluate:** So sánh dự báo với dữ liệu test.
6.  **Forecast:** Fit trên dữ liệu hiện có và dự báo một số tháng tiếp
    theo.
7.  **Persist:** Lưu kết quả dự báo và metadata lần chạy vào schema
    `dss`.
8.  **Visualize:** Power BI đọc kết quả để hiển thị Actual vs Forecast.

### Mô hình khuyến nghị

Chỉ cần một baseline và một mô hình chính:

-   **Naive baseline:** Dùng giá trị kỳ gần nhất làm dự báo kỳ tiếp
    theo.
-   **Moving Average:** Dự báo bằng trung bình một số tháng gần nhất.

Có thể thay Moving Average bằng **Exponential Smoothing** nếu muốn thử
một mô hình chuỗi thời gian cơ bản khác. Không cần triển khai ARIMA,
Prophet, XGBoost hay deep learning trong phạm vi tối thiểu.

### Đánh giá

-   **MAE:** Sai số tuyệt đối trung bình.
-   **RMSE:** Phạt nặng hơn các sai số lớn.
-   **MAPE:** Sai số phần trăm; không phù hợp khi giá trị thực bằng hoặc
    gần 0.

Ưu tiên MAE/RMSE. Nếu dùng MAPE, cần xử lý rõ các kỳ có giá trị thực
bằng 0. Ghi lại khoảng thời gian train/test để kết quả có thể tái lập.

## 6. Cấu trúc thư mục cho phương án A

Nếu chọn Predictive Analytics:

``` text
src/
└── dss/
    ├── README.md
    ├── common/
    │   ├── db.py
    │   └── logger.py
    └── predictive/
        ├── __init__.py
        ├── config.py
        ├── extract.py
        ├── transform.py
        ├── features.py
        ├── models.py
        ├── evaluate.py
        ├── forecast.py
        ├── load.py
        └── run.py
```

  -----------------------------------------------------------------------
  File                                Trách nhiệm
  ----------------------------------- -----------------------------------
  `README.md`                         Cách chạy pipeline, input, output
                                      và cấu hình

  `common/db.py`                      Kết nối, đọc/ghi PostgreSQL; tái sử
                                      dụng connector hiện có nếu có

  `common/logger.py`                  Logging; ưu tiên dùng logger chung
                                      của project

  `predictive/config.py`              Bảng nguồn, target, cột thời gian,
                                      horizon và tham số mô hình

  `predictive/extract.py`             Truy vấn FactSales, DimDate và
                                      DimProduct

  `predictive/transform.py`           Tổng hợp dữ liệu theo tháng, kiểm
                                      tra và xử lý chuỗi thời gian

  `predictive/features.py`            Tạo đặc trưng thời gian cơ bản nếu
                                      mô hình cần

  `predictive/models.py`              Baseline và mô hình dự báo được
                                      chọn

  `predictive/evaluate.py`            Chia train/test theo thời gian,
                                      tính MAE/RMSE/MAPE phù hợp

  `predictive/forecast.py`            Huấn luyện trên dữ liệu hiện có và
                                      sinh dự báo tương lai

  `predictive/load.py`                Ghi kết quả và metadata vào
                                      PostgreSQL

  `predictive/run.py`                 Entry point điều phối pipeline
  -----------------------------------------------------------------------

Nếu phiên bản cơ bản không cần feature engineering riêng, có thể bỏ
`features.py`; không tạo file chỉ để giữ cấu trúc đẹp.

### Bảng kết quả gợi ý trong schema `dss`

**`dss.forecast_run`** -- metadata mỗi lần chạy:

-   `run_id`
-   `model_name`
-   `target_name`
-   `granularity` (ví dụ `month`)
-   `train_start`, `train_end`
-   `test_start`, `test_end`
-   `created_at`
-   `mae`, `rmse`, `mape` (MAPE có thể null)
-   `parameters` (JSONB, nếu cần)

**`dss.forecast_result`** -- kết quả dự báo:

-   `run_id`
-   `forecast_date`
-   `series_key` (null với tổng Sales; Category khi dự báo theo danh
    mục)
-   `actual_value` (null cho kỳ tương lai chưa có actual)
-   `predicted_value`
-   `lower_bound`, `upper_bound` (nullable; chỉ lưu nếu mô hình cung cấp
    khoảng dự báo)

Không cần lưu model artifact nếu mô hình đơn giản và có thể tái huấn
luyện nhanh. Nếu có lưu artifact, đặt ở thư mục output riêng, không
commit file sinh tự động hoặc file lớn vào Git.

### Cách chạy minh họa

``` bash
python -m src.dss.predictive.run --target sales --horizon 3
```

Nếu hỗ trợ dự báo Quantity theo Category:

``` bash
python -m src.dss.predictive.run --target quantity --group-by category --horizon 3
```

Đây là cú pháp gợi ý, cần đồng bộ với cách chạy các pipeline ETL hiện
tại.

------------------------------------------------------------------------

# PHƯƠNG ÁN B -- ASSOCIATION RULE MINING

## 7. Mục tiêu

Khai phá các tập sản phẩm thường xuất hiện cùng nhau trong một đơn hàng,
sau đó tạo luật kết hợp để hỗ trợ phân tích hành vi mua hàng và ý tưởng
cross-selling.

Ví dụ:

``` text
ORD-001: [Product A, Product B, Product C]
ORD-002: [Product A, Product D]
ORD-003: [Product B, Product C]
```

Có thể tìm được luật dạng `Product A -> Product B`. Luật chỉ thể hiện
mối liên hệ đồng xuất hiện trong dữ liệu, không chứng minh A gây ra việc
mua B.

## 8. Dữ liệu đầu vào

**Nguồn ưu tiên:** `silver.sales_cleaned`; hoặc `gold.fact_sales` JOIN
`gold.dim_product`.

Silver thường thuận tiện nếu đã có đủ `order_id` và `product_id`. Nếu
dùng Gold, phải đảm bảo FactSales vẫn ở grain dòng sản phẩm trong đơn
hàng và giữ được định danh đơn hàng.

Cột tối thiểu:

-   `order_id`: định danh đơn hàng.
-   `product_id`: định danh sản phẩm.

Có thể lấy `product_name`, `category`, `sub_category` từ DimProduct để
hiển thị kết quả dễ hiểu. Không dùng bảng tổng hợp doanh thu theo
tháng/danh mục làm input vì bảng đó không còn quan hệ sản phẩm trong
từng đơn hàng.

### Chuyển dữ liệu thành transaction/basket

Dữ liệu dòng giao dịch:

  order_id   product_id
  ---------- ------------
  ORD-001    P001
  ORD-001    P002
  ORD-001    P003
  ORD-002    P001
  ORD-002    P004

Dạng transaction:

``` text
ORD-001: [P001, P002, P003]
ORD-002: [P001, P004]
```

Mỗi đơn hàng chỉ nên chứa một lần xuất hiện của một `product_id`. Nếu
một sản phẩm xuất hiện nhiều dòng trong cùng đơn hàng, loại trùng ở cấp
`(order_id, product_id)` trước khi tạo basket.

Nếu nguồn có thông tin trạng thái hủy/hoàn trả thì cần xác định quy tắc
loại các giao dịch đó. Không tự suy diễn trạng thái nếu dataset không
cung cấp.

## 9. Khai phá và đánh giá luật

Pipeline đề xuất:

1.  **Extract:** Đọc `order_id`, `product_id` và thông tin sản phẩm từ
    Silver hoặc Gold.
2.  **Clean:** Loại dòng thiếu Order ID/Product ID; loại trùng cặp
    `(order_id, product_id)`.
3.  **Basket construction:** Gom danh sách Product ID theo Order ID.
4.  **Frequent itemset mining:** Tìm tập sản phẩm phổ biến bằng Apriori
    hoặc FP-Growth.
5.  **Rule generation:** Sinh luật kết hợp từ frequent itemsets.
6.  **Filter:** Lọc luật theo Support, Confidence và Lift.
7.  **Enrich:** Nối Product ID với tên và danh mục sản phẩm.
8.  **Persist:** Lưu itemsets, rules và metadata lần chạy vào schema
    `dss`.
9.  **Visualize:** Hiển thị luật nổi bật và các sản phẩm liên quan.

### Thuật toán khuyến nghị

Chỉ chọn **một**:

-   **Apriori:** Dễ giải thích, phù hợp khi muốn trình bày nguyên lý
    thuật toán.
-   **FP-Growth:** Có thể hiệu quả hơn khi dữ liệu có nhiều frequent
    itemsets.

Không cần triển khai cả hai. Có thể dùng thư viện Python `mlxtend`, đồng
thời trình bày rõ cách chuyển dữ liệu giao dịch thành basket.

### Các chỉ số cần trình bày

Với luật `A -> B`:

-   **Support:** Tỷ lệ tổng số đơn hàng có cả A và B.
-   **Confidence:** Trong các đơn hàng có A, tỷ lệ đơn hàng cũng có B.
-   **Lift:** So sánh xác suất xuất hiện B khi có A với xác suất nền
    xuất hiện B.

Diễn giải Lift:

-   `Lift > 1`: A và B đồng xuất hiện nhiều hơn mức kỳ vọng nếu độc lập.
-   `Lift = 1`: Không thể hiện liên kết vượt mức độc lập.
-   `Lift < 1`: A và B đồng xuất hiện ít hơn mức kỳ vọng nếu độc lập.

Không chỉ sắp xếp luật theo Confidence: một sản phẩm phổ biến có thể tạo
Confidence cao nhưng Lift thấp. Nên xem đồng thời Support, Confidence,
Lift và số lượng giao dịch thực tế.

Ngưỡng Support/Confidence cần được thử nghiệm: ngưỡng quá thấp có thể
tạo rất nhiều luật ít giá trị; ngưỡng quá cao có thể không tìm thấy luật
nào đáng kể.

## 10. Cấu trúc thư mục cho phương án B

Nếu chọn Association Rule Mining:

``` text
src/
└── dss/
    ├── README.md
    ├── common/
    │   ├── db.py
    │   └── logger.py
    └── association/
        ├── __init__.py
        ├── config.py
        ├── extract.py
        ├── transform.py
        ├── mine.py
        ├── rules.py
        ├── evaluate.py
        ├── load.py
        └── run.py
```

  -----------------------------------------------------------------------
  File                                Trách nhiệm
  ----------------------------------- -----------------------------------
  `README.md`                         Cách chạy, input, output và cấu
                                      hình

  `common/db.py`                      Kết nối, đọc/ghi PostgreSQL; tái sử
                                      dụng connector hiện có nếu có

  `common/logger.py`                  Logging; tái sử dụng logger chung
                                      của project nếu có

  `association/config.py`             Bảng nguồn, cột Order ID/Product
                                      ID, thuật toán và ngưỡng

  `association/extract.py`            Truy vấn dữ liệu dòng giao dịch từ
                                      Silver hoặc Gold

  `association/transform.py`          Làm sạch, loại trùng và tạo
                                      transaction/basket

  `association/mine.py`               Chạy Apriori hoặc FP-Growth để tìm
                                      frequent itemsets

  `association/rules.py`              Sinh luật kết hợp từ frequent
                                      itemsets

  `association/evaluate.py`           Kiểm tra Support, Confidence, Lift
                                      và lọc luật

  `association/load.py`               Ghi itemsets, rules và metadata vào
                                      PostgreSQL

  `association/run.py`                Entry point điều phối pipeline
  -----------------------------------------------------------------------

### Bảng kết quả gợi ý trong schema `dss`

**`dss.association_run`** -- metadata mỗi lần chạy:

-   `run_id`
-   `algorithm`
-   `min_support`
-   `min_confidence`
-   `min_lift`
-   `transaction_count`
-   `created_at`

**`dss.frequent_itemset`** -- tập sản phẩm phổ biến:

-   `run_id`
-   `itemset_id`
-   `items` (JSONB hoặc cấu trúc lưu danh sách Product ID)
-   `itemset_size`
-   `support`
-   `transaction_count`

**`dss.association_rule`** -- luật kết hợp:

-   `run_id`
-   `antecedents` (JSONB hoặc danh sách Product ID)
-   `consequents` (JSONB hoặc danh sách Product ID)
-   `support`
-   `confidence`
-   `lift`

Có thể bỏ bảng `frequent_itemset` nếu chỉ cần lưu luật cuối cùng. Tuy
nhiên, lưu itemsets giúp giải thích nguồn gốc luật và kiểm tra kết quả.
Khi hiển thị, join Product ID với DimProduct để lấy tên; không nên chỉ
lưu tên vì tên có thể trùng hoặc thay đổi.

### Cách chạy minh họa

``` bash
python -m src.dss.association.run --algorithm apriori
```

Ngưỡng như `min-support`, `min-confidence` có thể cấu hình qua CLI hoặc
`config.py`. Cú pháp CLI là gợi ý, cần đồng bộ với project.

------------------------------------------------------------------------

## 11. So sánh để lựa chọn

  -----------------------------------------------------------------------
  Tiêu chí                Predictive Analytics    Association Rule Mining
  ----------------------- ----------------------- -----------------------
  Câu hỏi chính           Doanh thu/nhu cầu có    Sản phẩm nào thường
                          thể diễn biến thế nào?  được mua cùng nhau?

  Dữ liệu đầu vào         Gold FactSales +        Silver sales_cleaned
                          DimDate; thêm           hoặc Gold FactSales ở
                          DimProduct cho demand   grain giao dịch

  Kiểu dữ liệu xử lý      Chuỗi thời gian theo    Basket gồm Product ID
                          tháng                   theo Order ID

  Kỹ thuật cơ bản         Naive, Moving Average   Apriori hoặc FP-Growth

  Đánh giá                MAE, RMSE; MAPE khi phù Support, Confidence,
                          hợp                     Lift

  Kết quả lưu             Actual/Predicted theo   Frequent itemsets,
                          kỳ và metadata mô hình  rules và metrics

  Khó khăn chính          Chuỗi thời gian ngắn,   Chọn ngưỡng và lọc luật
                          cần split theo thời     có ý nghĩa
                          gian                    

  Cách trình bày          Biểu đồ Actual vs       Bảng luật, danh sách
                          Forecast                sản phẩm liên quan hoặc
                                                  network graph
  -----------------------------------------------------------------------

Gợi ý:

-   Chọn **Predictive Analytics** nếu muốn thể hiện quy trình huấn
    luyện, kiểm thử, đánh giá mô hình và dự báo tương lai.
-   Chọn **Association Rule Mining** nếu muốn bài toán khai phá dữ liệu
    gọn, liên hệ trực tiếp với giao dịch và có kết quả dễ giải thích.

Cả hai đều phù hợp với phạm vi cơ bản. Không cần làm cả hai để chứng
minh hệ thống có DSS.

## 12. Nguyên tắc triển khai chung

1.  **Giữ DSS tách khỏi ETL:** `src/dss/` đọc dữ liệu từ Gold/Silver,
    không tự sửa Bronze, Silver hoặc Gold.
2.  **Tách các bước:** Extract -- Transform -- Model/Mining -- Evaluate
    -- Load. Không dồn toàn bộ logic vào một notebook hoặc một file
    `run.py`.
3.  **Có thể chạy lại:** Mỗi lần chạy nên có `run_id`, thời điểm chạy,
    cấu hình và trạng thái.
4.  **Không hard-code thông tin kết nối:** Dùng environment
    variables/cấu hình theo chuẩn repository.
5.  **Quản lý file sinh ra:** Model artifact, CSV kết quả và cache không
    nên commit tùy tiện vào Git; dùng thư mục output riêng và
    `.gitignore` nếu phù hợp.
6.  **Kết quả truy vấn được:** Lưu vào schema riêng, ví dụ `dss`, để
    Power BI/giao diện khác sử dụng.
7.  **Tái sử dụng thành phần hiện có:** Nếu project đã có database
    connector, logger hoặc config chung thì dùng lại, không tạo bản sao
    không cần thiết.

## 13. Checklist phạm vi tối thiểu

### Nếu chọn Predictive Analytics

-   [ ] Truy vấn Gold và tổng hợp Sales theo tháng.
-   [ ] Tạo baseline và ít nhất một mô hình dự báo đơn giản.
-   [ ] Chia train/test theo thời gian.
-   [ ] Đánh giá bằng MAE và RMSE.
-   [ ] Sinh dự báo cho một số tháng tiếp theo.
-   [ ] Lưu kết quả và metadata vào PostgreSQL.
-   [ ] Hiển thị Actual vs Forecast trên Power BI.
-   [ ] Product Demand Forecasting theo Category là phần mở rộng cơ bản
    nếu đủ thời gian.

### Nếu chọn Association Rule Mining

-   [ ] Truy vấn dữ liệu giao dịch có Order ID và Product ID.
-   [ ] Làm sạch và loại trùng sản phẩm trong từng đơn hàng.
-   [ ] Tạo transaction/basket.
-   [ ] Chạy Apriori hoặc FP-Growth.
-   [ ] Sinh luật và tính Support, Confidence, Lift.
-   [ ] Lọc và diễn giải một số luật tiêu biểu.
-   [ ] Lưu kết quả và metadata vào PostgreSQL.
-   [ ] Hiển thị luật và tên sản phẩm trên Power BI hoặc giao diện DSS.

**Quyết định cuối cùng:** Chỉ triển khai checklist tương ứng với hướng
DSS mà nhóm lựa chọn. Không tạo module của hướng còn lại để giữ phạm vi
gọn, dễ kiểm thử và dễ trình bày.
