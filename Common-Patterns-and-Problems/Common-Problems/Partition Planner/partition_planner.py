import boto3
import pandas as pd
import io
from collections import Counter

BUCKET = 'my-data-pipeline'
INPUT_KEY = 'raw-data/events.csv'
CANDIDATE_COLUMNS = ['region', 'event_type']

s3 = boto3.client('s3')

def download_csv_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def compute_partition_stats(df: pd.DataFrame, columns: list):
    results = []
    for col in columns:
        freqs = Counter(df[col])
        cardinality = len(freqs)
        top_values = freqs.most_common(5)
        skew = max(freqs.values()) / (sum(freqs.values()) / cardinality)

        results.append({
            'column': col,
            'cardinality': cardinality,
            'top_values': top_values,
            'skew_ratio': round(skew, 2),
        })
    return results

def suggest_partitions(stats):
    print("\nPartition Key Suggestions:")
    for stat in stats:
        col = stat['column']
        print(f"→ {col}")
        print(f"   - Cardinality: {stat['cardinality']}")
        print(f"   - Skew Ratio: {stat['skew_ratio']}")
        print(f"   - Top Values: {stat['top_values']}")
        if stat['cardinality'] > 50:
            print(f"   ⚠️  High cardinality — avoid as primary partition key")
        elif stat['skew_ratio'] > 5:
            print(f"   ⚠️  Skewed values — consider compounding with another key")
        else:
            print(f"   ✅ Good candidate for partitioning")
        print()

def main():
    df = download_csv_from_s3(BUCKET, INPUT_KEY)
    stats = compute_partition_stats(df, CANDIDATE_COLUMNS)
    suggest_partitions(stats)

if __name__ == "__main__":
    main()
