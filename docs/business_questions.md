# Câu hỏi nghiệp vụ và định hướng DSS -- Global Superstore

Tài liệu tổng hợp 3 nhóm câu hỏi nghiệp vụ chính cho bài tập Data
Warehouse + Decision Support System (DSS) sử dụng bộ dữ liệu **Global
Superstore**.

## 1. Sales Performance -- Hiệu quả kinh doanh

**Mục tiêu:** Đánh giá tình hình doanh thu, lợi nhuận và hiệu quả kinh
doanh theo thời gian, khu vực và danh mục sản phẩm.

  -----------------------------------------------------------------------
  ID                                  Câu hỏi nghiệp vụ
  ----------------------------------- -----------------------------------
  S01                                 Doanh thu và lợi nhuận thay đổi như
                                      thế nào theo thời gian?

  S02                                 Tốc độ tăng trưởng doanh thu và lợi
                                      nhuận theo tháng, quý, năm là bao
                                      nhiêu?

  S03                                 Khu vực, quốc gia hoặc thành phố
                                      nào có doanh thu và lợi nhuận cao
                                      nhất/thấp nhất?

  S04                                 Những khu vực nào có doanh thu cao
                                      nhưng lợi nhuận thấp hoặc âm?

  S05                                 Danh mục sản phẩm nào đóng góp
                                      nhiều nhất vào tổng doanh thu và
                                      lợi nhuận?

  S06                                 Mức chiết khấu ảnh hưởng như thế
                                      nào đến doanh thu và lợi nhuận?

  S07                                 Những giai đoạn nào có hiệu quả
                                      kinh doanh thấp bất thường?
  -----------------------------------------------------------------------

**Hướng DSS có thể triển khai:**

-   **What-if Analysis:** Mô phỏng ảnh hưởng của các mức chiết khấu đến
    lợi nhuận.
-   **Sales Forecasting:** Dự báo doanh thu và lợi nhuận trong các kỳ
    tiếp theo.
-   **Correlation Analysis:** Phân tích mối tương quan giữa Discount,
    Sales và Profit.

## 2. Product Performance -- Hiệu quả sản phẩm

**Mục tiêu:** Đánh giá hiệu suất của từng sản phẩm, danh mục sản phẩm và
hỗ trợ quyết định về danh mục kinh doanh.

  -----------------------------------------------------------------------
  ID                                  Câu hỏi nghiệp vụ
  ----------------------------------- -----------------------------------
  P01                                 Những sản phẩm nào có doanh thu cao
                                      nhất/thấp nhất?

  P02                                 Những sản phẩm nào có lợi nhuận cao
                                      nhất/thấp nhất?

  P03                                 Sản phẩm nào bán chạy nhưng có lợi
                                      nhuận thấp hoặc âm?

  P04                                 Danh mục và phân nhóm sản phẩm nào
                                      đóng góp nhiều nhất vào doanh thu,
                                      lợi nhuận?

  P05                                 Sản phẩm nào có số lượng bán cao
                                      nhưng doanh thu thấp?

  P06                                 Hiệu quả kinh doanh của sản phẩm
                                      thay đổi như thế nào theo thời
                                      gian?

  P07                                 Sản phẩm nào thường được mua cùng
                                      nhau trong một đơn hàng?

  P08                                 Hiệu quả của một sản phẩm có khác
                                      biệt giữa các khu vực không?
  -----------------------------------------------------------------------

**Hướng DSS có thể triển khai:**

-   **ABC Analysis:** Phân loại sản phẩm theo mức độ đóng góp doanh thu
    hoặc lợi nhuận.
-   **Product Portfolio Analysis:** Phân nhóm sản phẩm theo hai tiêu chí
    Sales và Profit.
-   **Market Basket Analysis:** Tìm các sản phẩm thường xuất hiện cùng
    nhau trong một đơn hàng bằng Apriori.
-   **Product Clustering:** Phân nhóm sản phẩm theo đặc trưng kinh
    doanh.

## 3. Customer Analytics -- Phân tích khách hàng

**Mục tiêu:** Hiểu hành vi mua hàng, giá trị đóng góp và phân khúc khách
hàng để hỗ trợ chiến lược kinh doanh.

  -----------------------------------------------------------------------
  ID                                  Câu hỏi nghiệp vụ
  ----------------------------------- -----------------------------------
  C01                                 Những khách hàng nào đóng góp doanh
                                      thu và lợi nhuận nhiều nhất?

  C02                                 Khách hàng nào có tổng giá trị mua
                                      hàng cao nhất/thấp nhất?

  C03                                 Tần suất mua hàng và giá trị trung
                                      bình mỗi đơn hàng của khách hàng
                                      như thế nào?

  C04                                 Khách hàng thường mua những danh
                                      mục sản phẩm nào?

  C05                                 Doanh thu và lợi nhuận phân bố như
                                      thế nào giữa các phân khúc khách
                                      hàng?

  C06                                 Bao nhiêu phần trăm doanh thu đến
                                      từ nhóm khách hàng đóng góp cao
                                      nhất?

  C07                                 Những khách hàng nào có dấu hiệu
                                      giảm mức độ mua hàng theo thời
                                      gian?
  -----------------------------------------------------------------------

**Hướng DSS có thể triển khai:**

-   **RFM Analysis:** Phân khúc khách hàng dựa trên Recency, Frequency
    và Monetary.
-   **Customer Clustering:** Sử dụng K-Means để phân nhóm khách hàng
    theo hành vi mua hàng.
-   **Pareto Analysis:** Xác định nhóm khách hàng đóng góp phần lớn
    doanh thu.
-   **Customer Behavior Analysis:** Phân tích xu hướng và thay đổi hành
    vi mua hàng.

## 4. Tổng hợp phạm vi triển khai

  -----------------------------------------------------------------------
  Data Mart               Trọng tâm               DSS đề xuất
  ----------------------- ----------------------- -----------------------
  Sales Performance       Doanh thu, lợi nhuận,   What-if, Forecasting
                          tăng trưởng             

  Product Performance     Hiệu quả sản phẩm, danh ABC, Portfolio, Market
                          mục                     Basket

  Customer Analytics      Giá trị và hành vi      RFM, K-Means, Pareto
                          khách hàng              
  -----------------------------------------------------------------------

## 5. Lưu ý về dữ liệu

-   **Sales:** Có Order Date, Ship Date, Sales, Profit, Discount nên có
    thể phân tích hiệu quả kinh doanh.
-   **Product:** Có Product ID, Category, Sub-Category, Product Name,
    Quantity nên có thể phân tích hiệu suất sản phẩm.
-   **Customer:** Có Customer ID, Segment, Order ID và Order Date nên có
    thể xây dựng RFM.
-   **Churn:** Dataset không có trạng thái ngừng sử dụng dịch vụ hoặc dữ
    liệu tương tác khách hàng. Vì vậy, chỉ nên phân tích dấu hiệu giảm
    tần suất mua hàng, không khẳng định chính xác khách hàng đã rời bỏ.

## 6. Đề xuất triển khai

Với phạm vi bài tập, nên ưu tiên 3 dashboard tương ứng với 3 nhóm nghiệp
vụ trên, đồng thời chọn khoảng 3--4 chức năng DSS có chiều sâu thay vì
cố triển khai tất cả thuật toán.

Một hướng triển khai hợp lý:

1.  **Sales:** Dashboard doanh thu/lợi nhuận kết hợp What-if Analysis
    hoặc Forecasting.
2.  **Product:** Dashboard hiệu quả sản phẩm kết hợp Product Portfolio
    hoặc ABC Analysis.
3.  **Customer:** Dashboard phân khúc khách hàng kết hợp RFM Analysis.

Các thuật toán phân tích nâng cao có thể được triển khai bằng Python,
sau đó lưu kết quả vào PostgreSQL để Power BI khai thác và trực quan
hóa.
