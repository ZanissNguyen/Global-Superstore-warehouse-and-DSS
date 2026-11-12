"""
DSS Module: What-If Discount & Profit Simulation Engine
Simulates the effect of adjusting discount rates on sales volume, revenue,
and net profit based on Price Elasticity of Demand (e).
"""

import sys
from typing import Dict, Any, Optional, Tuple
from src.pipeline.reader import read_sql

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def fetch_baseline_from_db(market: Optional[str] = None, category: Optional[str] = None) -> Tuple[float, float, float]:
    """
    Fetch baseline sales, profit, and avg discount from Gold schema fact and dimensions.
    """
    from src.pipeline.database import create_db_engine
    from src.pipeline.executor import query_sql
    engine = create_db_engine()
    try:
        sql = read_sql("gold/whatif/fetch_baseline.sql")
        params = {
            "market": market.strip() if market and market.lower() != "all" else None,
            "category": category.strip() if category and category.lower() != "all" else None,
        }
        df = query_sql(engine, sql, params)
        row = df.iloc[0]
        if float(row["total_sales"]) <= 0:
            raise ValueError("Không có doanh thu Gold trong bộ lọc đã chọn.")
        return (float(row["total_sales"]), float(row["total_profit"]),
                float(row["avg_discount"]))
    finally:
        engine.dispose()

def run_what_if_simulation(
    baseline_sales: float,
    baseline_profit: float,
    baseline_discount: float,
    discount_adjustment: float,
    elasticity: float = 1.4,
    shipping_ratio: float = 0.08
) -> Dict[str, Any]:
    """
    Run what-if scenario.
    discount_adjustment: e.g. +0.05 for +5% additional discount
    elasticity: Price Elasticity of Demand (e > 1 is elastic)
    """
    new_discount = max(0.0, min(0.85, baseline_discount + discount_adjustment))
    
    # Percentage price change: delta_P / P = ( (1 - d_new) - (1 - d_old) ) / (1 - d_old)
    denom = max(0.01, 1.0 - baseline_discount)
    pct_price_change = ((1.0 - new_discount) - denom) / denom
    
    # Expected demand change: delta_Q / Q = - elasticity * (delta_P / P)
    pct_demand_change = -elasticity * pct_price_change
    
    # Simulated sales: Sales_new = Sales_base * (1 + delta_Q/Q) * (1 - d_new) / (1 - d_old)
    simulated_sales = max(0.0, baseline_sales * (1.0 + pct_demand_change) * (1.0 - new_discount) / denom)
    
    # Baseline cost structure estimation
    baseline_cost = baseline_sales - baseline_profit
    # Variable cost increases proportional to unit volume
    simulated_cost = baseline_cost * (1.0 + pct_demand_change)
    simulated_profit = simulated_sales - simulated_cost
    
    baseline_margin = (baseline_profit / baseline_sales * 100) if baseline_sales > 0 else 0
    simulated_margin = (simulated_profit / simulated_sales * 100) if simulated_sales > 0 else 0
    
    sales_diff_pct = ((simulated_sales - baseline_sales) / baseline_sales * 100) if baseline_sales > 0 else 0
    profit_diff_pct = ((simulated_profit - baseline_profit) / abs(baseline_profit) * 100) if baseline_profit != 0 else 0
    
    # Prescriptive Recommendation Rule
    if simulated_margin < 5.0 or simulated_profit < 0:
        status = "[!] WARNING / REJECT"
        message = (
            f"Tăng chiết khấu làm xói mòn lợi nhuận ròng (lợi nhuận giảm {profit_diff_pct:.1f}%), "
            f"biên lợi nhuận chỉ còn {simulated_margin:.2f}%. Không khuyến nghị áp dụng!"
        )
    elif simulated_profit < baseline_profit:
        status = "[*] CAUTION"
        message = (
            f"Doanh số tăng {sales_diff_pct:.1f}% nhưng không đủ bù đắp mức giảm giá bán. "
            f"Lợi nhuận giảm ${abs(simulated_profit - baseline_profit):,.2f} ({profit_diff_pct:.1f}%). "
            f"Không khuyến nghị áp dụng nếu mục tiêu là tối đa hóa lợi nhuận."
        )
    else:
        status = "[+] APPROVE / VIABLE"
        message = (
            f"KỊCH BẢN KHẢ THI! Lợi nhuận ròng tăng ${simulated_profit - baseline_profit:,.2f} (+{profit_diff_pct:.1f}%), "
            f"biên lợi nhuận an toàn ({simulated_margin:.2f}%). Khuyến nghị phê duyệt."
        )

    return {
        "baseline": {
            "sales": round(baseline_sales, 2),
            "profit": round(baseline_profit, 2),
            "discount_pct": round(baseline_discount * 100, 2),
            "margin_pct": round(baseline_margin, 2)
        },
        "simulated": {
            "sales": round(simulated_sales, 2),
            "profit": round(simulated_profit, 2),
            "discount_pct": round(new_discount * 100, 2),
            "margin_pct": round(simulated_margin, 2),
            "sales_change_pct": round(sales_diff_pct, 2),
            "profit_change_pct": round(profit_diff_pct, 2)
        },
        "recommendation": {
            "status": status,
            "message": message
        }
    }

def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="What-If Simulation CLI")
    parser.add_argument("--market", type=str, default=None, help="Geographic market filter (e.g. APAC, EU, US)")
    parser.add_argument("--category", type=str, default=None, help="Product category filter (e.g. Furniture, Technology)")
    parser.add_argument("--discount", type=float, default=None, help="Discount adjustment (+0.05 for +5%)")
    parser.add_argument("--discount-adj", type=float, default=None, help="Alias for --discount")
    parser.add_argument("--elasticity", type=float, default=1.4, help="Price elasticity of demand (e > 1 is elastic)")
    parser.add_argument("--sales", type=float, default=None, help="Manual override for baseline sales")
    parser.add_argument("--profit", type=float, default=None, help="Manual override for baseline profit")
    parser.add_argument("--base-discount", type=float, default=None, help="Manual override for baseline discount")
    parser.add_argument("--json", action="store_true", help="Output pure JSON format")
    args = parser.parse_args()

    # Determine discount adjustment
    if args.discount is not None:
        discount_adj = args.discount
    elif args.discount_adj is not None:
        discount_adj = args.discount_adj
    else:
        discount_adj = 0.05

    # Determine baseline values (from DB or manual override)
    if args.sales is not None and args.profit is not None:
        b_sales = args.sales
        b_profit = args.profit
        b_discount = args.base_discount if args.base_discount is not None else 0.15
    else:
        b_sales, b_profit, b_discount = fetch_baseline_from_db(market=args.market, category=args.category)
        if args.base_discount is not None:
            b_discount = args.base_discount

    res = run_what_if_simulation(
        baseline_sales=b_sales,
        baseline_profit=b_profit,
        baseline_discount=b_discount,
        discount_adjustment=discount_adj,
        elasticity=args.elasticity
    )

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        tgt_market = args.market if args.market else "Global"
        tgt_category = args.category if args.category else "All Categories"
        b = res["baseline"]
        s = res["simulated"]
        r = res["recommendation"]
        print("=" * 60)
        print("              WHAT-IF DECISION SIMULATION REPORT")
        print("=" * 60)
        print(f"Target: Market = {tgt_market} | Category = {tgt_category}")
        print(f"Parameters: Discount Adjustment = {discount_adj*100:+.1f}% | Elasticity = {args.elasticity:.2f}")
        print()
        print("[BASELINE CURRENT STATE]")
        print(f"  - Sales:        ${b['sales']:>14,.2f}")
        print(f"  - Net Profit:   ${b['profit']:>14,.2f}")
        print(f"  - Profit Margin:{b['margin_pct']:>13.2f}%")
        print(f"  - Base Discount:{b['discount_pct']:>13.2f}%")
        print()
        print("[SIMULATED SCENARIO]")
        print(f"  - Expected Sales:  ${s['sales']:>11,.2f} ({s['sales_change_pct']:+.2f}%)")
        print(f"  - Expected Profit: ${s['profit']:>11,.2f} ({s['profit_change_pct']:+.2f}%)")
        print(f"  - Expected Margin:     {s['margin_pct']:>9.2f}% ({s['margin_pct'] - b['margin_pct']:+.2f}%)")
        print()
        print("[DECISION RECOMMENDATION]")
        print(f"  {r['status']}: {r['message']}")
        print("=" * 60)

if __name__ == "__main__":
    main()
