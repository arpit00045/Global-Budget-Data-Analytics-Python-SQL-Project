from sqlalchemy import create_engine
import pandas as pd

def analyze_guns_vs_butter(selected_year = 2025) :
    engine = create_engine("mysql+pymysql://root:Arpit@2005@localhost/global_budget_db")

    # Pivot and calculate the ratio directly inside the mysql query engine
    query = """
        select 
            c.country_name,
            max(CASE WHEN sa.sector_name = 'Defense' THEN sa.allocated_percentage END) AS defense_pct,
            max(CASE WHEN sa.sector_name = 'Social_Welfare' THEN sa.allocated_percentage END) AS welfare_pct,
            max(CASE WHEN sa.sector_name = 'Education' THEN sa.allocated_percentage END) AS education_pct,
            round(
                (max(CASE WHEN sa.sector_name = 'Social_Welfare' THEN sa.allocated_percentage END) +
                 max(CASE WHEN sa.sector_name = 'Education' THEN sa.allocated_percentage END)) /
                nullif(max(CASE WHEN sa.sector_name = 'Defense' THEN sa.allocated_percentage END),0), 2
            ) as civilian_to_defense_ratio
        from sector_allocations sa
        join budgets b on sa.budget_id = b.budget_id
        join countries c on b.country_id = c.country_id
        where b.year = %s
        group by c.country_name
        order by civilian_to_defense_ratio desc;
    """

    df = pd.read_sql(query, engine, params = (selected_year,))

    print(f"\n --- 🪖 Guns vs. Butter ratio Rankings ({selected_year}) ---")
    print(df.head(10))
    return df