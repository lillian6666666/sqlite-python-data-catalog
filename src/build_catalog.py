import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw.csv"
DB_PATH = ROOT / "project.db"

#SQL table
    # ↓
#look at every column
    # ↓
#collect metadata
    # ↓
#return a data dictionary

def profile_table(con, table_name):
    # Read SQL table into pandas
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", con)

    rows = len(df) # this is to count how many rows
    profile_rows = []

    # Loop loop loop 
    for col in df.columns:
        s = df[col]

        missing = s.isna().sum()
        missing_pct = (missing / rows) * 100 if rows else 0
        # if rows > 0 

        example_values = s.dropna().astype(str).head(3).tolist()

        profile_rows.append({
            "table": table_name,
            "column": col,
            "dtype": str(s.dtype),
            "rows": rows,
            "missing": missing,
            "missing_pct": round(missing_pct, 2),
            "example_values": ", ".join(example_values)
        })

    return pd.DataFrame(profile_rows)

def export_returns(con):
    df_returns = pd.read_sql_query(
        "SELECT * FROM returns;",
        con
    )

    out_path = ROOT / "output" / "daily-returns.csv"
    df_returns.to_csv(out_path, index=False)

    print("Yay returns exported to:", out_path)

def main():
    # 1 read to panda dataframe
    df = pd.read_csv(DATA_PATH)
    print("Loaded raw.csv yay:", df.shape)
    print("Columns:", list(df.columns))

    # 2 connect with the SQLite database file
    con = sqlite3.connect(DB_PATH)

    # 3) write dataframe to sql
    df.to_sql("raw", con, if_exists="replace", index=False)

    # 4) created a empty table called clean first from raw, raw → clean → analysis
    con.execute("DROP TABLE IF EXISTS clean;")
    con.execute("""
        CREATE TABLE clean AS
        SELECT *
        FROM raw;
    """)

    # 5) sanity checks using SQL queries
    raw_count = con.execute("SELECT COUNT(*) FROM raw;").fetchone()[0]
    clean_count = con.execute("SELECT COUNT(*) FROM clean;").fetchone()[0]
    print("Rows in raw:", raw_count)
    print("Rows in clean:", clean_count)
    print("SQLite database created here:", DB_PATH)

    # 6) close connection
    con.close()
    data_dict = profile_table(con, "raw")
    output_path = ROOT / "output" / "data_dictionary.csv"
    data_dict.to_csv(output_path, index=False)
    print("Yay data dictionary saved to:", output_path)

if __name__ == "__main__":
    main()
