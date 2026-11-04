"""
Generate Incremental Test Dataset for Global Superstore
Creates a realistic 500-record batch representing Q1 2015 orders.
"""

from pathlib import Path
import random
import pandas as pd

def generate_incremental_batch(
    base_dataset_path: str = "dataset/superstore_dataset2011-2015.csv",
    output_path: str = "dataset/incremental_orders_2015_q1.csv",
    num_records: int = 500
):
    print(f"Reading sample metadata from {base_dataset_path}...")
    base_df = pd.read_csv(base_dataset_path, encoding="latin1")

    # Sample reference entities
    customers = base_df[["Customer ID", "Customer Name", "Segment"]].drop_duplicates().to_dict("records")
    products = base_df[["Product ID", "Category", "Sub-Category", "Product Name"]].drop_duplicates().to_dict("records")
    geos = base_df[["City", "State", "Country", "Postal Code", "Market", "Region"]].drop_duplicates().to_dict("records")
    ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    priorities = ["Low", "Medium", "High", "Critical"]

    random.seed(42)
    rows = []

    start_row_id = 60001
    current_order_num = 10001
    
    # We will generate about num_records with multi-item orders
    i = 0
    while i < num_records:
        order_size = random.choice([1, 2, 2, 3, 4])
        order_size = min(order_size, num_records - i)
        
        geo = random.choice(geos)
        cust = random.choice(customers)
        ship_mode = random.choice(ship_modes)
        priority = random.choice(priorities)
        
        market_prefix = {
            "APAC": "IN",
            "EU": "ES",
            "US": "CA",
            "LATAM": "MX",
            "EMEA": "IT",
            "Africa": "EG"
        }.get(geo["Market"], "GL")
        order_id = f"{market_prefix}-2015-{current_order_num}"
        current_order_num += 1

        # Dates in Q1 2015
        day = random.randint(1, 28)
        month = random.randint(1, 3)
        order_date_str = f"{day:02d}/{month:02d}/2015"
        ship_day = day + random.randint(1, 5)
        if ship_day > 28:
            ship_day = ship_day - 28
            ship_month = month + 1
        else:
            ship_month = month
        ship_date_str = f"{ship_day:02d}/{ship_month:02d}/2015"

        for _ in range(order_size):
            prod = random.choice(products)
            qty = random.randint(1, 10)
            base_price = random.uniform(15.0, 500.0)
            discount = random.choice([0.0, 0.0, 0.1, 0.15, 0.2, 0.3])
            sales = round(qty * base_price * (1.0 - discount), 2)
            cost = round(sales * random.uniform(0.65, 0.90), 2)
            profit = round(sales - cost, 2)
            shipping_cost = round(random.uniform(3.0, 45.0), 2)

            rows.append({
                "Row ID": start_row_id,
                "Order ID": order_id,
                "Order Date": order_date_str,
                "Ship Date": ship_date_str,
                "Ship Mode": ship_mode,
                "Customer ID": cust["Customer ID"],
                "Customer Name": cust["Customer Name"],
                "Segment": cust["Segment"],
                "City": geo["City"],
                "State": geo["State"],
                "Country": geo["Country"],
                "Postal Code": geo["Postal Code"],
                "Market": geo["Market"],
                "Region": geo["Region"],
                "Product ID": prod["Product ID"],
                "Category": prod["Category"],
                "Sub-Category": prod["Sub-Category"],
                "Product Name": prod["Product Name"],
                "Sales": sales,
                "Quantity": qty,
                "Discount": discount,
                "Profit": profit,
                "Shipping Cost": shipping_cost,
                "Order Priority": priority
            })
            start_row_id += 1
            i += 1

    out_df = pd.DataFrame(rows)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False, encoding="latin1")
    print(f"Generated {len(out_df)} incremental rows saved to: {out_path}")
    print(f"Row IDs: {out_df['Row ID'].min()} to {out_df['Row ID'].max()}")
    print(f"Total Sales in batch: ${out_df['Sales'].sum():,.2f}")
    print(f"Total Profit in batch: ${out_df['Profit'].sum():,.2f}")

if __name__ == "__main__":
    generate_incremental_batch()
