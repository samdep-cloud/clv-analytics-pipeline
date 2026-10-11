#!/usr/bin/env python3

import aws_cdk as cdk
from clv_stack import ClvAnalyticsStack

# App as entry point for clv-analytics CDK project
# An app can contain one or more stacks.
app = cdk.App()

# Stack represents the collection of AWS resources defined in clv_stack.py.
# CLVAnalyticsStack creates an instance of our custom stack class.
ClvAnalyticsStack(
    app,
    "ClvAnalyticsStack",  # Logical name of the CloudFormation stack
    env=cdk.Environment(
        account="<account-id>",
        region="us-east-1",
    ),
)

# Synthesizes Python constructs into a CloudFormation template.
# Doesn't deploy or create AWS resources --> cdk synth/cdk deploy
app.synth()