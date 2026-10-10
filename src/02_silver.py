import sys
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

bucket = "sdep-clv-analytics-data"

def read_raw(table_name):
    return spark.read.parquet(
        f"s3://{bucket}/raw/{table_name}/"
    )


def write_silver(df, table_name):
    output_path = f"s3://{bucket}/silver/{table_name}/"
    count = df.count()

    df.write.mode("overwrite").parquet(output_path)

    print(f"Silver {table_name}: {count:,} records written")


# 1. ORDER ITEMS
orders = read_raw("order_items")

orders = (
    orders
    .withColumn(
        "order_timestamp",
        F.to_timestamp("CREATION_TIME_UTC")
    )
    .withColumn(
        "order_date",
        F.to_date("order_timestamp")
    )
    .withColumn(
        "item_price",
        F.col("ITEM_PRICE").cast("decimal(18,2)")
    )
    .withColumn(
        "item_quantity",
        F.col("ITEM_QUANTITY").cast("int")
    )
    .withColumn(
        "user_id_clean",
        F.when(
            F.trim(F.col("USER_ID")) == "",
            F.lit(None)
        ).otherwise(F.trim(F.col("USER_ID")))
    )
    .withColumn(
        "is_valid_timestamp",
        F.col("order_timestamp").isNotNull()
    )
)

orders.filter(
    F.trim(F.col("CREATION_TIME_UTC")).isin("1", "2")
).select(
    "CREATION_TIME_UTC",
    "order_timestamp",
    "is_valid_timestamp"
).show(20, truncate=False)

invalid_timestamps = orders.filter(
    ~F.col("is_valid_timestamp")
).count()

print(f"Invalid order timestamps: {invalid_timestamps:,}")

write_silver(orders, "order_items")


# 2. ORDER ITEM OPTIONS
options = read_raw("order_item_options")

options = (
    options
    .withColumn(
        "option_price",
        F.col("OPTION_PRICE").cast("decimal(18,2)")
    )
    .withColumn(
        "option_quantity",
        F.col("OPTION_QUANTITY").cast("int")
    )
)

write_silver(options, "order_item_options")


# 3. DATE DIMENSION
dates = read_raw("date_dim")

dates = (
    dates
    .withColumn(
        "date_key",
        F.to_date(F.col("DATE_KEY"))
    )
    .withColumn(
        "year_num",
        F.col("YEAR").cast("int")
    )
    .withColumn(
        "month_num",
        F.col("MONTH").cast("int")
    )
    .withColumn(
        "is_weekend_flag",
        F.lower(F.trim(F.col("IS_WEEKEND"))).isin(
            "true", "1", "yes"
        )
    )
    .withColumn(
        "is_holiday_flag",
        F.lower(F.trim(F.col("IS_HOLIDAY"))).isin(
            "true", "1", "yes"
        )
    )
)

write_silver(dates, "date_dim")

print("All Silver transformations completed successfully.")