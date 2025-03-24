import boto3
import argparse
import subprocess
import os
import tempfile
import paramiko

# Clients for EC2 and Instance Connect
ec2 = boto3.client('ec2')
ic = boto3.client('ec2-instance-connect')

def get_instances(state='running'):
    filters = [{'Name': 'instance-state-name', 'Values': [state]}]
    response = ec2.describe_instances(Filters=filters)
    instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            public_ip = instance.get('PublicIpAddress', '—')
            az = instance['Placement']['AvailabilityZone']
            key_name = instance.get('KeyName', '—')

            instances.append({
                'Name': name,
                'InstanceId': instance_id,
                'PublicIp': public_ip,
                'AZ': az,
                'KeyName': key_name
            })
    return instances

def display_instances(instances):
    print("\n📋 EC2 Instances:")
    for i, inst in enumerate(instances):
        print(f"[{i}] {inst['Name']} ({inst['InstanceId']}) — IP: {inst['PublicIp']} — 🔑 Key: {inst['KeyName']}")

def instance_connect_send_key(instance, os_user='ec2-user'):
    """
    Generates a temporary SSH key, sends the public key to the instance using EC2 Instance Connect,
    and returns the path to the temporary private key.
    """
    instance_id = instance['InstanceId']
    az = instance['AZ']
    public_ip = instance['PublicIp']
    
    if public_ip == '—':
        print("❌ Instance has no public IP — cannot use Instance Connect.")
        return None

    # Generate a temporary key using Paramiko
    key = paramiko.RSAKey.generate(2048)
    private_key_file = tempfile.NamedTemporaryFile(delete=False)
    key.write_private_key_file(private_key_file.name)
    public_key = f"{key.get_name()} {key.get_base64()}"

    try:
        response = ic.send_ssh_public_key(
            InstanceId=instance_id,
            InstanceOSUser=os_user,
            SSHPublicKey=public_key,
            AvailabilityZone=az
        )
        if not response.get('Success'):
            print("❌ Failed to push SSH key via Instance Connect.")
            return None
    except Exception as e:
        print(f"❌ Error sending public key: {e}")
        return None

    return private_key_file.name

def instance_connect_ssh(instance):
    """
    Interactive SSH using Instance Connect (launches an SSH session in a subprocess).
    """
    os_user = 'ec2-user'  # Adjust this if your instance uses a different default user
    key_path = instance_connect_send_key(instance, os_user)
    if not key_path:
        return

    public_ip = instance['PublicIp']
    print(f"🚀 Connecting to {public_ip} via Instance Connect as {os_user}...")
    subprocess.run(["chmod", "400", key_path])
    subprocess.run(["ssh", "-i", key_path, f"{os_user}@{public_ip}"])

def install_agents(instance):
    """
    Connects to the selected instance using Instance Connect (via a temporary key)
    and runs commands to install and start the CloudWatch Agent (SSM Agent omitted).
    """
    os_user = 'ec2-user'  # Change if needed (e.g. 'ubuntu' for Ubuntu)
    key_path = instance_connect_send_key(instance, os_user)
    if not key_path:
        return

    public_ip = instance['PublicIp']
    if public_ip == '—':
        print("❌ Instance has no public IP — cannot connect.")
        return

    print(f"🚀 Connecting to {public_ip} via Instance Connect to install CloudWatch Agent...")

    # Set up Paramiko SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        ssh.connect(public_ip, username=os_user, pkey=key, look_for_keys=False)
    except Exception as e:
        print(f"❌ SSH connection failed: {e}")
        return

    commands = [
        "sudo yum install -y amazon-cloudwatch-agent",
        "sudo systemctl enable amazon-cloudwatch-agent",
        "sudo systemctl start amazon-cloudwatch-agent"
    ]

    for cmd in commands:
        print(f"🔧 Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(f"OUTPUT:\n{out}")
        if err:
            print(f"ERROR:\n{err}")

    ssh.close()
    os.remove(key_path)

def main():
    parser = argparse.ArgumentParser(description="EC2 Instance Connect Tool with Agent Installer")
    parser.add_argument('--state', help="Filter instances by state (default: running)", default='running')
    parser.add_argument('--ssh', action='store_true', help="Connect interactively via Instance Connect")
    parser.add_argument('--install-agents', action='store_true',
                        help="Run remote commands to install CloudWatch and SSM agents (non-interactive)")

    args = parser.parse_args()
    instances = get_instances(args.state)

    if not instances:
        print("No matching instances found.")
        exit()

    display_instances(instances)

    choice = input("\nEnter instance number to manage: ").strip()
    if not choice.isdigit():
        print("❌ Please enter a valid number.")
        exit()

    index = int(choice)
    if index < 0 or index >= len(instances):
        print("❌ Invalid index.")
        exit()

    selected = instances[index]

    # If the --install-agents flag is set, run the installation commands.
    if args.install_agents:
        install_agents(selected)
    # Otherwise, if --ssh flag is set, open an interactive SSH session.
    elif args.ssh:
        instance_connect_ssh(selected)
    else:
        print(f"ℹ️ You selected: {selected['Name']} ({selected['InstanceId']})")
        print("Use --ssh to connect interactively or --install-agents to install agents remotely.")

if __name__ == "__main__":
    main()
