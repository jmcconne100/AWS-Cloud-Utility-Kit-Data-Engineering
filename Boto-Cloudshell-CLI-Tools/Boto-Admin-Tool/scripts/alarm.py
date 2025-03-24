import boto3
import argparse

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')

DEFAULT_METRIC = 'CPUUtilization'

METRIC_OPTIONS = {
    'CPUUtilization': 'AWS/EC2',
    'NetworkIn': 'AWS/EC2',
    'DiskReadOps': 'AWS/EC2',
    'StatusCheckFailed': 'AWS/EC2'
}

def list_running_instances_with_alarms():
    response = ec2.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']
    }])

    all_alarms = cloudwatch.describe_alarms()['MetricAlarms']
    instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')

            matching_alarms = []
            for alarm in all_alarms:
                for dim in alarm.get('Dimensions', []):
                    if dim['Name'] == 'InstanceId' and dim['Value'] == instance_id:
                        matching_alarms.append({
                            'name': alarm['AlarmName'],
                            'metric': alarm['MetricName'],
                            'state': alarm['StateValue']
                        })

            instances.append({
                'InstanceId': instance_id,
                'Name': name,
                'Alarms': matching_alarms
            })

    return instances

def display_instances(instances):
    print("\n🖥️ Running EC2 Instances:")
    for idx, inst in enumerate(instances):
        alarm_info = (
            ", ".join([f"{a['metric']} ({a['state']})" for a in inst['Alarms']])
            if inst['Alarms'] else "⚠️ None"
        )
        print(f"[{idx}] {inst['Name']} ({inst['InstanceId']}) — Alarms: {alarm_info}")

def create_alarm(instance_id, instance_name, metric, threshold, period, evals):
    namespace = METRIC_OPTIONS.get(metric)
    if not namespace:
        print(f"❌ Unsupported metric: {metric}")
        return

    alarm_name = f"{metric}-Alarm-{instance_name}-{instance_id[-6:]}"
    print(f"📊 Creating Alarm: {alarm_name} for metric {metric}")

    cloudwatch.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmDescription=f"{metric} > {threshold} for {evals * (period // 60)} minutes",
        ActionsEnabled=False,  # SNS later
        MetricName=metric,
        Namespace=namespace,
        Statistic='Average',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        Period=period,
        EvaluationPeriods=evals,
        Threshold=threshold,
        ComparisonOperator='GreaterThanThreshold',
        TreatMissingData='missing'
    )

    print(f"✅ Alarm created: {alarm_name}")

def delete_alarms(attached_alarms):
    if not attached_alarms:
        print("ℹ️ No alarms to delete.")
        return

    print("\n🔍 Alarms for this instance:")
    for idx, alarm in enumerate(attached_alarms):
        print(f"[{idx}] {alarm['name']} — {alarm['metric']} ({alarm['state']})")

    choice = input("Enter alarm number to delete (or 'all' / Enter to cancel): ").strip()

    if choice == "":
        return
    elif choice.lower() == "all":
        names = [a['name'] for a in attached_alarms]
        cloudwatch.delete_alarms(AlarmNames=names)
        print("🗑️ Deleted all alarms for this instance.")
    elif choice.isdigit():
        index = int(choice)
        if index < len(attached_alarms):
            cloudwatch.delete_alarms(AlarmNames=[attached_alarms[index]['name']])
            print(f"🗑️ Deleted: {attached_alarms[index]['name']}")
        else:
            print("❌ Invalid index.")
    else:
        print("❌ Invalid input.")

def main():
    parser = argparse.ArgumentParser(description="EC2 Alarm Manager")
    parser.add_argument('--metric', default=DEFAULT_METRIC, help="Metric name (default: CPUUtilization)")
    parser.add_argument('--threshold', type=float, default=80.0, help="Trigger threshold (default: 80.0)")
    parser.add_argument('--period', type=int, default=300, help="Evaluation period in seconds (default: 300)")
    parser.add_argument('--evals', type=int, default=1, help="Number of periods to breach (default: 1)")
    parser.add_argument('--delete', action='store_true', help="Delete alarms instead of creating them")

    args = parser.parse_args()

    instances = list_running_instances_with_alarms()

    if not instances:
        print("No running EC2 instances found.")
        exit()

    display_instances(instances)

    choice = input("\nEnter instance number to manage: ").strip()

    if not choice.isdigit() or int(choice) >= len(instances):
        print("❌ Invalid selection.")
        exit()

    selected = instances[int(choice)]

    if args.delete:
        delete_alarms(selected['Alarms'])
    else:
        create_alarm(
            instance_id=selected['InstanceId'],
            instance_name=selected['Name'],
            metric=args.metric,
            threshold=args.threshold,
            period=args.period,
            evals=args.evals
        )

if __name__ == "__main__":
    main()
