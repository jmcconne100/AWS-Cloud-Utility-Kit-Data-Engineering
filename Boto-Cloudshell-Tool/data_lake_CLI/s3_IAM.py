import boto3
import json


iam = boto3.client('iam')

# Utility to create a role with trust and attach policies
def create_iam_role(role_name, trust_policy, policy_arns):
    try:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Role for {role_name} in Data Lake setup"
        )
        print(f"✅ Created role: {role_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️ Role already exists: {role_name}")

    for arn in policy_arns:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=arn)
        print(f"   🔗 Attached policy: {arn}")

# Prebuilt Trust Policies
trust_glue = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "glue.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

trust_lambda = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

trust_data_users = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"AWS": "arn:aws:iam::ACCOUNT_ID:root"},
        "Action": "sts:AssumeRole"
    }]
}

# Sample Policies
cloudwatch_logs_policy = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
s3_full_policy = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
s3_readwrite_policy = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
kms_policy = "arn:aws:iam::aws:policy/AWSKeyManagementServicePowerUser"
glue_policy = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
lambda_exec_policy = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

def main():
    # Create roles
    create_iam_role("DataLakeETLRole", trust_glue, [cloudwatch_logs_policy, kms_policy, glue_policy])
    create_iam_role("DataLakeLambdaRole", trust_lambda, [cloudwatch_logs_policy, kms_policy, lambda_exec_policy])
    create_iam_role("DataLakeUserGroupRole", trust_data_users, [s3_full_policy, kms_policy])

    # Allow user to create custom role
    custom_service = input("Enter AWS service name for custom role (e.g., ec2.amazonaws.com, athena.amazonaws.com): ").strip()
    custom_role_name = input("Enter a name for your custom role: ").strip()

    custom_trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": custom_service},
            "Action": "sts:AssumeRole"
        }]
    }

    # Suggest common policies for user to select
    print("\nChoose policies to attach (comma separated numbers):")
    policy_options = [
        ("1", "AmazonS3FullAccess", s3_full_policy),
        ("2", "CloudWatchLogsFullAccess", cloudwatch_logs_policy),
        ("3", "AWSKeyManagementServicePowerUser", kms_policy),
        ("4", "AWSLambdaBasicExecutionRole", lambda_exec_policy),
        ("5", "AWSGlueServiceRole", glue_policy)
    ]
    for code, label, _ in policy_options:
        print(f"  [{code}] {label}")

    choices = input("Enter choice(s): ").split(',')
    selected_policies = [arn for code, _, arn in policy_options if code.strip() in choices]

    create_iam_role(custom_role_name, custom_trust, selected_policies)

    print("\n✅ IAM roles setup complete.")


if __name__ == "__main__":
    main()
