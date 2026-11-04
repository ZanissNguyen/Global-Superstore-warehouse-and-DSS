"""
DSS Module: What-If Discount & Profit Simulation Engine
Simulates the effect of adjusting discount rates on sales volume, revenue,
and net profit based on Price Elasticity of Demand (e).
"""

from typing import Dict, Any

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
        status = "REJECT / DANGER"
        message = (
            f"TĂNG CHIẾT KHẤU LÀM LỖ VỐN HOẶC BIÊN LỢI NHUẬN RƠI XUỐNG DƯỚI 5% ({simulated_margin:.2f}%). "
            f"Lợi nhuận ròng giảm {profit_diff_pct:.1f}%. Hệ thống khuyến nghị TỪ CHỐI kịch bản này."
        )
    elif simulated_profit < baseline_profit:
        status = "CAUTION"
        message = (
            f"Doanh số tăng {sales_diff_pct:.1f}% nhưng không đủ bù đắp mức giảm giá bán. "
            f"Lợi nhuận giảm ${abs(simulated_profit - baseline_profit):,.2f} ({profit_diff_pct:.1f}%). "
            f"Không khuyến nghị áp dụng nếu mục tiêu là tối đa hóa lợi nhuận."
        )
    else:
        status = "APPROVE / VIABLE"
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

if __name__ == "__main__":
    import argparse
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="What-If Simulation CLI")
    parser.add_argument("--sales", type=float, default=1000000.0)
    parser.add_argument("--profit", type=float, default=120000.0)
    parser.add_argument("--base-discount", type=float, default=0.15)
    parser.add_argument("--discount-adj", type=float, default=0.05)
    parser.add_argument("--elasticity", type=float, default=1.4)
    args = parser.parse_args()

    res = run_what_if_simulation(
        baseline_sales=args.sales,
        baseline_profit=args.profit,
        baseline_discount=args.base_discount,
        discount_adjustment=args.discount_adj,
        elasticity=args.elasticity
    )
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
