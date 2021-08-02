import json
from typing import Any, Dict, List

import boto3

# import requests
# Create an S3 client
s3 = boto3.client("s3")
s3Bucket = boto3.resource('s3')

buckets = ["", "", ""]

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

    # Check if bucket actually exists
    if s3Bucket.Bucket(bucket).creation_date is None:
        print(f"The following bucket does not exist: {bucket}")
    else:
        try:

            # Get the existing bucket policy if it exists
            existing_policy: str = s3.get_bucket_policy(Bucket=bucket)
            statement: Dict[str, Any] = json.loads(existing_policy["Policy"])

            # Save Existing Policy to JSON File
            with open(f"original_policies_sandbox/{bucket}.json", 'w', encoding='utf-8') as f:
                json.dump(statement, f, ensure_ascii=False, indent=4)

            existing_statement = statement.get("Statement", [])
            new_statement = existing_statement
            new_statement.append(ssl_statement)

            # Check to see if the following condition already present in the existing policy
            key_value: str = '{"Bool": {"aws:SecureTransport": "false"}}'
            condition = json.dumps(existing_statement[0].get("Condition"))

            if condition == key_value:
                print("This Condition Already Exists")
                print(f"Skipping Bucket: {bucket}")
            else:
                print(f"Creating bucket policy for {bucket}")
                new_policy = {
                    "Version": "2012-10-17",
                    "Id": "NewPolicy",
                    "Statement": new_statement,
                }
                s3.put_bucket_policy(
                    Bucket=bucket, Policy=json.dumps(new_policy))
                # print(json.dumps(new_policy))
                print(
                    f"Policy created for the following bucket: {bucket}")
        # If the bucket has no existing policy at all we create our policy here
        except s3.exceptions.from_code("NoSuchBucketPolicy"):
            print(f"No bucket policy exists for {bucket}")
            print(f"Creating a new bucket policy for: {bucket}")
            new_policy = {
                "Version": "2012-10-17",
                "Id": "EnforceSSLEncryption",
                "Statement": ssl_statement,
            }
            s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(new_policy))
            print(f"Policy created for the following bucket: {bucket}")
