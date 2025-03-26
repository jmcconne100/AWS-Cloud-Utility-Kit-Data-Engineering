import boto3
import pandas as pd
import io
import os
from typing import List

# CONFIG
BUCKET = 'my-data-pipeline'
INPUT_PREFIX = 'raw-data/'
OUTPUT_KEY = 'processed-data/combined_output.parquet'

s3 = boto3.client('s3')

def list_csv_keys(bucket: str, prefix: str) -> List[str]:
    keys = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.csv'):
                keys.append(obj['Key'])
    return keys

def read_csv_from_s3(key: str) -> pd.DataFrame:
    response = s3.get_object(Bucket=BUCKET, Key=key)
    body = response['Body'].read()
    df = pd.read_csv(io.BytesIO(body))
    return df

def write_parquet_to_s3(df: pd.DataFrame, output_key: str):
    buffer = io.BytesIO()
    df.to_parquet(buffer, engine='pyarrow', index=False)
    buffer.seek(0)
    s3.upload_fileobj(buffer, BUCKET, output_key)

def combine_csv_to_parquet():
    csv_keys = list_csv_keys(BUCKET, INPUT_PREFIX)
    if not csv_keys:
        print("No CSV files found.")
        return

    dfs = []
    for key in csv_keys:
        try:
            df = read_csv_from_s3(key)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {key}: {e}")

    combined_df = pd.concat(dfs, ignore_index=True)
    write_parquet_to_s3(combined_df, OUTPUT_KEY)
    print(f"Combined {len(csv_keys)} files and uploaded Parquet to: {OUTPUT_KEY}")

if __name__ == "__main__":
    combine_csv_to_parquet()
