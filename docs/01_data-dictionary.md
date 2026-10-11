# Data Dictionary — Gold Layer

The Gold layer contains three analytical datasets derived from validated Silver order-item records. Transaction timestamps were validated during Silver processing, with no invalid timestamps identified in the correctly parsed source data.

## 1. order_sales

**Grain:** One row per order (`ORDER_ID`).

| Column | Definition |
|---|---|
| `ORDER_ID` | Unique order identifier |
| `customer_id` | Cleaned customer identifier; nullable for anonymous orders |
| `restaurant_id` | Restaurant associated with the order |
| `order_timestamp` | Earliest valid transaction timestamp for the order |
| `order_date` | Earliest valid order date |
| `order_revenue` | Sum of item prices across order line items; null prices treated as zero |
| `total_quantity` | Sum of item quantities; null quantities treated as zero |
| `line_item_count` | Number of valid line-item records |
| `is_loyalty` | True if any line item indicates loyalty participation |

## 2. customer_metrics

**Grain:** One row per identified customer (`customer_id`). Anonymous orders are excluded.

| Column | Definition |
|---|---|
| `customer_id` | Cleaned customer identifier |
| `historical_clv` | Sum of observed order revenue across the customer's transactions |
| `total_orders` | Number of customer orders |
| `last_order_date` | Most recent order date |
| `recency_days` | Days between the dataset's latest order date and the customer's last order |
| `clv_segment` | Low (bottom quintile), High (top quintile), or Medium (middle three quintiles), based on historical CLV |

Historical CLV represents realized customer revenue. Next steps could include a predictive model of potential future CLV.

## 3. restaurant_performance

**Grain:** One row per restaurant (`restaurant_id`).

| Column | Definition |
|---|---|
| `restaurant_id` | Restaurant identifier |
| `total_revenue` | Sum of order revenue |
| `total_orders` | Number of orders |
| `avg_order_value` | Average order revenue, rounded to two decimal places |

## Storage

All three Gold datasets are stored as Parquet files in Amazon S3 under `gold/`. The current pipeline uses `overwrite` mode, rebuilding each dataset in full on every execution.

**Future enhancement — Incremental processing:** Rather than rebuilding entire datasets, the pipeline could process only new or changed records. New transactions could be appended, while existing customer and restaurant aggregates would require updates (upserts). Apache Iceberg with `MERGE` is one option for supporting these operations in AWS Glue.