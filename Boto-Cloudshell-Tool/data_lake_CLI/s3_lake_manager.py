import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')


def list_files(bucket, prefix=''):
    print(f"\n📂 Listing files in s3://{bucket}/{prefix}")
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            print(f" - {obj['Key']} ({obj['Size']} bytes)")


def copy_file(src_bucket, src_key, dest_bucket, dest_key):
    print(f"📄 Copying {src_key} to {dest_key} in {dest_bucket}")
    s3.copy_object(Bucket=dest_bucket, CopySource={'Bucket': src_bucket, 'Key': src_key}, Key=dest_key)


def move_file(src_bucket, src_key, dest_bucket, dest_key):
    print(f"🚚 Moving {src_key} to {dest_key} in {dest_bucket}")
    copy_file(src_bucket, src_key, dest_bucket, dest_key)
    delete_file(src_bucket, src_key)


def delete_file(bucket, key):
    print(f"🗑️ Deleting {key} from {bucket}")
    s3.delete_object(Bucket=bucket, Key=key)


def rename_file(bucket, old_key, new_key):
    print(f"✏️ Renaming {old_key} to {new_key} in {bucket}")
    move_file(bucket, old_key, bucket, new_key)


def recursive_copy(bucket, source_prefix, dest_prefix):
    print(f"📄 Recursively copying {source_prefix} to {dest_prefix}")
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=source_prefix):
        for obj in page.get('Contents', []):
            src_key = obj['Key']
            dest_key = src_key.replace(source_prefix, dest_prefix, 1)
            copy_file(bucket, src_key, bucket, dest_key)


def recursive_move(bucket, source_prefix, dest_prefix):
    print(f"🚚 Recursively moving {source_prefix} to {dest_prefix}")
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=source_prefix):
        for obj in page.get('Contents', []):
            src_key = obj['Key']
            dest_key = src_key.replace(source_prefix, dest_prefix, 1)
            move_file(bucket, src_key, bucket, dest_key)


def recursive_delete(bucket, prefix):
    print(f"🗑️ Recursively deleting {prefix} in {bucket}")
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            delete_file(bucket, obj['Key'])


def setup_data_lake(bucket_name, region='us-east-1'):
    print(f"🚀 Creating data lake bucket: {bucket_name}")
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region} if region != 'us-east-1' else {}
        )
        print("✅ Bucket created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print("ℹ️ Bucket already exists and is owned by you.")
        else:
            raise

    print("🔐 Enabling default encryption...")
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [{
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            }]
        }
    )

    print("🌍 Enabling public access block...")
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

    print("📁 Creating folders: raw/, processed/, temp/")
    for prefix in ['raw/', 'processed/', 'temp/']:
        s3.put_object(Bucket=bucket_name, Key=prefix)

    print("✅ Data lake setup complete.")


def main():
    while True:
        print("\nS3 File Manager")
        print("[1] List files")
        print("[2] Copy file")
        print("[3] Move file")
        print("[4] Delete file")
        print("[5] Rename file")
        print("[6] Recursive copy")
        print("[7] Recursive move")
        print("[8] Recursive delete")
        print("[9] Setup new data lake bucket")
        print("[0] Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            b = input("Bucket name: ")
            p = input("Prefix (optional): ")
            list_files(b, p)
        elif choice == '2':
            src_b = input("Source bucket: ")
            src_k = input("Source key: ")
            dst_b = input("Destination bucket: ")
            dst_k = input("Destination key: ")
            copy_file(src_b, src_k, dst_b, dst_k)
        elif choice == '3':
            src_b = input("Source bucket: ")
            src_k = input("Source key: ")
            dst_b = input("Destination bucket: ")
            dst_k = input("Destination key: ")
            move_file(src_b, src_k, dst_b, dst_k)
        elif choice == '4':
            b = input("Bucket name: ")
            k = input("Key to delete: ")
            delete_file(b, k)
        elif choice == '5':
            b = input("Bucket name: ")
            old = input("Old key: ")
            new = input("New key: ")
            rename_file(b, old, new)
        elif choice == '6':
            b = input("Bucket name: ")
            src = input("Source prefix: ")
            dst = input("Destination prefix: ")
            recursive_copy(b, src, dst)
        elif choice == '7':
            b = input("Bucket name: ")
            src = input("Source prefix: ")
            dst = input("Destination prefix: ")
            recursive_move(b, src, dst)
        elif choice == '8':
            b = input("Bucket name: ")
            p = input("Prefix to delete: ")
            recursive_delete(b, p)
        elif choice == '9':
            b = input("New bucket name: ")
            r = input("Region (default us-east-1): ") or 'us-east-1'
            setup_data_lake(b, r)
        elif choice == '0':
            print("👋 Exiting.")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
