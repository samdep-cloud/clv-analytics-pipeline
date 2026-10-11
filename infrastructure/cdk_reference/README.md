# AWS CDK Infrastructure Reference

This directory contains a Python-based AWS CDK reference implementation of the infrastructure supporting the CLV analytics pipeline.

The operational AWS resources were provisioned manually through the AWS Console. This CDK implementation was developed separately to practice infrastructure as code (IaC) and demonstrate how AWS resources can be defined programmatically.

## Resources Defined

- **Amazon S3:** Analytics bucket with server-side encryption and public access blocked.
- **AWS IAM:** Glue execution role with managed Glue permissions and access to the analytics bucket.
- **AWS Glue:** Three PySpark ETL jobs for Raw ingestion, Silver transformations, and Gold aggregations.
- **Glue Workflow:** On-demand execution with conditional triggers that advance jobs after successful completion.

## CDK Concepts Practiced

- **Constructs and stacks:** Defining AWS infrastructure using Python classes and CDK constructs.
- **Object-oriented programming:** Extending the `Stack` class and initializing resources within its constructor.
- **Resource permissions:** Using CDK methods such as `grant_read_write()` to generate IAM policies.
- **Infrastructure orchestration:** Defining Glue jobs, workflows, and conditional triggers.
- **CloudFormation synthesis:** Translating Python infrastructure definitions into a CloudFormation template.

## Validate the Reference

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

With the AWS CDK CLI installed, generate the CloudFormation template:

```bash
cdk synth --app "python app.py"
```

Synthesis validates template generation without deploying resources.

## Scope and Limitations

This is a learning reference, not a fully deployable reproduction of the operational environment.

Additional configuration would be required for production deployment, including RDS connectivity, Glue networking, script-bucket permissions, and supporting security and runtime settings.

**The CDK reference was successfully synthesized but was not deployed.**