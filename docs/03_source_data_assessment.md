# Source Data Assessment

## Overview

Assessed `order_items`, `order_item_options`, and `date_dim_tbl` to identify data-quality issues, validate pricing assumptions, and inform Silver transformations and Gold metrics.

A more detailed analysis is available in the EDA notebooks under `notebooks/`.

## Key Findings

| Area | Findings | Treatment |
|---|---|---|
| **Source integrity** | `order_items` contains 203,519 records after correcting CSV parsing with `multiLine=True`. No duplicate `(ORDER_ID, LINEITEM_ID)` pairs were found. One record has missing item identifiers and zero quantity. | Validate record counts, timestamps, and required fields. Preserve anomalous records in Raw. |
| **Customer identification** | 17,808 order-item records (8.75%) lack `USER_ID`. Loyalty-card matching could recover only a small subset. | Include anonymous transactions in aggregate revenue; exclude them from customer-level CLV. |
| **Option data** | `order_item_options` contains 193,017 records, including repeated option combinations that may represent valid selections. | Preserve option records. Avoid joining them directly into revenue calculations where they could multiply order amounts. |
| **Pricing** | Analysis suggests `ITEM_PRICE` is the extended line-item amount, incorporating quantity and options, rather than a unit price. | Sum `ITEM_PRICE` for revenue without multiplying by quantity or adding option charges again. Business validation remains outstanding. |
| **Exceptional values** | Prices include zero values and quantities include unusually large values. No negative option prices were observed. | Preserve recorded values and flag anomalies. Discount effectiveness cannot be reliably determined from the available fields. |
| **Dates and coverage** | Transactions span April 2020–February 2024 across 28 restaurants, while the supplied calendar covers only 2023. Correctly parsed source records have valid timestamps. | Parse timestamps and retain transaction dates. A complete calendar would be needed for date-dimension reporting across the full history. |

## Revenue Calculation

Based on the relationships and pricing patterns examined in `04_relationships_and_metrics.ipynb`:

| Metric | Rule |
|---|---|
| Line revenue | `ITEM_PRICE` |
| Order revenue | `SUM(ITEM_PRICE)` grouped by `ORDER_ID` |
| Effective unit price | `ITEM_PRICE / ITEM_QUANTITY` when quantity is greater than zero |
| Option charges | Retained as detail; not added to revenue again |

**Business assumption:** `ITEM_PRICE` represents the extended line-item amount. This interpretation is supported by observed transaction patterns but differs from the source data dictionary and requires business validation.

## Limitations

- Historical CLV represents observed customer revenue, not predicted future value.
- Anonymous transactions cannot be attributed to individual customers (e.g. potential checkout as guest option).
- Discount effectiveness cannot be reliably measured from the available option pricing fields.
- The supplied calendar does not cover the complete transaction history.