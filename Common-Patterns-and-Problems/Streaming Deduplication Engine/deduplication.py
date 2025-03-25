from collections import deque
from datetime import datetime, timedelta
import csv
import io
import boto3

# CONFIG
WINDOW_MINUTES = 5
BUCKET = 'my-data-pipeline'
INPUT_KEY = 'stream-data/raw_events.csv'
OUTPUT_KEY = 'deduplicated/cleaned.csv'

s3 = boto3.client('s3')

def parse_timestamp(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def read_csv_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return list(csv.reader(io.StringIO(obj['Body'].read().decode())))[1:]  # skip header

def write_csv_to_s3(rows, bucket, key):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['timestamp', 'event_id', 'value'])
    writer.writerows(rows)
    buffer.seek(0)
    s3.put_object(Body=buffer.getvalue(), Bucket=bucket, Key=key)

def deduplicate_stream(events):
    dedup_cache = {}  # key = event_id, value = timestamp
    queue = deque()   # [(timestamp, event_id)]
    window = timedelta(minutes=WINDOW_MINUTES)
    results = []

    for row in events:
        ts = parse_timestamp(row[0])
        event_id = row[1]
        val = row[2]

        # Garbage collection: remove old entries
        while queue and (ts - queue[0][0]) > window:
            old_ts, old_id = queue.popleft()
            if dedup_cache.get(old_id) == old_ts:
                del dedup_cache[old_id]

        # Deduplication check
        if event_id not in dedup_cache:
            dedup_cache[event_id] = ts
            queue.append((ts, event_id))
            results.append(row)
        else:
            print(f"🛑 Duplicate detected: {event_id} at {ts}")

    return results

def main():
    rows = read_csv_from_s3(BUCKET, INPUT_KEY)
    deduped_rows = deduplicate_stream(rows)
    write_csv_to_s3(deduped_rows, BUCKET, OUTPUT_KEY)
    print(f"✅ Deduplicated stream written to: s3://{BUCKET}/{OUTPUT_KEY}")

if __name__ == "__main__":
    main()
