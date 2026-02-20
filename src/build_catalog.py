import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw.csv"
DB_PATH = ROOT / "project.db"

# SQL table
    # ↓
# look at every column
    # ↓
# collect metadata
    # ↓
# return a data dictionary

## A0) cleaning step (raw -> clean)
def build_clean_table(con):
    con.execute("DROP TABLE IF EXISTS clean;")

    con.execute("""
        CREATE TABLE clean AS
        WITH ranked AS (
            SELECT
                *,
                DATE(Date) AS Date_norm,

                ROW_NUMBER() OVER (
                    PARTITION BY DATE(Date) 
                    ORDER BY rowid DESC
                ) AS rn
            FROM raw

            WHERE DATE(Date) IS NOT NULL
              AND Close IS NOT NULL
              AND Close > 0
              AND (Volume IS NULL OR Volume >= 0)
        )

        SELECT *
        FROM ranked
        WHERE rn = 1;
    """)



## A) data dictionary report
def profile_table(con, table_name):
    # Read SQL table into pandas
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", con)
    rows = len(df)  # this is to count how many rows
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
            "missing": int(missing),  
            "missing_pct": round(missing_pct, 2),
            "example_values": ", ".join(example_values)
        })

    return pd.DataFrame(profile_rows)

## B) daily returns report
def returns_report(con):
    con.execute("DROP TABLE IF EXISTS returns;")
    con.execute("""
        CREATE TABLE returns AS
        SELECT
            Date,
            Close,
            LAG(Close) OVER (ORDER BY Date) AS prev_close,
            ROUND(
                (Close - LAG(Close) OVER (ORDER BY Date))
                / LAG(Close) OVER (ORDER BY Date) * 100,
                2
            ) AS daily_return_pct
        FROM clean;  
    """)

    return pd.read_sql_query("SELECT * FROM returns ORDER BY Date;", con)

## C) returns stats report
def returns_stats_report(returns):
    s = returns["daily_return_pct"]

    mean_val = s.mean(skipna=True)
    std_val = s.std(skipna=True)
    sharpe_like = mean_val / std_val

    stats = pd.DataFrame([{
        "n_rows": len(returns),
        "n_missing_returns": int(s.isna().sum()),
        "mean_return_pct": round(float(s.mean(skipna=True)), 4),
        "median_return_pct": round(float(s.median(skipna=True)), 4),
        "std_return_pct": round(float(s.std(skipna=True)), 4),
        "min_return_pct": round(float(s.min(skipna=True)), 4),
        "max_return_pct": round(float(s.max(skipna=True)), 4),
        "pct_positive_days": round(float((s > 0).mean(skipna=True) * 100), 2),
        "pct_negative_days": round(float((s < 0).mean(skipna=True) * 100), 2),
        "sharpe_like_ratio": round(float(sharpe_like), 4)
    }])

    ## sharpe-like ratio: average return per unit of volatility (std), measures return relative to risk
    ## Higher Sharpe = better risk-adjusted performance
    return stats


## D) quality report
def quality_report(con):
    """Run basic missingness/validity/duplicate checks on the clean table."""
    total_rows = con.execute("SELECT COUNT(*) FROM clean;").fetchone()[0]

    # missing values
    null_close = con.execute("SELECT COUNT(*) FROM clean WHERE Close IS NULL;").fetchone()[0]
    null_volume = con.execute("SELECT COUNT(*) FROM clean WHERE Volume IS NULL;").fetchone()[0]

    # validity chekcs these should be 0 or small
    nonpositive_close = con.execute("SELECT COUNT(*) FROM clean WHERE Close <= 0;").fetchone()[0]
    negative_volume = con.execute("SELECT COUNT(*) FROM clean WHERE Volume < 0;").fetchone()[0]

    # duplicates check (same Date appears more than once)
    duplicate_dates = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT Date
            FROM clean
            GROUP BY Date
            HAVING COUNT(*) > 1
        );
    """).fetchone()[0]

    return pd.DataFrame([
        {"check": "total_rows_clean", "value": total_rows},
        {"check": "null_close_rows", "value": null_close},
        {"check": "null_volume_rows", "value": null_volume},
        {"check": "close<=0_rows", "value": nonpositive_close},
        {"check": "volume<0_rows", "value": negative_volume},
        {"check": "duplicate_date_count", "value": duplicate_dates},
    ])

## E) data lineage report
def lineage_report():
    # documents how data flows through the pipeline
    return pd.DataFrame([
        {"source": "data/raw.csv", "target": "raw (SQL table)", "step": "load_csv"},
        {"source": "raw (SQL table)", "target": "clean (SQL table)", "step": "clean/filter/deduplicate"},
        {"source": "clean (SQL table)", "target": "returns (SQL table)", "step": "calculate_daily_returns"},
        {"source": "returns (SQL table)", "target": "output/daily_returns.csv", "step": "export_returns"},
        {"source": "returns (DataFrame)", "target": "output/returns_stats.csv", "step": "summary_stats"},
        {"source": "raw (SQL table)", "target": "output/data_dictionary.csv", "step": "metadata_profile"},
        {"source": "clean (SQL table)", "target": "output/quality_report.csv", "step": "quality_checks"},
    ])


## F) main
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
    build_clean_table(con)


    # 5) sanity checks using SQL queries
    raw_count = con.execute("SELECT COUNT(*) FROM raw;").fetchone()[0]
    clean_count = con.execute("SELECT COUNT(*) FROM clean;").fetchone()[0]
    print("Rows in raw:", raw_count)
    print("Rows in clean:", clean_count)
    print("SQLite database created here:", DB_PATH)

    out_dir = ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 7) close connection
    qr = quality_report(con)
    qr_path = out_dir / "quality_report.csv"  
    qr.to_csv(qr_path, index=False)
    print("Yay quality report saved to:", qr_path)

    data_dict = profile_table(con, "raw")
    dictionary_path = out_dir / "data_dictionary.csv"  
    data_dict.to_csv(dictionary_path, index=False)
    print("Yay data dictionary saved to:", dictionary_path)

    returns = returns_report(con) 
    out_path = out_dir / "daily_returns.csv"  
    returns.to_csv(out_path, index=False)
    print("Yay returns exported to:", out_path)

    stats = returns_stats_report(returns)
    stats_path = out_dir / "returns_stats.csv"
    stats.to_csv(stats_path, index=False)
    print("Yay returns stats saved to:", stats_path)

    lineage = lineage_report()
    lineage_path = out_dir / "data_lineage.csv"
    lineage.to_csv(lineage_path, index=False)
    print("Yay lineage saved to:", lineage_path)

    con.close()


if __name__ == "__main__":
    main()

