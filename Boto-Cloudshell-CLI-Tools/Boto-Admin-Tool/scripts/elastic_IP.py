import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
resource_ec2 = boto3.resource('ec2')

def list_eips(tag_filter=None):
    try:
        response = ec2.describe_addresses()
        addresses = response['Addresses']
    except ClientError as e:
        print("❌ Error retrieving EIPs:", e)
        return []

    print("\n📡 Elastic IP Addresses:\n")
    unused_eips = []

    for idx, addr in enumerate(addresses):
        public_ip = addr.get('PublicIp')
        instance_id = addr.get('InstanceId')
        allocation_id = addr.get('AllocationId')
        association_id = addr.get('AssociationId')
        domain = addr.get('Domain')

        # If a tag filter is provided, and the EIP is attached, check tags
        if tag_filter and instance_id:
            instance = resource_ec2.Instance(instance_id)
            tags = {tag['Key']: tag['Value'] for tag in instance.tags or []}
            key, val = tag_filter
            if tags.get(key) != val:
                print(f"[{idx}] {public_ip} — ⏭️ Skipped (Tag {key} != {val})")
                continue

        if instance_id:
            print(f"[{idx}] {public_ip} — ✅ Attached to {instance_id} ({domain})")
        else:
            print(f"[{idx}] {public_ip} — ⚠️ Unused — ⚠️ Costs $7.20/mo")
            unused_eips.append({
                'index': idx,
                'public_ip': public_ip,
                'allocation_id': allocation_id
            })

    print(f"\n💸 Estimated monthly cost for unused EIPs: ${len(unused_eips) * 7.20:.2f}")
    return unused_eips

def release_eip(allocation_id, public_ip):
    try:
        ec2.release_address(AllocationId=allocation_id)
        print(f"🗑️ Released unused EIP: {public_ip}")
    except ClientError as e:
        print(f"❌ Failed to release {public_ip}: {e}")

def main():
    tag_key = input("\n🔎 Filter unused EIPs by tag key (or press Enter to skip): ").strip()
    tag_val = ""
    tag_filter = None

    if tag_key:
        tag_val = input(f"🔎 Value for tag key '{tag_key}': ").strip()
        tag_filter = (tag_key, tag_val)

    unused = list_eips(tag_filter)
    if not unused:
        print("✅ No matching unused EIPs found.")
        return

    auto = input("\n⚙️ Auto-release all unused EIPs? (y/N): ").strip().lower()
    if auto == 'y':
        for eip in unused:
            release_eip(eip['allocation_id'], eip['public_ip'])
    else:
        release = input("Would you like to release any manually? (y/N): ").strip().lower()
        if release != 'y':
            print("❌ Skipping release.")
            return

        for eip in unused:
            choice = input(f"Release {eip['public_ip']}? (y/N): ").strip().lower()
            if choice == 'y':
                release_eip(eip['allocation_id'], eip['public_ip'])
            else:
                print(f"↩️ Skipped {eip['public_ip']}")

if __name__ == "__main__":
    main()
