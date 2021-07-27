import json
from typing import Any, Dict, List

import boto3

# import requests
# Create an S3 client
s3 = boto3.client("s3")


def lambda_handler(event, context):

    # For multiple bukcets
    buckets = ["grafana-metrics-test-bucket-kaise"]

    for bucket in buckets:

        # Create the bucket policy
        ssl_statement = {
            "Sid": "AllowSSLRequestsOnly",
            "Action": "s3:*",
            "Effect": "Deny",
            "Resource": [f"arn:aws:s3:::{bucket}", f"arn:aws:s3:::{bucket}/*"],
            "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            "Principal": "*",
        }
        try:
            existing_policy: str = s3.get_bucket_policy(Bucket=bucket)
            statement: Dict[str, Any] = json.loads(existing_policy["Policy"])
            existing_statement = statement.get("Statement", [])
            existing_statement.append(ssl_statement)
            print(existing_statement)
            new_policy = {
                "Version": "2012-10-17",
                "Id": "NewPolicy",
                "Statement": existing_statement,
            }
            s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(new_policy))
        except s3.exceptions.from_code("NoSuchBucketPolicy"):
            new_policy = {
                "Version": "2012-10-17",
                "Id": "EnforceSSLEncryption",
                "Statement": ssl_statement,
            }
            s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(new_policy))
