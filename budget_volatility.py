from sqlalchemy import create_engine
import pandas as pd 
import urllib.parse
from urllib.parse import quote_plus
def analyze_budget_volatility(country_name) :
    host = "localhost"
    user = "root"
    password = "Arpit@2005"
    database = "global_budget_db"
    password_quoted = urllib.parse.quote_plus(password)
    engine = create_engine(
            f"mysql+pymysql://{user}:{password_quoted}@{host}/{database}"
        )
    
 
    #Extract historical spending sequence
    query = """
        select b.year, b.total_budget_billions_usd
        from budgets b
        join countries c on b.country_id = c.country_id
        where c.country_name = %s order by b.year asc;
    """
    df = pd.read_sql(query, engine, params = (country_name,))

    if df.empty: 
        return
    
    # Calculate a 10-year rolling mean and standard deviation using pandas
    df['rolling_mean'] = df['total_budget_billions_usd'].rolling(window=10).mean()
    df['rolling_std'] = df['total_budget_billions_usd'].rolling(window=10).std()

    # Calculate volatility Index (Coefficient of Variation)
    df['volatility_index'] = df['rolling_std'] / df['rolling_mean'] * 100

    print(f"\n --- Era Volatility Index for {country_name} (sample) --- ")
    print(df.dropna().head(10)) 
    return df

if __name__ == "__main__":
    analyze_budget_volatility("USA") #or your country name
