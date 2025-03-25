import boto3
import pandas as pd
import io
import os

s3 = boto3.client('s3')

# CONFIG
EXPECTED_COLUMNS = ['id', 'timestamp', 'value']
DEST_PREFIXES = {
    "valid": "processing/",
    "invalid": "rejected/",
    "quarantine": "quarantine/"
}
MAX_EMPTY_MB = 0.01  # ~10KB

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        try:
            # Check file size
            head = s3.head_object(Bucket=bucket, Key=key)
            size_mb = head['ContentLength'] / (1024 * 1024)
            print(f"📏 File size: {size_mb:.4f} MB")

            if size_mb < MAX_EMPTY_MB:
                dest = DEST_PREFIXES['quarantine']
            else:
                # Read and parse the CSV
                obj = s3.get_object(Bucket=bucket, Key=key)
                body = obj['Body'].read()
                df = pd.read_csv(io.BytesIO(body))

                # Validate schema
                if list(df.columns) == EXPECTED_COLUMNS:
                    dest = DEST_PREFIXES['valid']
                else:
                    dest = DEST_PREFIXES['invalid']
        except Exception as e:
            print(f"❌ Error: {e}")
            dest = DEST_PREFIXES['invalid']

        # Move to appropriate location
        dest_key = dest + os.path.basename(key)
        copy_source = {'Bucket': bucket, 'Key': key}
        s3.copy_object(Bucket=bucket, CopySource=copy_source, Key=dest_key)
        s3.delete_object(Bucket=bucket, Key=key)
        print(f"✅ Moved: {key} → {dest_key}")
