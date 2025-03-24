import boto3
from collections import defaultdict
from datetime import datetime, timezone, timedelta

s3 = boto3.client('s3')
MB = 1024 * 1024
GB = 1024 * MB
STALE_DAYS = 30

# Estimated monthly cost per GB (you can update for your region)
COST_PER_GB = {
    'STANDARD': 0.023,
    'GLACIER': 0.004,
    'DEEP_ARCHIVE': 0.00099,
    'STANDARD_IA': 0.0125,
    'ONEZONE_IA': 0.01
}

def list_buckets():
    response = s3.list_buckets()
    return [b['Name'] for b in response['Buckets']]

def scan_prefix(bucket, prefix=''):
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    total_size = 0
    total_files = 0
    latest_time = datetime(1970, 1, 1, tzinfo=timezone.utc)

    for page in pages:
        for obj in page.get('Contents', []):
            total_files += 1
            total_size += obj['Size']
            if obj['LastModified'] > latest_time:
                latest_time = obj['LastModified']

    return total_files, total_size, latest_time

def get_replication_status(bucket_name):
    try:
        response = s3.get_bucket_replication(Bucket=bucket_name)
        rules = response['ReplicationConfiguration']['Rules']
        dests = []
        for rule in rules:
            dest_bucket_arn = rule['Destination']['Bucket']
            dest_region = dest_bucket_arn.split(':')[3]  # arn:aws:s3:::dest-bucket
            prefix = rule.get('Filter', {}).get('Prefix', 'Entire bucket')
            dests.append((dest_region, prefix))
        return dests
    except s3.exceptions.ClientError as e:
        if "ReplicationConfigurationNotFoundError" in str(e):
            return None
        else:
            raise

def profile_bucket(bucket):
    print(f"\n📂 Bucket: {bucket}")

    replication = get_replication_status(bucket)
    if replication:
        print("   🔄 Multi-Region Replication enabled:")
        for region, prefix in replication:
            print(f"      ➤ To region: {region} — Prefix: {prefix}")
    else:
        print("   ❌ No replication detected")

def drill_down(bucket):
    result = s3.list_objects_v2(Bucket=bucket, Delimiter='/')

    if 'CommonPrefixes' not in result and 'Contents' not in result:
        print("   (empty)")
        return

    folders = [p['Prefix'] for p in result.get('CommonPrefixes', [])]
    if not folders and 'Contents' in result:
        folders = ['']  # Just root-level files

    for prefix in folders:
        count, size, lastmod = scan_prefix(bucket, prefix)
        size_mb = size / MB
        size_gb = size / GB
        estimated_cost = size_gb * COST_PER_GB.get('STANDARD', 0.023)
        stale = (datetime.now(timezone.utc) - lastmod).days > STALE_DAYS
        lastmod_fmt = lastmod.strftime('%Y-%m-%d')

        stale_tag = "⚠️ STALE" if stale else ""
        print(f"  📁 {prefix or '[root]'}")
        print(f"     🧮 Files: {count}")
        print(f"     💾 Size: {size_mb:.2f} MB")
        print(f"     🕒 Last modified: {lastmod_fmt} {stale_tag}")
        print(f"     💰 Est. Monthly Cost: ${estimated_cost:.2f}")

def main():
    buckets = list_buckets()
    for b in buckets:
        profile_bucket(b)

    print("\n📌 Drill down into a specific bucket to analyze subfolders.")
    selected = input("Enter bucket name to drill into (or press Enter to skip): ").strip()
    if selected and selected in buckets:
        drill_down(selected)
    elif selected:
        print("❌ Invalid bucket name.")

if __name__ == "__main__":
    main()
