# Append-S3-Bucket-Policy

### Background

CloudFormation nor CDK will allow you to mutate an existing bucket policy. Current boto3 API doesn't have a function to APPEND the bucket policy either.
You need load and manipulate the JSON yourself. E.g. write script load the policy into a dict, append the "Statement" element list,
then use the policy.put to replace the whole policy.

This lambda function does the following:

1. Checks for an existing policy
2. Checks for specific coniditions inside of the the existing policy.

If the condition exists it will skip over the bucket
If there is an existing policy it will append a new statement to the policy
If there is not an existing policy it will create a new policy
