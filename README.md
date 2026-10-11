# Customer Lifetime Value (CLV) Analytics Pipeline

An AWS-native data engineering pipeline that ingests transactional restaurant data from Amazon RDS MySQL, transforms it using PySpark and AWS Glue, and produces analytical datasets for customer lifetime value (CLV) and restaurant performance analysis.

## Architecture

**Amazon RDS MySQL → AWS Glue → Amazon S3 (Raw → Silver → Gold) → AWS Glue Data Catalog / Amazon Athena → Streamlit**

The pipeline follows a medallion architecture:

- **Raw:** Extracts source tables from RDS MySQL and stores them in S3.
- **Silver:** Cleans and standardizes order-item records, including identifiers, timestamps, prices, quantities, and validation flags.
- **Gold:** Builds order-level sales, historical customer CLV, and restaurant performance datasets.

## Technology Stack

| Component | Technology |
|---|---|
| Source database | Amazon RDS MySQL |
| ETL and transformations | AWS Glue, PySpark |
| Storage | Amazon S3, Parquet |
| Query layer | AWS Glue Data Catalog, Amazon Athena |
| Orchestration | AWS Glue Workflows and Triggers |
| CI/CD | GitHub, AWS CodePipeline, AWS CodeBuild |
| Infrastructure reference | AWS CDK (Python) |
| Visualization | Streamlit |

## Gold Datasets

| Dataset | Grain | Key Metrics |
|---|---|---|
| `order_sales` | Order | Revenue, quantity, line-item count, loyalty indicator |
| `customer_metrics` | Customer | Historical CLV, order frequency, recency, CLV segment |
| `restaurant_performance` | Restaurant | Total revenue, total orders, average order value |

Historical CLV measures observed customer revenue, not predicted future lifetime value. Anonymous orders are excluded from customer-level CLV but retained in overall sales and restaurant metrics.

## Pipeline Execution

An AWS Glue workflow orchestrates three ETL jobs:

1. `clv-analytics-rds-ingestion` — extracts source data from RDS into S3 Raw.
2. `clv-analytics-silver` — performs cleaning and standardization.
3. `clv-analytics-gold` — generates analytical aggregates.

The workflow is started on demand, with conditional triggers advancing subsequent jobs after successful completion.

## CI/CD

GitHub is the source repository for the ETL scripts.

AWS CodePipeline and CodeBuild provide a manually triggered deployment workflow that:

- Validates Python syntax using `py_compile`.
- Uploads the three ETL scripts to the Glue scripts S3 bucket.

CI/CD updates the Glue job scripts; it does not automatically execute the ETL workflow.

## Infrastructure and Networking

The operational infrastructure was configured through the AWS Console, including private RDS connectivity for Glue and an S3 VPC gateway endpoint.

An additional Python AWS CDK reference demonstrates how the S3 bucket, IAM role, Glue jobs, workflow, and triggers can be defined as infrastructure as code. The reference was successfully synthesized into CloudFormation but was not deployed.

## Project Documentation

- [Data Model](docs/data-model.md)
- [Data Dictionary](docs/data-dictionary.md)
- [AWS Networking Notes](docs/aws_networking_notes.md)
- [Source Data Assessment](docs/source_data_assessment.md)
- [CDK Infrastructure Reference](infrastructure/cdk_reference/README.md)

## Notes

This is a portfolio project using historical transactional data. Gold datasets are written in Parquet format and rebuilt using overwrite mode.