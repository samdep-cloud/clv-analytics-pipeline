from pathlib import Path
import os

import pandas as pd
from sqlalchemy import create_engine, URL


project_root = Path(__file__).resolve().parents[1]
# csv_path = project_root / "data" / "raw" / "order_items.csv"
# csv_path = project_root / "data" / "raw" / "order_item_options.csv"
csv_path = project_root / "data" / "raw" / "date_dim.csv"

# Preserving multiline CSV fields
df = pd.read_csv(
    csv_path,
    dtype=str,
    keep_default_na=False,
)

print(f"Source rows: {len(df):,}")

load_df = df

# RDS connection
url = URL.create(
    "mysql+pymysql",
    username=os.environ["RDS_USER"],
    password=os.environ["RDS_PASSWORD"],
    host=os.environ["RDS_HOST"],
    port=3306,
    database="clv_analytics",
)

engine = create_engine(url, pool_pre_ping=True)

load_df.to_sql(
    "date_dim",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    method="multi",
)

engine.dispose()

print(f"Successfully loaded {len(load_df):,} records into RDS.")