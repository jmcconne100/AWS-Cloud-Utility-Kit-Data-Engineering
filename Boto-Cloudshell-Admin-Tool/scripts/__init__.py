from scripts import alarm, elastic_IP, idle_ec2, schedule, sec_groups, spot_instance_launcher, spot_price_analyzer, ssh_and_cw_agent, stray_EBS, tags

def run_script(script_name):
    print(f"running {script}.py")
    script_name.main()

def menu():
    while True:
        print("\nAWS SysAdmin Toolkit")
        print("1. Alarm")
        print("2. Elastic IPs")
        print("3. Idle EC2")
        print("4. Schedule")
        print("5. Security Groups")
        print("6. Spot Instance Launcher")
        print("7. Spot Price Analyzer")
        print("8. SSH and Cloudwatch Agent")
        print("9. Stray EBS")
        print("10. Tags")
        print("11. Exit")
        choice = input("Choose a task: ")

        if choice == '1':
            run_script("alarm")
        elif choice == '2':
            run_script("elastic_IP")
        elif choice == '3':
            run_script("idle_ec2")
        elif choice == '4':
            run_script("schedule")
        elif choice == '5':
            run_script("sec_groups")
        elif choice == '6':
            run_script("spot_instance_launcher")
        elif choice == '7':
            run_script("spot_price_analyzer")
        elif choice == '8':
            run_script("ssh_and_cw_agent")
        elif choice == '9':
            run_script("stray_EBS")
        elif choice == '10':
            run_script("tags")
        elif choice == '11':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    menu()
