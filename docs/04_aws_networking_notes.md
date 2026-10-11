# AWS Networking Notes — RDS to Glue

Personal reference notes on AWS networking concepts encountered while building the CLV analytics pipeline.

## 1. Core Networking Concepts

| Component | Purpose |
|---|---|
| VPC | Logically isolated network for AWS resources |
| Subnet | IP address range within a VPC, associated with one Availability Zone |
| Route table | Determines where subnet network traffic is directed |
| Internet Gateway | Enables internet connectivity for appropriately routed resources with public IP addresses |
| NAT Gateway | Allows resources in private subnets to initiate outbound connections without accepting unsolicited inbound internet connections |
| Security Group | Stateful virtual firewall controlling inbound and outbound traffic |
| Network ACL | Stateless subnet-level traffic filtering |
| VPC Endpoint | Private connectivity to supported AWS services without traversing the public internet |

## 2. Networking in the CLV Pipeline

The pipeline extracts source data from Amazon RDS MySQL using AWS Glue, then writes Parquet datasets to Amazon S3.

```text
AWS Glue ETL Job
       |
       | JDBC / TCP 3306
       v
Amazon RDS MySQL
       |
       | Data extracted by Glue
       v
Amazon S3 — Raw Layer
```

For Glue to connect to a private RDS instance:

- Glue must use an appropriate VPC connection and subnet.
- The RDS security group must allow inbound MySQL traffic (TCP 3306) from the Glue job's security group.
- Glue's security group must permit the required outbound traffic and self-referencing inbound TCP traffic for Glue worker communication.
- Glue requires suitable network access to S3 for scripts, temporary files, and data outputs, typically through an S3 gateway endpoint or an appropriate NAT route.
- The Glue execution role must have the necessary IAM permissions.

S3 VPC Endpoint
Configured an S3 Gateway VPC Endpoint to allow Glue jobs to access Amazon S3 privately without requiring a NAT gateway or internet gateway. The endpoint is associated with the relevant VPC route table.

## 3. Security Groups vs. IAM

**Security groups control network access.** They determine which connections are permitted between resources.

**IAM controls AWS API permissions.** It determines what actions an AWS identity can perform on AWS resources.

For example:

- Security group: Can Glue establish a TCP connection to MySQL on port 3306?
- IAM: Can the Glue execution role read from or write to the S3 bucket?

Both must be configured correctly for the pipeline to work.

## 4. Troubleshooting Connectivity

When a Glue job cannot reach RDS:

1. Confirm the database endpoint and port.
2. Verify that the Glue connection uses the intended VPC and subnet.
3. Check the RDS inbound security group rule for TCP 3306.
4. Check Glue security group rules, including worker-to-worker communication.
5. Review route tables and S3 endpoint or NAT connectivity.
6. Confirm database credentials and authentication separately from network connectivity.
7. Review Glue job logs for timeouts, connection refusals, or authentication failures.

## 5. Lessons to Remember

- A resource being inside a VPC does not automatically make it reachable from another resource.
- A public subnet does not automatically give every resource in it internet access.
- Security groups are stateful; network ACLs are stateless.
- Glue jobs accessing private RDS databases require careful VPC and security group configuration.
- Network connectivity, database authentication, and IAM authorization are separate concerns.