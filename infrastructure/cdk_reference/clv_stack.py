
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
)
from constructs import Construct
from aws_cdk import aws_iam as iam
from aws_cdk import aws_glue as glue

# A Stack groups AWS resources into one CloudFormation deployment unit.
# This class defines the infrastructure for our CLV analytics pipeline.
class ClvAnalyticsStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        # Initialize the parent Stack class.
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for the Raw, Silver, and Gold data layers.
        # This models the existing bucket, which was created through the AWS Console.
        analytics_bucket = s3.Bucket(
            self,
            "ClvAnalyticsData",
            bucket_name="sdep-clv-analytics-data",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # IAM role assumed by AWS Glue when executing ETL jobs.
        # The trust policy determines who can assume this role.
        glue_role = iam.Role(
            self,
            "ClvGlueExecutionRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="Execution role for CLV analytics Glue jobs",
        )

        # Attach AWS's managed Glue service policy.
        # Provides baseline permissions for Glue job execution.
        glue_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSGlueServiceRole"
            )
        )

        # Grant the Glue role read/write access to clv analytics bucket.
        # CDK generates the corresponding IAM policy statements.
        analytics_bucket.grant_read_write(glue_role)

        # Note: This is a simplified CDK reference for learning purposes.
        # The production CLV pipeline was provisioned through the AWS Console.
        # This stack is not intended for deployment (see below for more info).

        # Additional permissions/configuration needed for a full implementation:
        # - S3 access to the separate Glue scripts/assets bucket.
        # - CloudWatch Logs permissions for job execution and monitoring.
        # - Glue Data Catalog permissions, where required.
        # - RDS/JDBC connectivity, including VPC, subnets, security groups,
        #   and access to database credentials through Secrets Manager.
        # - Least-privilege IAM policies tailored to individual Glue jobs.
        #
        # These are intentionally outside the scope of this CDK reference.


        # Raw ingestion: RDS MySQL -> S3 Raw layer.
        # CfnJob is an L1 construct that maps to AWS::Glue::Job
        # in CloudFormation.
        raw_job = glue.CfnJob(
            self,
            "ClvRawIngestionJob",
            name="clv-analytics-rds-ingestion",
            role=glue_role.role_arn,
            glue_version="5.0",
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=(
                    "s3://aws-glue-assets-<account-id>-us-east-1/"
                    "scripts/clv-analytics-rds-ingestion.py"
                ),
                python_version="3",
            ),
            worker_type="G.1X",
            number_of_workers=2,
            max_retries=0,
            timeout=30,
        )


        # Silver: transform Raw data into cleaned, standardized datasets.
        silver_job = glue.CfnJob(
            self,
            "ClvSilverJob",
            name="clv-analytics-silver",
            role=glue_role.role_arn,
            glue_version="5.0",
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=(
                    "s3://aws-glue-assets-<account-id>-us-east-1/"
                    "scripts/clv-analytics-silver.py"
                ),
                python_version="3",
            ),
            worker_type="G.1X",
            number_of_workers=2,
            max_retries=0,
            timeout=30,
        )

        # Gold: aggregate Silver data into analytics-ready datasets.
        # Outputs: order_sales, customer_metrics, restaurant_performance.
        gold_job = glue.CfnJob(
            self,
            "ClvGoldJob",
            name="clv-analytics-gold",
            role=glue_role.role_arn,
            glue_version="5.0",
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=(
                    "s3://aws-glue-assets-<account-id>-us-east-1/"
                    "scripts/clv-analytics-gold.py"
                ),
                python_version="3",
            ),
            worker_type="G.1X",
            number_of_workers=2,
            max_retries=0,
            timeout=30,
        )


        # Glue Workflow groups the three ETL jobs into one pipeline.
        workflow = glue.CfnWorkflow(
            self,
            "ClvAnalyticsWorkflow",
            name="clv-analytics-workflow",
        )

        # On-demand trigger starts Raw ingestion.
        start_trigger = glue.CfnTrigger(
            self,
            "StartRawTrigger",
            name="clv-start-raw",
            type="ON_DEMAND",
            workflow_name=workflow.name,
            actions=[
                glue.CfnTrigger.ActionProperty(job_name=raw_job.name)
            ],
        )

        # Run Silver only after Raw completes successfully.
        silver_trigger = glue.CfnTrigger(
            self,
            "RawToSilverTrigger",
            name="clv-raw-to-silver",
            type="CONDITIONAL",
            workflow_name=workflow.name,
            start_on_creation=True,
            predicate=glue.CfnTrigger.PredicateProperty(
                conditions=[
                    glue.CfnTrigger.ConditionProperty(
                        job_name=raw_job.name,
                        state="SUCCEEDED",
                    )
                ]
            ),
            actions=[
                glue.CfnTrigger.ActionProperty(job_name=silver_job.name)
            ],
        )

        # Run Gold only after Silver completes successfully.
        gold_trigger = glue.CfnTrigger(
            self,
            "SilverToGoldTrigger",
            name="clv-silver-to-gold",
            type="CONDITIONAL",
            workflow_name=workflow.name,
            start_on_creation=True,
            predicate=glue.CfnTrigger.PredicateProperty(
                conditions=[
                    glue.CfnTrigger.ConditionProperty(
                        job_name=silver_job.name,
                        state="SUCCEEDED",
                    )
                ]
            ),
            actions=[
                glue.CfnTrigger.ActionProperty(job_name=gold_job.name)
            ],
        )
