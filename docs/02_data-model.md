# Data Model — CLV Analytics Pipeline

## Overview

The pipeline follows a medallion architecture, transforming source data from Amazon RDS MySQL into analytical datasets stored as Parquet in Amazon S3.

**Raw → Silver → Gold**

- **Raw:** Source data extracted from RDS MySQL.
- **Silver:** Cleaned and standardized order-item data, including customer identifiers, timestamps, prices, quantities, and validation flags.
- **Gold:** Aggregated datasets supporting order, customer lifetime value (CLV), and restaurant performance analysis.

## Gold Data Model

| Dataset | Grain | Key | Purpose |
|---|---|---|---|
| `order_sales` | One row per order | `ORDER_ID` | Order-level revenue and transaction metrics |
| `customer_metrics` | One row per identified customer | `customer_id` | Historical CLV, purchase frequency, recency, and customer segmentation |
| `restaurant_performance` | One row per restaurant | `restaurant_id` | Restaurant revenue, order volume, and average order value |

### Dataset Relationships

```text
Silver: order_items
        |
        | Aggregate by ORDER_ID
        v
Gold: order_sales
        |
        +---- customer_id ----> customer_metrics
        |                       (aggregate by customer)
        |
        +---- restaurant_id --> restaurant_performance
                                (aggregate by restaurant)
```

`order_sales` is the foundational Gold dataset. Both `customer_metrics` and `restaurant_performance` are derived from it.

## Business Assumptions

- Each `ORDER_ID` represents a single transaction associated with one customer ID (or an anonymous customer).
- Order revenue is calculated by summing item prices across all valid line items sharing an `ORDER_ID`.
- Customer revenue attribution assumes consistent customer identifiers within an order. Shared orders or split-payment scenarios would require additional business rules.
- Anonymous orders contribute to order-level and restaurant-level revenue but are excluded from customer CLV calculations.
- Historical CLV represents observed customer revenue, not predicted future value.
- Recency is measured relative to the latest order date in the dataset, rather than the current calendar date.
- Customer segments are assigned using historical CLV quintiles: Low (bottom 20%), Medium (middle 60%), and High (top 20%).

## Storage and Refresh

Gold datasets are stored in Amazon S3 as Parquet files. Each Glue job run overwrites the corresponding Gold outputs rather than incrementally updating them.

**Future enhancement — Incremental processing:** Rather than rebuilding entire datasets, the pipeline could process only new or changed records. New transactions could be appended, while existing customer and restaurant aggregates would require updates (upserts). Apache Iceberg with `MERGE` is one option for supporting these operations in AWS Glue.