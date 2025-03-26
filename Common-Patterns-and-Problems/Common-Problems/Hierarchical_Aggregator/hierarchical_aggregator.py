import boto3
import pandas as pd
import io

BUCKET = 'my-data-pipeline'
INPUT_KEY = 'metrics/sales.csv'
OUTPUT_KEY = 'aggregated/rollup.csv'

GROUP_LEVELS = ['region', 'country', 'store']  # hierarchy
MEASURE = 'revenue'

s3 = boto3.client('s3')

def read_csv_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def write_csv_to_s3(df, bucket, key):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    s3.put_object(Body=buffer.getvalue(), Bucket=bucket, Key=key)

def hierarchical_aggregate(df: pd.DataFrame, levels: list, measure: str):
    rollups = []

    # Aggregate at each level of the hierarchy
    for i in range(len(levels)):
        group_cols = levels[:i+1]
        agg = df.groupby(group_cols)[measure].sum().reset_index()
        # Fill Nones for deeper levels
        for col in levels[i+1:]:
            agg[col] = None
        rollups.append(agg)

    # Add total rollup
    total = pd.DataFrame({**{col: [None] for col in levels}, measure: [df[measure].sum()]})
    rollups.append(total)

    # Combine all rollups
    final = pd.concat(rollups, ignore_index=True)
    return final[levels + [measure]]

def main():
    df = read_csv_from_s3(BUCKET, INPUT_KEY)
    rolled_up = hierarchical_aggregate(df, GROUP_LEVELS, MEASURE)
    write_csv_to_s3(rolled_up, BUCKET, OUTPUT_KEY)
    print(f"✅ Aggregated rollup written to: s3://{BUCKET}/{OUTPUT_KEY}")

if __name__ == "__main__":
    main()
