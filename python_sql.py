import pandas as pd
import mysql.connector
from mysql.connector import Error

def run_robust_etl(csv_path):
    
    df = pd.read_csv(csv_path)
    df = df.fillna(0)
    
    try:
        conn = mysql.connector.connect(
            host="localhost",      # or your server IP
            user="root",           # your MySQL username
            password="Arpit@2005",
            database="global_budget_db"  
        )
        cursor = conn.cursor()
        
        print("🚀 Step 1 : Seeding Country Dimensions...")
        unique_countries = df['Country'].unique()
        for country in unique_countries:
            cursor.execute("INSERT IGNORE INTO countries (country_name) VALUES (%s)",(country.strip(),))
            
        conn.commit()
        
        cursor.execute("SELECT country_name,country_id FROM countries")
        country_lookup = dict(cursor.fetchall())
        
        sectors = ['Defense','Education','Health','Interest_Payments',
                   'Infrastructure','Agriculture','State_Transfers','Social_Welfare']
        
        print(f"🚀 Step 2: Ingesting {len(df)} Fact Records..")
        success_count = 0
        
        for idx, row in df.iterrows():
            try:
                country_name = row['Country'].strip()
                country_id = country_lookup[country_name]
                year = int(row['Year'])
                total_budget = float(row['Total_Budget_Billions_USD'])
                
                cursor.execute(
                    "INSERT INTO budgets (country_id,year,total_budget_billions_usd) VALUES (%s,%s,%s)",
                    (country_id,year,total_budget)
                )
                budget_id = cursor.lastrowid
                
                
                for sector in sectors:
                    pct_col = f"{sector}_Percentage"
                    amt_col = f"{sector}_Amount_Billions_USD"
                    
                    cursor.execute(
                        """INSERT INTO sector_allocations
                        (budget_id,sector_name,allocated_percentage,allocated_amount_billions_usd
                        )
                        VALUES(%s,%s,%s,%s)""",
                        (budget_id,sector,float(row[pct_col]),float(row[amt_col]))
                        
                    )
                    success_count += 1
                    
            except Error as row_err:
                print(f" Error processing row{idx} ({country_name}-{year}):{row_err}")
                
                continue
            
            
        conn.commit()
        print(f" ETL Complete Successfully committed {success_count} structural record into MySQL.")
        
    except Error as df_err:
        print(f"Structural Database connection failureL{df_err}")
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            

if __name__ == "__main__":
    run_robust_etl("Master_Global_Budgets_Historical.csv")