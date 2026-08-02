# 🌍 Global Government Budget Analytics Core

An interactive **Streamlit + MySQL** dashboard for exploring global government spending — historical trends, sector-wise allocation, statistical anomalies, and data-driven forecasting, all in one place.

🔗 **Live App:** [global-budget-data-analytics-python-sql-project-bpjag9thn8rpt3.streamlit.app](https://global-budget-data-analytics-python-sql-project-bpjag9thn8rpt3.streamlit.app)

---

## 📌 Overview

This project analyzes multi-decade government budget data across countries, combining **SQL-driven data engineering** with **interactive Python visualizations**. It's built to help explore:

- How national spending has evolved over time
- Which sectors dominate a country's budget, and how that mix shifts
- Fiscal years that behave like statistical outliers
- Where spending is headed, using polynomial trend projections

---

## ✨ Features

| Tab | What it does |
|---|---|
| 📈 **Macro Historical Trends** | Line chart of total budget over time, with KPI cards for latest budget, YoY growth, peak year, and years tracked |
| 🥧 **Sector Structural Spreads** | Area chart of sector allocation shifts over time + box plot showing variance across sectors |
| 🔍 **Statistical Anomalies** | Z-score based outlier detection (\|Z\| > 1.96) with a highlighted scatter plot and flagged-years table |
| 🔬 **Macro Economic Research Lab** | Cross-sector correlation heatmap, 10-year rolling volatility index, and a polynomial forecast (with adjustable degree, horizon, and scenario shock) |

All data is filtered live by **country**, selectable from the sidebar.

---

## 🛠️ Tech Stack

- **Frontend / App Framework:** [Streamlit](https://streamlit.io/)
- **Database:** MySQL (hosted on [Railway](https://railway.app/))
- **Data Layer:** SQLAlchemy + `mysql-connector-python`
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly (Express + Graph Objects)
- **Styling:** Custom CSS (gradient theme, animated KPI cards)
- **Deployment:** Streamlit Community Cloud
- **Version Control:** Git + GitHub

---

## 🗂️ Project Structure

```
├── main_dashboard.py              # Main Streamlit app (entry point)
├── requirements.txt                # Python dependencies
├── Master_Global_Budgets_Historical.csv   # Source dataset
├── advance_query.py                # Exploratory SQL query scripts
├── budget_volatility.py
├── correlations.py
├── defense_social.py
├── forecasting_engine.py
├── outlier_det.py
├── python_sql.py
├── individual_countries.zip
├── .gitignore                      # Excludes local secrets/venv from Git
└── README.md
```

---

## 🗃️ Database Schema (simplified)

```
countries (country_id, country_name)
        │
        ▼
budgets (budget_id, country_id, year, total_budget_billions_usd)
        │
        ▼
sector_allocations (id, budget_id, sector_name, allocated_percentage, allocated_amount_billions_usd)
```

---

## 🚀 Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/arpit00045/Global-Budget-Data-Analytics-Python-SQL-Project.git
cd Global-Budget-Data-Analytics-Python-SQL-Project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your database connection
Create a `.streamlit/secrets.toml` file in the project root:
```toml
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "global_budget_db"
```
> If no `secrets.toml` is found, the app falls back to local defaults (`localhost`, `root`, port `3306`).

### 4. Run the app
```bash
streamlit run main_dashboard.py
```
The app will open at `http://localhost:8501`.

---

## ☁️ Deployment

This app is deployed on **Streamlit Community Cloud**, connected directly to this GitHub repository. Database credentials are stored securely using Streamlit's **Secrets Manager** (never committed to source control) and point to a **MySQL instance hosted on Railway**.

The same codebase works both locally and in production — `get_engine()` automatically detects available secrets and falls back gracefully when none are found.

---

## 📊 Data Source

Historical government budget data compiled in `Master_Global_Budgets_Historical.csv`, imported into MySQL and normalized into three relational tables: `countries`, `budgets`, and `sector_allocations`.

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 🙋 Author

**Arpit Jaiswal**
GitHub: [@arpit00045](https://github.com/arpit00045)
