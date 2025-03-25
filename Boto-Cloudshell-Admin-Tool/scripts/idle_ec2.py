import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
cw = boto3.client('cloudwatch')
resource = boto3.resource('ec2')

CPU_THRESHOLD = 5.0       # %
NET_THRESHOLD_MB = 5.0    # MB over LOOKBACK_DAYS
LOOKBACK_DAYS = 7

skip_all = False
auto_terminate = False
pending_idle_instances = []

def get_instances():
    response = ec2.describe_instances(Filters=[
        {"Name": "instance-state-name", "Values": ["running"]}
    ])
    instances = []
    for r in response['Reservations']:
        for i in r['Instances']:
            instances.append(i)
    return instances

def get_average_cpu(instance_id):
    end = datetime.utcnow()
    start = end - timedelta(days=LOOKBACK_DAYS)

    metrics = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start,
        EndTime=end,
        Period=3600 * 6,
        Statistics=['Average']
    )
    datapoints = metrics['Datapoints']
    if not datapoints:
        return 0.0
    avg = sum(dp['Average'] for dp in datapoints) / len(datapoints)
    return round(avg, 2)

def get_network_io(instance_id):
    end = datetime.utcnow()
    start = end - timedelta(days=LOOKBACK_DAYS)
    total_bytes = 0

    for metric in ['NetworkIn', 'NetworkOut']:
        stats = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric,
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start,
            EndTime=end,
            Period=3600 * 6,
            Statistics=['Sum']
        )
        total_bytes += sum(dp['Sum'] for dp in stats['Datapoints'])

    total_mb = total_bytes / (1024 * 1024)
    return round(total_mb, 2)

def act_on_idle_instance(instance):
    global skip_all, auto_terminate, pending_idle_instances

    instance_id = instance['InstanceId']
    name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
    print(f"\n⚠️  IDLE DETECTED: {name} ({instance_id})")

    if skip_all:
        print("⏭️ Skipping due to skip-all flag.")
        pending_idle_instances.append(instance_id)
        return

    if auto_terminate:
        terminate_instance(instance_id)
        return

    print("Options:")
    print("  [1] Stop instance")
    print("  [2] Terminate instance")
    print("  [3] Tag for review")
    print("  [4] Skip all remaining")
    print("  [5] Exit script")
    print("  [6] Auto-terminate all remaining idle instances under threshold")
    choice = input("Choose action: ").strip()

    inst = resource.Instance(instance_id)

    if choice == '1':
        inst.stop()
        print(f"🛑 Stopping {instance_id}")
    elif choice == '2':
        inst.terminate()
        print(f"🗑️ Terminating {instance_id}")
    elif choice == '3':
        ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'IdleCheck', 'Value': 'Review'}])
        print(f"🏷️ Tagged {instance_id} for review")
    elif choice == '4':
        skip_all = True
        pending_idle_instances.append(instance_id)
        print("🔁 Will skip all remaining idle instance prompts.")
    elif choice == '5':
        print("🚪 Exiting script by user request.")
        exit(0)
    elif choice == '6':
        confirm = input("⚠️ Are you sure you want to terminate ALL remaining idle instances? (y/N): ").strip().lower()
        if confirm == 'y':
            auto_terminate = True
            terminate_instance(instance_id)
        else:
            print("❌ Auto-terminate cancelled.")
    else:
        print("⏭️ Skipped.")
        pending_idle_instances.append(instance_id)

def terminate_instance(instance_id):
    try:
        resource.Instance(instance_id).terminate()
        print(f"💥 Terminated {instance_id}")
    except Exception as e:
        print(f"❌ Failed to terminate {instance_id}: {e}")

def main():
    instances = get_instances()
    if not instances:
        print("✅ No running instances found.")
        return

    print(f"🔍 Checking {len(instances)} running EC2 instance(s)...")

    for inst in instances:
        instance_id = inst['InstanceId']
        name = next((tag['Value'] for tag in inst.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
        cpu = get_average_cpu(instance_id)
        net = get_network_io(instance_id)

        print(f"\n🖥️ {name} ({instance_id})")
        print(f"   🔧 CPU: {cpu:.2f}%")
        print(f"   🌐 Network In+Out: {net:.2f} MB (last {LOOKBACK_DAYS}d)")

        if cpu < CPU_THRESHOLD and net < NET_THRESHOLD_MB:
            act_on_idle_instance(inst)

    if auto_terminate and pending_idle_instances:
        print(f"\n💣 Auto-terminated {len(pending_idle_instances)} idle instances.")
    elif skip_all and pending_idle_instances:
        print(f"\n📝 You skipped review for {len(pending_idle_instances)} idle instances.")
        print("You can run the script again or use a bulk action on the skipped list.")

if __name__ == "__main__":
    main()
