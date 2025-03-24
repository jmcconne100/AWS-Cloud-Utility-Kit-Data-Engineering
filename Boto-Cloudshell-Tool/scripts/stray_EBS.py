import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
resource_ec2 = boto3.resource('ec2')

PRICE_PER_GB = 0.10  # You can update this based on your region

def list_unattached_volumes():
    print("\n🔍 Scanning for unattached EBS volumes...\n")
    try:
        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )['Volumes']
    except ClientError as e:
        print("❌ Failed to retrieve volumes:", e)
        return []

    orphaned = []
    for idx, vol in enumerate(volumes):
        vol_id = vol['VolumeId']
        size = vol['Size']
        cost = size * PRICE_PER_GB
        tags = {tag['Key']: tag['Value'] for tag in vol.get('Tags', [])}
        name = tags.get('Name', 'Unnamed')
        create_time = vol['CreateTime'].strftime('%Y-%m-%d')
        print(f"[{idx}] {vol_id} ({name}) — {size} GiB — ${cost:.2f}/mo — Created: {create_time}")
        orphaned.append({
            'index': idx,
            'volume_id': vol_id,
            'size': size,
            'tags': tags
        })

    print(f"\n💸 Estimated total monthly cost: ${sum(v['size'] for v in orphaned) * PRICE_PER_GB:.2f}")
    return orphaned

def snapshot_and_delete(vol_id):
    try:
        snap = ec2.create_snapshot(VolumeId=vol_id, Description="Snapshot before auto-deletion")
        print(f"📸 Created snapshot {snap['SnapshotId']} for {vol_id}")
        waiter = ec2.get_waiter('snapshot_completed')
        waiter.wait(SnapshotIds=[snap['SnapshotId']])
        print("✅ Snapshot completed.")

        ec2.delete_volume(VolumeId=vol_id)
        print(f"🗑️ Deleted volume {vol_id}")
    except ClientError as e:
        print(f"❌ Failed snapshot/delete for {vol_id}:", e)

def tag_volume(vol_id, key='CleanupCandidate', value='Yes'):
    try:
        ec2.create_tags(Resources=[vol_id], Tags=[{'Key': key, 'Value': value}])
        print(f"🏷️ Tagged {vol_id} with {key}={value}")
    except ClientError as e:
        print(f"❌ Failed to tag volume {vol_id}:", e)

def delete_volume(vol_id):
    try:
        ec2.delete_volume(VolumeId=vol_id)
        print(f"🗑️ Deleted volume {vol_id}")
    except ClientError as e:
        print(f"❌ Failed to delete volume {vol_id}:", e)

def main():
    volumes = list_unattached_volumes()
    if not volumes:
        print("✅ No unattached volumes found.")
        return

    print("\n⚙️ Choose an action for each volume:")
    print("  [1] Snapshot + Delete")
    print("  [2] Delete only")
    print("  [3] Tag for review")
    print("  [Enter] Skip")

    for v in volumes:
        choice = input(f"\nAction for {v['volume_id']}? [1/2/3]: ").strip()
        if choice == '1':
            snapshot_and_delete(v['volume_id'])
        elif choice == '2':
            delete_volume(v['volume_id'])
        elif choice == '3':
            tag_volume(v['volume_id'])
        else:
            print(f"⏭️ Skipped {v['volume_id']}")

if __name__ == "__main__":
    main()
