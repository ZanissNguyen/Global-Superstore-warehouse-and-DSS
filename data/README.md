## 1. Dữ liệu đầu vào (Datasets)

Dự án sử dụng hai bộ dữ liệu đơn hàng của **Superstore Global**, được tải từ Kaggle và lưu trong `data/raw/`:

| File | Bộ dữ liệu | Nguồn tải | Số lượng bản ghi | Giai đoạn dữ liệu |
|---|---|---|---:|---|
| `Global_Superstore.xls` | Global Superstore | [Kaggle – Global Superstore](https://www.kaggle.com/datasets/shekpaul/global-superstore) | 51.290 | 2011–2014 |
| `Sample-Superstore.csv` | Sample – Superstore | [Kaggle – Superstore Dataset Final](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final/data) | 9.994 | 2014–2017 |
| `Sample-Superstore.xlsx` | Sample – Superstore (bản chuyển đổi) | Cùng nguồn với file CSV trên | 9.994 | 2014–2017 |

`Global_Superstore.xls` cung cấp dữ liệu đơn hàng trong giai đoạn 2011–2014, được sử dụng làm nguồn dữ liệu chính để xây dựng và kiểm thử quy trình ETL, kho dữ liệu và các thành phần phân tích nghiệp vụ.

`Sample-Superstore.csv` chứa số lượng bản ghi ít hơn, thuộc giai đoạn 2014–2017. Bộ dữ liệu này được sử dụng để kiểm thử khả năng **nạp bổ sung dữ liệu mới (incremental data loading)** vào kho dữ liệu, đồng thời đánh giá khả năng xử lý dữ liệu phát sinh từ một đợt nhập dữ liệu mới.

`Sample-Superstore.xlsx` là bản chuyển đổi của file CSV: các cột ngày (`Order Date`, `Ship Date`) đã được chuyển từ số serial Excel sang ngày thật (origin 1899-12-30), và **Row ID đã được chỉnh về dải 51291–61284** để nạp bổ sung không trùng với dữ liệu nền (Row ID 1–51290). Đây là file mặc định của demo incremental (`src/etl/incremental/demo_incremental.py`) và có thể tải lên qua tab **Nạp dữ liệu và đối soát** trong UI.

*Lưu ý: Số lượng bản ghi và phạm vi thời gian được ghi nhận theo thông tin hiện có; cần đối chiếu với dữ liệu thực tế sau khi tải và xử lý.*
