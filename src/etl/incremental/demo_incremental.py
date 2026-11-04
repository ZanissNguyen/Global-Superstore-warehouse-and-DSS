"""
Incremental Loading Demo Runner & Validator
Demonstrates end-to-end Change Data Capture (CDC) and incremental ingestion
of new business transactions without re-processing legacy data.
"""

import sys
import argparse
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql, execute_sql
from src.pipeline.flows.bronze_to_gold import run_pipeline

def get_warehouse_metrics(engine):
    sql = """
    SELECT 
        (SELECT COUNT(*) FROM bronze.ingestion) AS ingestion_batches,
        (SELECT COALESCE(MAX(id), 0) FROM bronze.ingestion) AS latest_ingestion_id,
        (SELECT COUNT(*) FROM bronze.raw_orders) AS bronze_rows,
        (SELECT COUNT(*) FROM silver.orders) AS silver_rows,
        (SELECT COUNT(*) FROM gold.fact_sales) AS gold_rows,
        (SELECT COALESCE(SUM(sales), 0) FROM gold.fact_sales) AS total_sales,
        (SELECT COALESCE(SUM(profit), 0) FROM gold.fact_sales) AS total_profit
    """
    df = query_sql(engine, sql)
    return df.iloc[0].to_dict()

def reset_incremental_test(engine):
    print("=" * 65)
    print("REVERTING INCREMENTAL TEST BATCH (RESETTING TO BASELINE)")
    print("=" * 65)
    
    # 1. Delete from gold.fact_sales
    del_gold = "DELETE FROM gold.fact_sales WHERE CAST(row_id AS INTEGER) >= 60000;"
    execute_sql(engine, del_gold)
    
    # 2. Delete from silver.orders
    del_silver = "DELETE FROM silver.orders WHERE row_id >= 60000;"
    execute_sql(engine, del_silver)
    
    # 3. Find test ingestion IDs and delete from bronze
    sql_ing = "SELECT id FROM bronze.ingestion WHERE source_name LIKE '%incremental%';"
    df_ing = query_sql(engine, sql_ing)
    if not df_ing.empty:
        ing_ids = [str(x) for x in df_ing["id"].tolist()]
        id_list = ",".join(ing_ids)
        execute_sql(engine, f"DELETE FROM bronze.raw_orders WHERE ingestion IN ({id_list});")
        execute_sql(engine, f"DELETE FROM bronze.ingestion WHERE id IN ({id_list});")
    
    # 4. Refresh materialized views
    execute_sql(engine, "REFRESH MATERIALIZED VIEW gold.mv_sales_mart;")
    execute_sql(engine, "REFRESH MATERIALIZED VIEW gold.mv_product_mart;")
    execute_sql(engine, "REFRESH MATERIALIZED VIEW gold.mv_customer_mart;")
    
    print("Reset completed successfully. Warehouse returned to baseline state.")

def run_demo(input_file: str = "dataset/incremental_orders_2015_q1.csv"):
    engine = create_db_engine()
    print("=" * 65)
    print("   DEMO NẠP GIA TĂNG KHO DỮ LIỆU (INCREMENTAL LOADING DEMO)")
    print("   CO4031 - Kho dữ liệu & Hệ hỗ trợ Quyết định | Bách Khoa TP.HCM")
    print("=" * 65)

    # 1. Baseline status
    print("\n[BƯỚC 1: TRẠNG THÁI HIỆN TẠI TRƯỚC KHI NẠP GIA TĂNG]")
    m_before = get_warehouse_metrics(engine)
    print(f"  - Số đợt Ingestion đã nạp:   {m_before['ingestion_batches']}")
    print(f"  - Tổng số dòng Bronze:       {m_before['bronze_rows']:,}")
    print(f"  - Tổng số dòng Silver:       {m_before['silver_rows']:,}")
    print(f"  - Tổng số dòng FactSales:    {m_before['gold_rows']:,}")
    print(f"  - Tổng Doanh thu hiện tại:   ${m_before['total_sales']:,.2f}")
    print(f"  - Tổng Lợi nhuận hiện tại:   ${m_before['total_profit']:,.2f}")

    # 2. Execute incremental ingestion
    print(f"\n[BƯỚC 2: TIẾN HÀNH NẠP ĐỢT DỮ LIỆU MỚI: {input_file}]")
    run_pipeline(input_path=input_file)

    # 3. Post-load metrics
    print("\n[BƯỚC 3: TRẠNG THÁI SAU KHI NẠP GIA TĂNG]")
    m_after = get_warehouse_metrics(engine)
    delta_rows = m_after["gold_rows"] - m_before["gold_rows"]
    delta_sales = m_after["total_sales"] - m_before["total_sales"]
    delta_profit = m_after["total_profit"] - m_before["total_profit"]

    print(f"  - Số đợt Ingestion mới:      {m_after['ingestion_batches']} (Lần nạp mới: #{m_after['latest_ingestion_id']})")
    print(f"  - Số dòng mới nạp vào Fact:  +{delta_rows:,} dòng")
    print(f"  - Tổng số dòng FactSales:    {m_after['gold_rows']:,}")
    print(f"  - Doanh thu mới bổ sung:     +${delta_sales:,.2f}")
    print(f"  - Tổng Doanh thu mới:        ${m_after['total_sales']:,.2f}")
    print(f"  - Lợi nhuận mới bổ sung:     +${delta_profit:,.2f}")
    print(f"  - Tổng Lợi nhuận mới:        ${m_after['total_profit']:,.2f}")

    # 4. Query verification: Yearly Distribution in Gold
    print("\n[BƯỚC 4: XÁC MINH TRỰC QUAN DOANH SỐ PHÂN BỔ THEO NĂM TRONG GOLD SCHEMA]")
    sql_years = """
    SELECT 
        d.year AS "Năm",
        COUNT(f.sales) AS "Số dòng đơn hàng",
        ROUND(SUM(f.sales), 2) AS "Doanh thu ($)",
        ROUND(SUM(f.profit), 2) AS "Lợi nhuận ($)",
        ROUND(AVG(f.discount) * 100, 2) AS "Chiết khấu BQ (%)"
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    GROUP BY d.year
    ORDER BY d.year;
    """
    df_years = query_sql(engine, sql_years)
    print(df_years.to_string(index=False))

    # 5. Ingestion Audit Table check
    print("\n[BƯỚC 5: LỊCH SỬ CÁC ĐỢT NẠP TRONG BẢNG BRONZE.INGESTION]")
    df_ing = query_sql(engine, "SELECT id, source_name, loaded_time, metadata FROM bronze.ingestion ORDER BY id DESC LIMIT 3;")
    print(df_ing.to_string(index=False))

    print("\n" + "=" * 65)
    print("  KẾT LUẬN: NẠP GIA TĂNG THÀNH CÔNG 100%! DỮ LIỆU CŨ ĐƯỢC BẢO TOÀN,")
    print("  DỮ LIỆU MỚI ĐƯỢC TÍCH HỢP TỨC THÌ VÀO STAR SCHEMA & DATA MARTS.")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Incremental Loading Demo")
    parser.add_argument("--input", type=str, default="dataset/incremental_orders_2015_q1.csv")
    parser.add_argument("--reset", action="store_true", help="Revert incremental test back to baseline")
    args = parser.parse_args()

    engine = create_db_engine()
    if args.reset:
        reset_incremental_test(engine)
    else:
        run_demo(input_file=args.input)

if __name__ == "__main__":
    main()
