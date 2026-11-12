"""
DSS Association Rule Mining Pipeline (Market Basket Analysis)
Discovers frequently co-purchased product pairs in orders,
evaluates Support, Confidence, Lift, and persists to dss schema.
"""

import argparse
from sqlalchemy import text
from collections import defaultdict
from itertools import combinations

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql
from src.pipeline.reader import read_sql

def extract_baskets(engine, level="product"):
    variant = "product" if level == "product" else "subcategory"
    sql = read_sql(f"dss/association/baskets_by_{variant}.sql")
    return query_sql(engine, sql)

def mine_association_rules(df, min_support=0.0001, min_confidence=0.10, min_lift=1.2, min_count=2):
    # Group items by order_id
    baskets = df.groupby("order_id")["item_name"].apply(set).tolist()
    total_tx = len(baskets)
    if total_tx == 0:
        return 0, []

    item_counts = defaultdict(int)
    pair_counts = defaultdict(int)

    for b in baskets:
        for item in b:
            item_counts[item] += 1
        for p1, p2 in combinations(sorted(b), 2):
            pair_counts[(p1, p2)] += 1

    rules = []
    for (p1, p2), count in pair_counts.items():
        if count < min_count:
            continue
        support = count / total_tx
        if support < min_support:
            continue

        # Rule 1: p1 -> p2
        conf_1 = count / item_counts[p1]
        lift_1 = conf_1 / (item_counts[p2] / total_tx)
        if conf_1 >= min_confidence and lift_1 >= min_lift:
            rules.append({
                "antecedent": p1,
                "consequent": p2,
                "support": round(support, 6),
                "confidence": round(conf_1, 4),
                "lift": round(lift_1, 2)
            })

        # Rule 2: p2 -> p1
        conf_2 = count / item_counts[p2]
        lift_2 = conf_2 / (item_counts[p1] / total_tx)
        if conf_2 >= min_confidence and lift_2 >= min_lift:
            rules.append({
                "antecedent": p2,
                "consequent": p1,
                "support": round(support, 6),
                "confidence": round(conf_2, 4),
                "lift": round(lift_2, 2)
            })

    rules = sorted(rules, key=lambda x: x["lift"], reverse=True)
    return total_tx, rules

def persist_rules(engine, total_tx, rules, min_support, min_confidence, min_lift):
    with engine.begin() as conn:
        run_id = conn.execute(text(read_sql("dss/association/insert_run.sql")), {"min_supp": min_support, "min_conf": min_confidence,
               "min_lift": min_lift, "tx_cnt": total_tx,
               "rules_cnt": len(rules)}).scalar_one()
        if rules:
            conn.execute(text(read_sql("dss/association/insert_rule.sql")), [{"run_id": run_id, "ant": r["antecedent"][:20],
                    "con": r["consequent"][:20],
                    "ant_name": r["antecedent"], "con_name": r["consequent"],
                    "supp": r["support"], "conf": r["confidence"],
                    "lift": r["lift"]} for r in rules])
    print(f"Persisted {len(rules)} association rules to dss schema under run #{run_id}.")
    return run_id

def main():
    parser = argparse.ArgumentParser(description="Market Basket Analysis")
    parser.add_argument("--algorithm", type=str, default="apriori")
    parser.add_argument("--level", type=str, default="product", choices=["product", "sub_category"])
    parser.add_argument("--min-support", type=float, default=0.0001)
    parser.add_argument("--min-confidence", type=float, default=0.10)
    parser.add_argument("--min-lift", type=float, default=1.2)
    parser.add_argument("--min-count", type=int, default=2)
    args = parser.parse_args()

    engine = create_db_engine()
    print("=" * 60)
    print("RUNNING MARKET BASKET & ASSOCIATION RULE MINING")
    print(f"Parameters: Level={args.level.upper()} | Min Count={args.min_count} | Min Confidence={args.min_confidence*100}% | Min Lift={args.min_lift}")
    print("=" * 60)

    df = extract_baskets(engine, level=args.level)
    total_tx, rules = mine_association_rules(
        df,
        min_support=args.min_support,
        min_confidence=args.min_confidence,
        min_lift=args.min_lift,
        min_count=args.min_count
    )

    print(f"\nAnalyzed {total_tx} transactions. Discovered {len(rules)} valid rules.")
    print("-" * 60)
    for i, r in enumerate(rules[:10]):
        print(f"[{i+1}] {r['antecedent']}  --->  {r['consequent']}")
        print(f"    Support: {r['support']*100:.2f}% | Confidence: {r['confidence']*100:.1f}% | Lift: {r['lift']:.2f}")

    persist_rules(engine, total_tx, rules, args.min_support, args.min_confidence, args.min_lift)
    print("=" * 60)

if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
