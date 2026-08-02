import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

def detect_budget_anomalies(country_name) :
    host = "localhost"
    user = "root"
    password = "Arpit@2005"
    database = "global_budget_db"
    password_quoted = urllib.parse.quote_plus(password)
    engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password_quoted}@{host}/{database}"
    )

    # Extract complete sequence for the country
    query = """
         select b.year, b.total_budget_billions_usd
         from budgets b
         join countries c on b.country_id = c.country_id
         where c.country_name = %s order by b.year asc
    """
    df = pd.read_sql_query(query, engine, params = (country_name,))
    engine.dispose()

    if df.empty: return

    # statistical analytics calculations
    mean_val = df['total_budget_billions_usd'].mean()
    std_val = df['total_budget_billions_usd'].std()


    #calculate rolling z-scores to flag shifts out of historical baselines
    df['z_score'] = (df['total_budget_billions_usd'] - mean_val) / std_val


    #Identify anomaly years where spending jumps outside a 95% confidence threshold (> 1.96 standard deviations)
    anomalies = df[df['z_score'].abs() > 1.96]

    print(f"\n--- Flagged Fiscal Anomalies for {country_name} (Outlier variance analysis) ---")
    if anomalies.empty:
        print("No extreme statistical outliers identified.")
    else:
        print(anomalies)
    return anomalies        