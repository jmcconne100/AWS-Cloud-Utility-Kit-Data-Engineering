import boto3
from botocore.exceptions import ClientError
import os
import gzip

s3 = boto3.client('s3')

def enable_access_logs(target_bucket, log_bucket, log_prefix='logs/'):
    try:
        # Enable logging
        s3.put_bucket_logging(
            Bucket=target_bucket,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': log_bucket,
                    'TargetPrefix': log_prefix
                }
            }
        )
        print(f"✅ Enabled access logs for '{target_bucket}' to '{log_bucket}/{log_prefix}'")
    except ClientError as e:
        print(f"❌ Failed to enable access logging: {e}")


def list_logs(log_bucket, log_prefix='logs/'):
    print(f"\n📄 Available log files in s3://{log_bucket}/{log_prefix}:")
    response = s3.list_objects_v2(Bucket=log_bucket, Prefix=log_prefix)
    logs = response.get('Contents', [])
    if not logs:
        print("(No logs found yet — logging might take a few minutes to generate.)")
        return []

    for i, obj in enumerate(logs):
        print(f"[{i}] {obj['Key']} ({obj['Size']} bytes)")
    return [obj['Key'] for obj in logs]


def download_and_view_log(log_bucket, key):
    filename = os.path.basename(key)
    download_path = f"/tmp/{filename}"
    s3.download_file(log_bucket, key, download_path)

    if filename.endswith(".gz"):
        with gzip.open(download_path, 'rt') as f:
            print(f"\n🔍 Contents of {filename}:")
            print(f.read())
    else:
        with open(download_path, 'r') as f:
            print(f"\n🔍 Contents of {filename}:")
            print(f.read())

def main():
    print("S3 Access Log Setup and Viewer")
    print("==============================")
    print("[1] Enable access logs on a bucket")
    print("[2] View access logs")
    print("[0] Exit")

    choice = input("Choose an option: ")

    if choice == '1':
        target = input("Enter the bucket to enable logging on: ")
        logbucket = input("Enter the logging bucket: ")
        prefix = input("Enter a prefix for the logs (default 'logs/'): ") or 'logs/'
        enable_access_logs(target, logbucket, prefix)

    elif choice == '2':
        logbucket = input("Enter the bucket storing logs: ")
        prefix = input("Enter the prefix for logs (default 'logs/'): ") or 'logs/'
        keys = list_logs(logbucket, prefix)
        if keys:
            idx = input("Enter index of log to view (or press Enter to cancel): ")
            if idx.isdigit() and int(idx) < len(keys):
                download_and_view_log(logbucket, keys[int(idx)])
    else:
        print("👋 Exiting")

if __name__ == '__main__':
    main()
