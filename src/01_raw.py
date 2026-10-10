import sys
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

connection_name = "clv-analytics-rds-jdbc"
bucket = "sdep-clv-analytics-data"

tables = {
    "order_items": 203519,
    "order_item_options": 193017,
    "date_dim": 365,
}

for table_name, expected_count in tables.items():
    print(f"Starting ingestion: {table_name}")

    df = glue_context.create_dynamic_frame.from_options(
        connection_type="mysql",
        connection_options={
            "useConnectionProperties": "true",
            "connectionName": connection_name,
            "dbtable": table_name,
        },
    ).toDF()

    actual_count = df.count()

    if actual_count != expected_count:
        raise ValueError(
            f"{table_name}: expected {expected_count:,} rows, "
            f"found {actual_count:,}"
        )

    df = df.withColumn(
        "ingestion_timestamp_utc",
        F.current_timestamp()
    )

    output_path = f"s3://{bucket}/raw/{table_name}/"