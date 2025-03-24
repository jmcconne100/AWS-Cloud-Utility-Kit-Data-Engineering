import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def get_tag_value(tags, key):
    if not tags:
        return None
    for tag in tags:
        if tag['Key'] == key:
            return tag['Value']
    return None

def list_instances_by_schedule():
    instances = list(ec2.instances.all())
    managed = []
    unmanaged = []

    print("\n📋 EC2 Instance Overview:\n")
    for idx, inst in enumerate(instances):
        name = get_tag_value(inst.tags, 'Name') or 'Unnamed'
        schedule = get_tag_value(inst.tags, 'Schedule')
        label = f"[{idx}] {name} ({inst.id}) — State: {inst.state['Name']}"

        if schedule == 'WorkHours':
            print(f"⏰ {label} — Schedule: WorkHours")
            managed.append(inst)
        else:
            print(f"❌ {label} — Schedule: {schedule or 'None'}")
            unmanaged.append(inst)
    return instances

def modify_schedule_tag(instances):
    idx = input("\n🔧 Enter the instance number to modify (or press Enter to cancel): ").strip()
    if not idx.isdigit():
        print("❌ Cancelled.")
        return

    idx = int(idx)
    if not (0 <= idx < len(instances)):
        print("❌ Invalid number.")
        return

    inst = instances[idx]
    inst_id = inst.id
    name = get_tag_value(inst.tags, 'Name') or 'Unnamed'

    print(f"\n🛠️ Modifying tags for {name} ({inst_id})")
    print("Choose Schedule:")
    print("  [1] WorkHours (8AM–6PM Weekdays)")
    print("  [2] AlwaysOn")
    print("  [3] Remove tag")

    choice = input("Select an option: ").strip()
    if choice == '1':
        inst.create_tags(Tags=[{'Key': 'Schedule', 'Value': 'WorkHours'}])
        print("✅ Tag applied: Schedule=WorkHours")
    elif choice == '2':
        inst.create_tags(Tags=[{'Key': 'Schedule', 'Value': 'AlwaysOn'}])
        print("✅ Tag applied: Schedule=AlwaysOn")
    elif choice == '3':
        try:
            inst.delete_tags(Tags=[{'Key': 'Schedule'}])
            print("🗑️ Schedule tag removed.")
        except ClientError as e:
            print("❌ Failed to remove tag:", e)
    else:
        print("❌ Cancelled.")

def create_instance_with_schedule():
    name = input("\n📛 Enter a name for the instance: ").strip()
    ami_id = input("📦 Enter AMI ID (or leave blank for Amazon Linux 2): ").strip() or 'ami-0c02fb55956c7d316'  # default Amazon Linux 2
    key_name = input("🔑 Enter key pair name (must exist): ").strip()

    try:
        instance = ec2.create_instances(
            ImageId=ami_id,
            InstanceType='t2.micro',
            KeyName=key_name,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': name},
                        {'Key': 'Schedule', 'Value': 'WorkHours'}
                    ]
                }
            ]
        )[0]
        print(f"🚀 Launching instance {instance.id} with Schedule=WorkHours tag")
    except ClientError as e:
        print("❌ Launch failed:", e)

def main():
    while True:
        print("\n========== EC2 Schedule Manager ==========")
        print("1️⃣  View instances by schedule")
        print("2️⃣  Modify Schedule tag on an instance")
        print("3️⃣  Launch new EC2 with predefined schedule")
        print("4️⃣  Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            all_instances = list_instances_by_schedule()
        elif choice == '2':
            all_instances = list_instances_by_schedule()
            modify_schedule_tag(all_instances)
        elif choice == '3':
            create_instance_with_schedule()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
