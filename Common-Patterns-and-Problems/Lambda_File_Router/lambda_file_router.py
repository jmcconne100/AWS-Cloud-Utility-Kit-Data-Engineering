import boto3
import pandas as pd
import os
import io

s3 = boto3.client('s3')

# === CONFIG ===
EXPECTED_COLUMNS = ["id", "timestamp", "value"]
TARGET_PREFIXES = {
    "valid": "processing/",
    "small": "small-files/",
    "invalid": "rejected/"
}
MAX_VALID_SIZE_MB = 1

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        try:
            # Get the object metadata
            response = s3.head_object(Bucket=bucket, Key=key)
            size_mb = response['ContentLength'] / (1024 * 1024)

            # Download the file
            obj = s3.get_object(Bucket=bucket, Key=key)
            body = obj['Body'].read()
            df = pd.read_csv(io.BytesIO(body))

            # Check for valid schema
            if list(df.columns) == EXPECTED_COLUMNS:
                if size_mb < MAX_VALID_SIZE_MB:
                    dest_prefix = TARGET_PREFIXES['small']
                else:
                    dest_prefix = TARGET_PREFIXES['valid']
            else:
                dest_prefix = TARGET_PREFIXES['invalid']
        except Exception as e:
            print(f"Error processing file {key}: {e}")
            dest_prefix = TARGET_PREFIXES['invalid']

        dest_key = dest_prefix + os.path.basename(key)
        copy_source = {'Bucket': bucket, 'Key': key}

        # Copy and delete (move)
        s3.copy_object(Bucket=bucket, CopySource=copy_source, Key=dest_key)
        s3.delete_object(Bucket=bucket, Key=key)

        print(f"Routed {key} → {dest_key}")
