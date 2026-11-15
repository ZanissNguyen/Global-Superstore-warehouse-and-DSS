# Application & Presentation Layer (`src/app/`)

This directory houses the interactive frontend application for the Global Superstore Data Warehouse & Decision Support System (DSS).

## Structure

```text
src/app/
├── README.md               # Documentation and execution instructions
└── main.py                 # Streamlit Interactive DSS Web Application
```

## Running the Applications

### 1. Interactive Streamlit DSS Web App
Launch the interactive decision support dashboard:
```bash
streamlit run src/app/main.py
```
Open your browser at `http://localhost:8501`.

Features:
- **Tab 1: Executive KPIs & Hotspots:** Real-time KPI scorecards and risk alerts on loss-making markets/categories.
- **Tab 2: What-If Simulation Sandbox:** Interactive sliders to adjust discount rates and elasticity, comparing baseline vs. simulated profit with automated prescriptive recommendations.
- **Tab 3: Sales Forecasting:** Historical sales vs. 6-month forecast with 95% confidence intervals and accuracy metrics (MAE, RMSE, MAPE).
- **Tab 4: Market Basket & Cross-Selling:** Discovered association rules with Lift > 1.2 and suggested bundling strategies.
