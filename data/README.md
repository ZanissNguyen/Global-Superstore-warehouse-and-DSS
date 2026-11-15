## 1. Dữ liệu đầu vào (Datasets)

Dự án sử dụng hai bộ dữ liệu đơn hàng của **Superstore Global**, được tải từ Kaggle:

| Bộ dữ liệu | Nguồn tải | Số lượng bản ghi | Giai đoạn dữ liệu |
|---|---|---:|---|
| `Global Superstore.xls` | [Kaggle – Global Superstore](https://www.kaggle.com/datasets/shekpaul/global-superstore) | Khoảng 51.000 | 2011–2014 |
| `Sample - Superstore.csv` | [Kaggle – Superstore Dataset Final](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final/data) | Khoảng 10.000 | 2014–2018 |

Bộ dữ liệu thứ nhất cung cấp dữ liệu đơn hàng trong giai đoạn 2011–2014, được sử dụng làm nguồn dữ liệu chính để xây dựng và kiểm thử quy trình ETL, kho dữ liệu và các thành phần phân tích nghiệp vụ.

Bộ dữ liệu thứ hai chứa số lượng bản ghi ít hơn, thuộc giai đoạn 2014–2018. Bộ dữ liệu này có thể được sử dụng để kiểm thử khả năng **nạp bổ sung dữ liệu mới (incremental data loading)** vào kho dữ liệu, đồng thời đánh giá khả năng xử lý dữ liệu phát sinh từ một đợt nhập dữ liệu mới.

*Lưu ý: Số lượng bản ghi và phạm vi thời gian được ghi nhận theo thông tin hiện có; cần đối chiếu với dữ liệu thực tế sau khi tải và xử lý.*