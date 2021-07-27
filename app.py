import json
from typing import Any, Dict, List

import boto3

# import requests
# Create an S3 client
s3 = boto3.client("s3")


def lambda_handler(event, context):

    buckets = ["grafana-metrics-test-bucket-kaise"]

    for bucket in buckets:

        # The bucket policy we want to append or create
        ssl_statement = {
            "Sid": "AllowSSLRequestsOnly",
            "Action": "s3:*",
            "Effect": "Deny",
            "Resource": [f"arn:aws:s3:::{bucket}", f"arn:aws:s3:::{bucket}/*"],
            "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            "Principal": "*",
        }
        try:
            # Get the existing bucket policy if it exists
            existing_policy: str = s3.get_bucket_policy(Bucket=bucket)
            statement: Dict[str, Any] = json.loads(existing_policy["Policy"])
            existing_statement = statement.get("Statement", [])
            # Check to see if the following condition already present in the existing policy
            condition: str = "{\"Bool\": {\"aws:SecureTransport\": \"false\"}}"
            for key_value in existing_statement:
                print(json.dumps(key_value['Condition']))
                if json.dumps(key_value['Condition']) == condition:
                    print(
                        f"This condition already exists in the following bucket: ${bucket}")
                    print(f"Skipping bucket")
                else:
                    print(f"Creating bucket policy")
                    new_policy = {
                        "Version": "2012-10-17",
                        "Id": "NewPolicy",
                        "Statement": existing_statement,
                    }
                    s3.put_bucket_policy(
                        Bucket=bucket, Policy=json.dumps(new_policy))
                    print(f"Policy created for the following bucket: {bucket}")
        except s3.exceptions.from_code("NoSuchBucketPolicy"):
            print(
                f"No bucket policy exists for {bucket}")
            print(f"Creating a new bucket policy")
            new_policy = {
                "Version": "2012-10-17",
                "Id": "EnforceSSLEncryption",
                "Statement": ssl_statement,
            }
            s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(new_policy))
            print(f"Policy created for the following bucket: {bucket}")
