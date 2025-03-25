import boto3
import pandas as pd
import io

BUCKET = 'my-data-pipeline'
INPUT_KEY = 'raw-data/incoming.csv'
EXPECTED_COLUMNS = ['id', 'timestamp', 'user_id', 'event_type', 'value']
OUTPUT_KEY = 'cleaned-data/patched.csv'

s3 = boto3.client('s3')

def download_csv(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def upload_csv(df: pd.DataFrame, bucket, key):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    s3.put_object(Body=buffer.getvalue(), Bucket=bucket, Key=key)

def validate_and_patch(df: pd.DataFrame, expected: list):
    actual = list(df.columns)
    missing = list(set(expected) - set(actual))
    extra = list(set(actual) - set(expected))
    common = list(set(actual) & set(expected))

    print(f"\n✅ Matched columns: {sorted(common)}")
    print(f"⚠️  Missing columns: {sorted(missing)}")
    print(f"⚠️  Extra columns: {sorted(extra)}")

    # Patch: Add missing with NaN, drop extra
    for col in missing:
        df[col] = None
    df = df[expected]  # enforce order and drop extras

    return df

def main():
    df = download_csv(BUCKET, INPUT_KEY)
    patched_df = validate_and_patch(df, EXPECTED_COLUMNS)
    upload_csv(patched_df, BUCKET, OUTPUT_KEY)
    print(f"\n✅ Patched and uploaded cleaned file to s3://{BUCKET}/{OUTPUT_KEY}")

if __name__ == "__main__":
    main()
