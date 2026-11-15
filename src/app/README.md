# Application & Presentation Layer (`src/app/`)

This directory houses the interactive frontend application for the Global Superstore Data Warehouse & Decision Support System (DSS).

## Structure

```text
src/app/
├── README.md               # Documentation and execution instructions
├── main.py                 # Streamlit entry point: layout, tabs, database scope
├── executive.py            # Tab 1: executive KPI scorecards and hotspots
├── whatif.py               # Tab 2: what-if discount simulation
├── forecast.py             # Tab 3: sales forecast (Holt-Winters vs seasonal naive)
├── crosssell.py            # Tab 4: association rules & cross-sell suggestions
├── upload.py               # Tab 5: upload & reconciliation screen
├── demo_backend.py         # Upload validation, candidate DB clone, ETL orchestration
└── export_for_powerbi.py   # Export Gold/DSS tables to CSV for Power BI
```

## Running the Applications

### 1. Interactive Streamlit DSS Web App
Launch the interactive decision support dashboard:
```bash
python -m streamlit run src/app/main.py
```
Open your browser at `http://localhost:8501`.

Features (5 tabs):
- **Tab 1: Tổng quan kinh doanh (Executive KPIs & Hotspots):** KPI scorecards and risk alerts on loss-making markets/categories.
- **Tab 2: Quyết định giá và chiết khấu (What-If Simulation Sandbox):** Interactive sliders to adjust discount rates and elasticity, comparing baseline vs. simulated profit with automated prescriptive recommendations.
- **Tab 3: Kế hoạch doanh thu và dự báo (Sales Forecasting):** Historical sales vs. 6-month/3-month forecasts with accuracy metrics (MAE, RMSE, MAPE, WMAPE). The prediction intervals are **not** calibrated to 95% confidence (see `forecast.py`).
- **Tab 4: Cơ hội bán kèm (Market Basket & Cross-Selling):** Discovered association rules with lift/confidence filters and suggested bundling strategies.
- **Tab 5: Nạp dữ liệu và đối soát (Upload & Reconciliation):** Upload a CSV/Excel file, preview it, run the ETL on an isolated candidate database, and compare before/after metrics; the base database is only replaced after reconciliation succeeds.
