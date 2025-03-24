import boto3
import time
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
resource = boto3.resource('ec2')
ssm = boto3.client('ssm')

def get_latest_amazon_linux_ami():
    try:
        param = '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
        return ssm.get_parameter(Name=param)['Parameter']['Value']
    except Exception as e:
        print("❌ Could not fetch AMI:", e)
        return None

def get_availability_zones():
    response = ec2.describe_availability_zones(Filters=[{"Name": "state", "Values": ["available"]}])
    return [az['ZoneName'] for az in response['AvailabilityZones']]

def get_subnet_in_az(az):
    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'availability-zone', 'Values': [az]}]
    )['Subnets']
    if subnets:
        return subnets[0]
    else:
        return None

def list_key_pairs():
    keys = ec2.describe_key_pairs()['KeyPairs']
    return [k['KeyName'] for k in keys]

def list_security_groups_for_vpc(vpc_id):
    groups = ec2.describe_security_groups(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )['SecurityGroups']
    return [(g['GroupId'], g.get('GroupName', 'Unnamed')) for g in groups]

def request_spot_instance(ami_id, instance_type, subnet_id, az, key_name, sg_id):
    try:
        print("\n📨 Requesting Spot Instance...")

        response = ec2.request_spot_instances(
            InstanceCount=1,
            LaunchSpecification={
                'ImageId': ami_id,
                'InstanceType': instance_type,
                'SubnetId': subnet_id,
                'Placement': {'AvailabilityZone': az},
                'KeyName': key_name,
                'SecurityGroupIds': [sg_id],
            }
        )

        request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
        print(f"⏳ Waiting for Spot Request {request_id} to be fulfilled...")

        time.sleep(3)  # Let the request settle

        try:
            req = ec2.describe_spot_instance_requests(
                SpotInstanceRequestIds=[request_id]
            )['SpotInstanceRequests'][0]
        except ClientError as e:
            print(f"❌ Spot request vanished or failed immediately: {e}")
            return None

        state = req['State']
        status = req['Status']['Code']

        if state == 'active' and 'InstanceId' in req:
            instance_id = req['InstanceId']
        elif 'capacity-not-available' in status:
            print("⚠️ Capacity not available in that AZ. Try another.")
            return None
        elif state in ['cancelled', 'failed', 'closed']:
            print(f"❌ Spot request failed: {status}")
            return None
        else:
            print(f"⏳ Spot request in state: {state} - waiting a bit longer...")
            for _ in range(10):
                time.sleep(3)
                req = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=[request_id])['SpotInstanceRequests'][0]
                if req['State'] == 'active' and 'InstanceId' in req:
                    instance_id = req['InstanceId']
                    break
            else:
                print("❌ Spot request never activated.")
                return None

        print(f"✅ Instance {instance_id} launched. Waiting for running state...")

        instance = resource.Instance(instance_id)
        instance.wait_until_running()
        instance.reload()
        print(f"🚀 Instance is running: {instance_id}")
        print(f"🌐 Public IP: {instance.public_ip_address}")
        return instance_id

    except ClientError as e:
        print("❌ Spot instance request failed:", e)
        return None

def main():
    instance_type = input("🖥️ Enter instance type (e.g. t3.micro): ").strip()
    if not instance_type:
        print("❌ Instance type required.")
        return

    ami_id = get_latest_amazon_linux_ami()
    if not ami_id:
        return

    azs = get_availability_zones()
    print("\n🌎 Available AZs:")
    for i, az in enumerate(azs):
        print(f"  [{i}] {az}")
    az_choice = input("Pick an AZ by number: ").strip()
    az = azs[int(az_choice)] if az_choice.isdigit() and int(az_choice) < len(azs) else None
    if not az:
        print("❌ Invalid AZ.")
        return

    subnet = get_subnet_in_az(az)
    if not subnet:
        print("❌ No subnet found in selected AZ.")
        return
    subnet_id = subnet['SubnetId']
    vpc_id = subnet['VpcId']

    keys = list_key_pairs()
    if not keys:
        print("❌ No key pairs available.")
        return
    print("\n🔐 Available Key Pairs:")
    for i, k in enumerate(keys):
        print(f"  [{i}] {k}")
    key_choice = input("Pick a key pair by number: ").strip()
    key_name = keys[int(key_choice)] if key_choice.isdigit() and int(key_choice) < len(keys) else None

    sgs = list_security_groups_for_vpc(vpc_id)
    if not sgs:
        print("❌ No security groups found in VPC.")
        return
    print("\n🧱 Available Security Groups (Valid for AZ):")
    for i, (gid, gname) in enumerate(sgs):
        print(f"  [{i}] {gname} ({gid})")
    sg_choice = input("Pick a security group by number: ").strip()
    sg_id = sgs[int(sg_choice)][0] if sg_choice.isdigit() and int(sg_choice) < len(sgs) else None

    if not all([key_name, sg_id]):
        print("❌ Key or security group selection invalid.")
        return

    request_spot_instance(ami_id, instance_type, subnet_id, az, key_name, sg_id)

if __name__ == "__main__":
    main()
