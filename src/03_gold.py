from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("clv-analytics-gold").getOrCreate()

BUCKET = "sdep-clv-analytics-data"
SILVER_PATH = f"s3://{BUCKET}/silver"
GOLD_PATH = f"s3://{BUCKET}/gold"

# Read validated Silver data
items = spark.read.parquet(f"{SILVER_PATH}/order_items/")

# Safeguard to include only records with valid transaction timestamps
items_valid = items.filter(F.col("is_valid_timestamp") == True)

# Aggregate line items into one row per order
order_sales = (
    items_valid
    .groupBy("ORDER_ID")
    .agg(
        F.first("user_id_clean", ignorenulls=True).alias("customer_id"),
        F.first("RESTAURANT_ID", ignorenulls=True).alias("restaurant_id"),
        F.min("order_timestamp").alias("order_timestamp"),
        F.min("order_date").alias("order_date"),
        F.sum(F.coalesce(F.col("item_price"), F.lit(0))).alias("order_revenue"),
        F.sum(F.coalesce(F.col("item_quantity"), F.lit(0))).alias("total_quantity"),
        F.count("*").alias("line_item_count"),
        F.max(
            F.when(
                F.lower(F.trim(F.col("IS_LOYALTY").cast("string"))).isin(
                    "true", "1", "yes"
                ),
                1
            ).otherwise(0)
        ).cast("boolean").alias("is_loyalty")
    )
)

# Write Gold Parquet
order_sales.write.mode("overwrite").parquet(
    f"{GOLD_PATH}/order_sales/"
)

print(f"Gold order_sales rows: {order_sales.count()}")
print("Gold order_sales complete.")


# -----------------------------------------
# Gold: Customer Metrics
# -----------------------------------------

# Use the latest transaction date in the dataset
reference_date = order_sales.agg(
    F.max("order_date")
).first()[0]

# Exclude anonymous transactions from CLV
customer_orders = order_sales.filter(
    F.col("customer_id").isNotNull()
)

customer_metrics = (
    customer_orders
    .groupBy("customer_id")
    .agg(
        F.sum("order_revenue").alias("historical_clv"),
        F.count("*").alias("total_orders"),
        F.max("order_date").alias("last_order_date")
    )
    .withColumn(
        "recency_days",
        F.datediff(F.lit(reference_date), F.col("last_order_date"))
    )
)

# Segment customers by historical CLV
customer_metrics = (
    customer_metrics
    .withColumn(
        "clv_quintile",
        F.ntile(5).over(Window.orderBy("historical_clv"))
    )
    .withColumn(
        "clv_segment",
        F.when(F.col("clv_quintile") == 5, "High")
         .when(F.col("clv_quintile") == 1, "Low")
         .otherwise("Medium")
    )
    .drop("clv_quintile")
)

customer_metrics.write.mode("overwrite").parquet(
    f"{GOLD_PATH}/customer_metrics/"
)

print(f"Gold customer_metrics rows: {customer_metrics.count()}")


# -----------------------------------------
# Gold: Restaurant Performance
# -----------------------------------------

restaurant_performance = (
    order_sales
    .groupBy("restaurant_id")
    .agg(
        F.sum("order_revenue").alias("total_revenue"),
        F.count("*").alias("total_orders"),
        F.round(F.avg("order_revenue"), 2).alias("avg_order_value")
    )
)

restaurant_performance.write.mode("overwrite").parquet(
    f"{GOLD_PATH}/restaurant_performance/"
)

print(
    f"Gold restaurant_performance rows: "
    f"{restaurant_performance.count()}"
)

print("All Gold datasets complete.")
