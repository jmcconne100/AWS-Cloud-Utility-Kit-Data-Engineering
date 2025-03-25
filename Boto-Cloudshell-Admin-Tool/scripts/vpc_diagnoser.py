import boto3

ec2 = boto3.client('ec2')

def get_vpcs():
    return ec2.describe_vpcs()['Vpcs']

def get_internet_gateways():
    igws = ec2.describe_internet_gateways()['InternetGateways']
    return {att['VpcId']: igw['InternetGatewayId']
            for igw in igws
            for att in igw.get('Attachments', [])
            if att['State'] == 'available'}

def get_route_tables():
    rtbs = ec2.describe_route_tables()['RouteTables']
    return rtbs

def get_subnets():
    return ec2.describe_subnets()['Subnets']

def is_public_subnet(rtb, igw_ids):
    for route in rtb['Routes']:
        if route.get('GatewayId') in igw_ids or route.get('GatewayId', '').startswith("igw-"):
            if route['DestinationCidrBlock'] == '0.0.0.0/0':
                return True
    return False

def is_private_subnet(rtb):
    for route in rtb['Routes']:
        if route.get('NatGatewayId') or route.get('InstanceId'):
            if route['DestinationCidrBlock'] == '0.0.0.0/0':
                return True
    return False

def main():
    print("🔍 Diagnosing VPC Networking Issues...\n")

    vpcs = get_vpcs()
    igw_map = get_internet_gateways()
    rtbs = get_route_tables()
    subnets = get_subnets()

    rtb_map = {}
    for rtb in rtbs:
        for assoc in rtb['Associations']:
            if 'SubnetId' in assoc:
                rtb_map[assoc['SubnetId']] = rtb

    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        print(f"\n🌐 VPC: {vpc_id}")
        print(f"   CIDR: {vpc['CidrBlock']}")
        if vpc_id in igw_map:
            print(f"   ✅ Internet Gateway attached: {igw_map[vpc_id]}")
        else:
            print("   ❌ No Internet Gateway attached")

        print("   📍 Subnets:")
        for subnet in [s for s in subnets if s['VpcId'] == vpc_id]:
            subnet_id = subnet['SubnetId']
            az = subnet['AvailabilityZone']
            cidr = subnet['CidrBlock']
            rtb = rtb_map.get(subnet_id)

            if not rtb:
                print(f"    - {subnet_id} [{az}] {cidr} — ❌ No Route Table associated")
                continue

            if is_public_subnet(rtb, igw_map.values()):
                status = "🌐 Public"
            elif is_private_subnet(rtb):
                status = "🔒 Private (via NAT)"
            else:
                status = "❌ No internet route"

            print(f"    - {subnet_id} [{az}] {cidr} — {status}")

if __name__ == "__main__":
    main()
