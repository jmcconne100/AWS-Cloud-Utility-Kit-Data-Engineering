from scripts import (
    alarm,
    elastic_IP,
    idle_ec2,
    schedule,
    sec_groups,
    spot_instance_launcher,
    spot_price_analyzer,
    ssh_and_cw_agent,
    stray_EBS,
    tags,
    vpc_diagnoser,
)

def menu():
    options = {
        "1": ("Setup CloudWatch Alarm", alarm.main),
        "2": ("Allocate or Release Elastic IP", elastic_IP.main),
        "3": ("List or Terminate Idle EC2 Instances", idle_ec2.main),
        "4": ("Manage Schedules (Start/Stop)", schedule.main),
        "5": ("Audit Security Groups", sec_groups.main),
        "6": ("Launch Spot Instance", spot_instance_launcher.main),
        "7": ("Analyze Spot Price History", spot_price_analyzer.main),
        "8": ("Install SSH + CloudWatch Agent", ssh_and_cw_agent.main),
        "9": ("Find and Delete Stray EBS Volumes", stray_EBS.main),
        "10": ("Tag Resources Automatically", tags.main),
        "11": ("Diagnose VPC Networking", vpc_diagnoser.main),
        "0": ("Exit", None),
    }

    while True:
        print("\n=== AWS SysAdmin Toolkit ===")
        for key, (desc, _) in options.items():
            print(f"{key}. {desc}")
        choice = input("Choose a task: ")

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in options:
            try:
                options[choice][1]()  # Call the corresponding main function
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❗ Invalid choice, please try again.")

if __name__ == "__main__":
    menu()
