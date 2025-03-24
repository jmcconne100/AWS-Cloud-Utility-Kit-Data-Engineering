import boto3
from collections import defaultdict

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

SENSITIVE_PORTS = [22, 3389, 80, 443, 3306]

PREDEFINED_RULES = [
    {"name": "SSH", "port": 22, "proto": "tcp", "desc": "Secure Shell"},
    {"name": "HTTP", "port": 80, "proto": "tcp", "desc": "Web traffic (unencrypted)"},
    {"name": "HTTPS", "port": 443, "proto": "tcp", "desc": "Web traffic (encrypted)"},
    {"name": "MySQL", "port": 3306, "proto": "tcp", "desc": "MySQL Database"},
    {"name": "PostgreSQL", "port": 5432, "proto": "tcp", "desc": "PostgreSQL Database"},
    {"name": "RDP", "port": 3389, "proto": "tcp", "desc": "Remote Desktop Protocol"},
    {"name": "Custom App", "port": 8080, "proto": "tcp", "desc": "Alternate HTTP port"},
    {"name": "ICMP (Ping)", "port": -1, "proto": "icmp", "desc": "Diagnostics (ping)"},
]

def format_rule(rule):
    proto = rule.get('IpProtocol', 'all')
    from_port = rule.get('FromPort', 'all')
    to_port = rule.get('ToPort', 'all')
    port_range = f"{from_port}-{to_port}" if from_port != to_port else f"{from_port}"
    rules_output = []

    for ip in rule.get('IpRanges', []):
        cidr = ip['CidrIp']
        warnings = []
        if cidr == '0.0.0.0/0':
            warnings.append("🌐 OPEN TO WORLD")
        if isinstance(from_port, int) and from_port in SENSITIVE_PORTS:
            warnings.append("⚠️ Sensitive Port")
        warn_str = " ".join(warnings)
        rules_output.append(f"      → {proto.upper()} {port_range} from {cidr} {warn_str}")
    return rules_output

def list_instances_by_sg():
    sg_to_instances = defaultdict(list)
    for instance in ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
        for sg in instance.security_groups:
            sg_to_instances[sg['GroupId']].append(instance)
    return sg_to_instances

def inspect_and_select_sg():
    print("\n🔐 Inspecting Security Groups by VPC...\n")
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    sg_to_instances = list_instances_by_sg()
    sg_index = []
    counter = 0

    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        print(f"📦 VPC: {vpc_id}")
        sgs = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['SecurityGroups']

        for sg in sgs:
            sg_id = sg['GroupId']
            sg_name = sg.get('GroupName', 'Unnamed')
            print(f"\n  [{counter}] 🔒 {sg_name} ({sg_id})")

            # Inbound rules
            ip_perms = sg.get('IpPermissions', [])
            print("    🔹 Inbound Rules:")
            if not ip_perms:
                print("      ⚠️ No inbound rules.")
            else:
                for rule in ip_perms:
                    for line in format_rule(rule):
                        print(line)

            # Outbound rules
            out_perms = sg.get('IpPermissionsEgress', [])
            print("    🔸 Outbound Rules:")
            if not out_perms:
                print("      ⚠️ No outbound rules.")
            else:
                for rule in out_perms:
                    for line in format_rule(rule):
                        print(line)

            # Attached instances
            attached = sg_to_instances.get(sg_id, [])
            if attached:
                print("    🖥️ Attached Instances:")
                for inst in attached:
                    name = next((t['Value'] for t in inst.tags or [] if t['Key'] == 'Name'), 'Unnamed')
                    print(f"      - {name} ({inst.id})")
            else:
                print("    🚫 No running instances attached.")

            sg_index.append(sg)
            counter += 1
        print("-" * 60)

    return sg_index

def edit_rules(sg, direction='inbound'):
    label = 'Inbound' if direction == 'inbound' else 'Outbound'
    group_id = sg['GroupId']
    method = ec2_client.authorize_security_group_ingress if direction == 'inbound' else ec2_client.authorize_security_group_egress

    print(f"\n🔧 Editing {label} Rules for {sg['GroupName']} ({group_id})")
    print("Choose an option:")
    print("  [1] Add predefined rule")
    print("  [2] Add custom rule")
    choice = input("Enter choice (or press Enter to cancel): ").strip()

    if choice == '1':
        print("\n📚 Predefined Rules:")
        for idx, rule in enumerate(PREDEFINED_RULES):
            port_label = "ALL" if rule['port'] == -1 else rule['port']
            print(f"  [{idx}] {rule['name']} ({port_label}/{rule['proto'].upper()}): {rule['desc']}")

        rsel = input("Select rule number to add: ").strip()
        if rsel.isdigit() and int(rsel) < len(PREDEFINED_RULES):
            selected = PREDEFINED_RULES[int(rsel)]
            from_port = to_port = selected['port']
            if selected['port'] == -1:
                from_port = to_port = -1  # ICMP or all
            method(GroupId=group_id, IpPermissions=[{
                'IpProtocol': selected['proto'],
                'FromPort': from_port,
                'ToPort': to_port,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }])
            print(f"✅ Rule added: {selected['name']} ({selected['port']}/{selected['proto']})")
        else:
            print("❌ Invalid selection.")

    elif choice == '2':
        proto = input("Protocol (e.g., tcp): ").strip()
        from_port = int(input("From port: ").strip())
        to_port = int(input("To port: ").strip())
        cidr = input("CIDR block (e.g., 0.0.0.0/0): ").strip()
        method(GroupId=group_id, IpPermissions=[{
            'IpProtocol': proto,
            'FromPort': from_port,
            'ToPort': to_port,
            'IpRanges': [{'CidrIp': cidr}]
        }])
        print("✅ Custom rule added.")
    else:
        print("ℹ️ Cancelled.")

def delete_rules(sg, direction='inbound'):
    label = 'Inbound' if direction == 'inbound' else 'Outbound'
    group_id = sg['GroupId']
    perm_key = 'IpPermissions' if direction == 'inbound' else 'IpPermissionsEgress'
    revoke = ec2_client.revoke_security_group_ingress if direction == 'inbound' else ec2_client.revoke_security_group_egress

    print(f"\n🧨 Deleting {label} rules for {sg['GroupName']} ({group_id})")
    permissions = sg.get(perm_key, [])
    if not permissions:
        print(f"❌ No {label.lower()} rules to delete.")
        return

    flat_rules = []
    for perm in permissions:
        proto = perm.get('IpProtocol', 'all')
        from_port = perm.get('FromPort', 'all')
        to_port = perm.get('ToPort', 'all')
        for ip in perm.get('IpRanges', []):
            flat_rules.append({
                'IpProtocol': proto,
                'FromPort': from_port,
                'ToPort': to_port,
                'CidrIp': ip['CidrIp']
            })

    for idx, rule in enumerate(flat_rules):
        print(f"[{idx}] {rule['IpProtocol'].upper()} {rule['FromPort']}-{rule['ToPort']} from {rule['CidrIp']}")

    sel = input("Enter rule number to delete (or Enter to cancel): ").strip()
    if not sel.isdigit() or int(sel) >= len(flat_rules):
        print("❌ Invalid selection or cancelled.")
        return

    to_delete = flat_rules[int(sel)]
    confirm = input(f"⚠️ Confirm delete rule {to_delete}? (y/N): ").strip().lower()
    if confirm == 'y':
        revoke(GroupId=group_id, IpPermissions=[{
            'IpProtocol': to_delete['IpProtocol'],
            'FromPort': to_delete['FromPort'],
            'ToPort': to_delete['ToPort'],
            'IpRanges': [{'CidrIp': to_delete['CidrIp']}]
        }])
        print("✅ Rule deleted.")
    else:
        print("ℹ️ Cancelled.")

def main():
    all_sgs = inspect_and_select_sg()
    choice = input("\n🎯 Enter SG number to edit rules (or press Enter to skip): ").strip()

    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(all_sgs):
            action = input("Choose action: [i]nbound, [o]utbound, [di] delete inbound, [do] delete outbound: ").strip().lower()
            if action == 'o':
                edit_rules(all_sgs[idx], direction='outbound')
            elif action == 'di':
                delete_rules(all_sgs[idx], direction='inbound')
            elif action == 'do':
                delete_rules(all_sgs[idx], direction='outbound')
            else:
                edit_rules(all_sgs[idx], direction='inbound')
        else:
            print("❌ Invalid SG number.")

if __name__ == "__main__":
    main()
