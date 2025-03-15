🛠 Step 1: Create an AWS Key Pair
Generate the key pair in AWS:
1. Go to AWS Management Console → EC2 → Key Pairs.
2. Click Create key pair.
3. Name it CloudFormationKeyPair.
4. Select .pem format.
5. Click Create Key Pair (it will automatically download CloudFormationKeyPair.pem).
6. Move the .pem file to a safe location on your machine, e.g.:

    "C:\Users\YourUsername\KeyPairs\CloudFormationKeyPair.pem"

🔧 Step 2: Convert .pem to .ppk for PuTTY
1. Open PuTTYgen (installed with PuTTY).
2. Click Load and select your .pem file.
3. Click Save private key (ignore passphrase warning).
4. Save it as CloudFormationKeyPair.ppk in the same directory.
   
📜 Step 3: Create & Deploy the CloudFormation Template
1. Open AWS Management Console → CloudFormation.
2. Click Create Stack → With new resources (standard).
3. Upload the CloudFormation YAML file (with VPC, Public/Private Subnets, NACL, Security Groups, EC2 instances).
4. Click Next and provide:
5. Stack Name (e.g., MyVPCStack).
6. Leave default values for other options.
7. Click Create Stack and wait for deployment.
   
📤 Step 4: Copy the .pem File to the Public EC2 Instance
1. Open PowerShell on your local machine.
2. Use pscp (PuTTY SCP) to transfer the .pem file to the public instance:

    "pscp -i C:\Users\YourUsername\KeyPairs\CloudFormationKeyPair.ppk C:\Users\YourUsername\KeyPairs\CloudFormationKeyPair.pem ec2-user@<PUBLIC_IP>:/home/ec2-user/"

3. Replace <PUBLIC_IP> with the actual public IP of your public instance.
   
🔐 Step 5: SSH into the Public Instance & Secure the Key
1. Open PuTTY and connect to the public EC2 instance:

    "Host Name: ec2-user@<PUBLIC_IP>"

2. Auth (SSH): Browse for CloudFormationKeyPair.ppk
3. Once inside, protect the .pem file:

    "chmod 400 /home/ec2-user/CloudFormationKeyPair.pem"

🔑 Step 6: SSH into the Private Instance
1. From inside the public EC2 instance, SSH into the private EC2 instance:

    "ssh -i /home/ec2-user/CloudFormationKeyPair.pem ec2-user@<PRIVATE_IP>"

2. Replace <PRIVATE_IP> with the private IP of your private EC2 instance.
3. Now, you're inside your private instance! 🎉
