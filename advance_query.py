import mysql.connector
import pandas as pd

def run_advanced_analytics() :
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Arpit@2005",
        database="global_budget_db"
    )
    cursor = conn.cursor()

    # 1.Analysis : year over year (yoy) growth and 5-year rolling moving average
    moving_avg_query = """
        SELECT 
            c.country_name,b.year, b.total_budget_billions_usd,
            AVG(b.total_budget_billions_usd) OVER (
                PARTITION BY c.country_name 
                ORDER BY b.year 
                ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
            ) AS rolling_5yr_avg
        from budgets b
        JOIN countries c ON b.country_id = c.country_id;
    """
    df_moving = pd.read_sql_query(moving_avg_query, conn)  
    print("\n--- 1. 5-Year Rolling Budget Trends ---\n", df_moving.head())

    # 2. ANALYSIS : Historic sector dominance matrix (Isolating the #1 funded sector per year)
    dominance_query = """
        with RankedSectors AS (
            select 
                c.country_name, b.year, sa.sector_name, sa.allocated_percentage,
                DENSE_RANK() OVER (PARTITION BY c.country_name, b.year ORDER BY sa.allocated_percentage DESC) AS rnk
            from sector_allocations sa
            join budgets b on sa.budget_id = b.budget_id
            join countries c on b.country_id = c.country_id
        )
        SELECT country_name, year, sector_name, allocated_percentage
        FROM RankedSectors
        WHERE rnk = 1;
    """  

    df_dom = pd.read_sql(dominance_query, conn)
    print("\n--- 2. Historic #1 Budget Priorties --- \n", df_dom.head())

    conn.close()

if __name__ == "__main__":
    run_advanced_analytics()