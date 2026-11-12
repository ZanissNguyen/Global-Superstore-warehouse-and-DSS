# Application & Presentation Layer (`src/app/`)

This directory houses the interactive frontend applications and backend REST API services for the Global Superstore Data Warehouse & Decision Support System (DSS).

## Structure

```text
src/app/
├── README.md               # Documentation and execution instructions
├── main.py                 # Streamlit Interactive DSS Web Application
└── api/
    ├── __init__.py
    └── main.py             # FastAPI REST Backend Service
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

### 2. FastAPI REST Backend Service
Launch the REST API server:
```bash
uvicorn src.app.api.main:app --reload --port 8000
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

Endpoints:
- `GET /api/health/live`: API process liveness (does not query PostgreSQL).
- `GET /api/health/ready`: Read-only check of the UI-selected database and required Gold tables; HTTP 503 if unavailable.
- `GET /api/health`: Backward-compatible alias of the readiness check.
- `GET /api/kpi/summary`: Executive KPI metrics from Gold layer.
- `GET /api/olap/sales-trend`: Monthly sales and profit time series.
- `POST /api/dss/what-if`: What-if discount simulation engine.
- `GET /api/dss/forecast`: Time-series forecasting points and prediction intervals.
- `GET /api/dss/association-rules`: Discovered cross-selling association rules.
