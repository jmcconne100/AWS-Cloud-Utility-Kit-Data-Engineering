import boto3
import pandas as pd
import io

# CONFIG
BUCKET = 'my-data-pipeline'
INPUT_KEY = 'raw/input.csv'
OUTPUT_KEY = 'processed/output.parquet'
EXPECTED_COLUMNS = ['id', 'name', 'event_type', 'timestamp', 'value']

s3 = boto3.client('s3')

def download_csv(bucket, key) -> pd.DataFrame:
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    # Drop unexpected columns
    df = df[[col for col in df.columns if col in EXPECTED_COLUMNS]]

    # Add missing columns with NaN
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Enforce order
    df = df[EXPECTED_COLUMNS]

    # Drop rows with null IDs or timestamps
    df = df.dropna(subset=['id', 'timestamp'])

    # Standardize event types
    df['event_type'] = df['event_type'].str.lower().str.strip()

    return df

def write_parquet_to_s3(df: pd.DataFrame, bucket, key):
    buffer = io.BytesIO()
    df.to_parquet(buffer, engine='pyarrow', index=False)
    buffer.seek(0)
    s3.upload_fileobj(buffer, bucket, key)

def main():
    print("📥 Downloading CSV from S3...")
    df = download_csv(BUCKET, INPUT_KEY)

    print("🧹 Cleaning and validating...")
    cleaned_df = clean_and_validate(df)

    print("📤 Writing Parquet to S3...")
    write_parquet_to_s3(cleaned_df, BUCKET, OUTPUT_KEY)

    print(f"✅ Done. File saved to: s3://{BUCKET}/{OUTPUT_KEY}")

if __name__ == "__main__":
    main()
