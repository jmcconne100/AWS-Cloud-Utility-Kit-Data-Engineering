from collections import deque
from datetime import datetime, timedelta
import csv
import io
import boto3

# CONFIG
WINDOW_SECONDS = 60
BUCKET = 'my-data-pipeline'
INPUT_KEY = 'stream-data/events.csv'
OUTPUT_KEY = 'rolling-output/aggregated.csv'

s3 = boto3.client('s3')

def parse_timestamp(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def process_stream(events: list) -> list:
    window = deque()
    result = []

    for row in events:
        ts = parse_timestamp(row[0])
        val = float(row[1])
        window.append((ts, val))

        # Remove old events
        while (ts - window[0][0]).total_seconds() > WINDOW_SECONDS:
            window.popleft()

        values = [v for _, v in window]
        avg = sum(values) / len(values)
        result.append([row[0], val, round(avg, 2)])

    return result

def read_csv_from_s3(bucket: str, key: str):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return list(csv.reader(io.StringIO(obj['Body'].read().decode())))[1:]  # skip header

def write_output_to_s3(rows: list, bucket: str, key: str):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["timestamp", "value", "rolling_avg"])
    writer.writerows(rows)
    buffer.seek(0)
    s3.put_object(Body=buffer.getvalue(), Bucket=bucket, Key=key)

def run():
    rows = read_csv_from_s3(BUCKET, INPUT_KEY)
    processed = process_stream(rows)
    write_output_to_s3(processed, BUCKET, OUTPUT_KEY)
    print(f"Wrote rolling averages to: s3://{BUCKET}/{OUTPUT_KEY}")

if __name__ == "__main__":
    run()
