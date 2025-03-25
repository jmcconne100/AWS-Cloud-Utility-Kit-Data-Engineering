import boto3

ec2 = boto3.resource('ec2')

def get_instances(state='running'):
    filters = [{'Name': 'instance-state-name', 'Values': [state]}]
    return list(ec2.instances.filter(Filters=filters))

def format_tags(tags):
    return ", ".join(f"{tag['Key']}={tag['Value']}" for tag in tags or []) or "⚠️ No tags"

def list_resources(instances):
    indexed = []
    print("\n🖥️ EC2 Instances and Volumes:")
    count = 0

    for inst in instances:
        name = next((tag['Value'] for tag in inst.tags or [] if tag['Key'] == 'Name'), 'Unnamed')
        tag_summary = format_tags(inst.tags)
        print(f"[{count}] Instance: {name} ({inst.id}) — {tag_summary}")
        indexed.append(('instance', inst))
        count += 1

        for vol in inst.volumes.all():
            vol.load()
            tag_summary = format_tags(vol.tags)
            print(f"[{count}] └── Volume: {vol.id} — {tag_summary}")
            indexed.append(('volume', vol))
            count += 1

    return indexed

def tag_resource(resource_type, resource):
    print(f"\n🏷️ Current tags for {resource_type} {resource.id}:")
    print(format_tags(resource.tags))

    while True:
        key = input("Enter tag key (or leave empty to stop): ").strip()
        if not key:
            break
        value = input(f"Enter value for '{key}': ").strip()
        if value:
            resource.create_tags(Tags=[{'Key': key, 'Value': value}])
            print(f"✅ Applied tag: {key}={value}")
        else:
            print("⚠️ Skipped empty value.")

def main():
    instances = get_instances()
    if not instances:
        print("No running instances found.")
        exit()

    indexed_resources = list_resources(instances)

    while True:
        selection = input("\nEnter number to tag resource (or press Enter to exit): ").strip()
        if not selection:
            break
        if not selection.isdigit():
            print("❌ Invalid input.")
            continue

        idx = int(selection)
        if 0 <= idx < len(indexed_resources):
            rtype, rsrc = indexed_resources[idx]
            tag_resource(rtype, rsrc)
        else:
            print("❌ Number out of range.")

if __name__ == "__main__":
    main()
