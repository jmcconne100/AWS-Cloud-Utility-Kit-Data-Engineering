import boto3
from datetime import datetime, timedelta
from collections import defaultdict

ec2 = boto3.client('ec2')
pricing = boto3.client('pricing', region_name='us-east-1')  # Pricing API only lives here

PRICE_DURATION_DAYS = 7

REGION_NAME_MAP = {
    "us-east-1": "US East (N. Virginia)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "eu-west-1": "EU (Ireland)",
    "eu-central-1": "EU (Frankfurt)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
}

def get_region():
    return ec2.meta.region_name

def get_on_demand_price(instance_type, region):
    try:
        location = REGION_NAME_MAP.get(region)
        if not location:
            print("⚠️ Region mapping not found.")
            return None

        response = pricing.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}
            ],
            MaxResults=1
        )

        if not response['PriceList']:
            print("⚠️ No pricing info found.")
            return None

        price_item = eval(response['PriceList'][0])
        on_demand_terms = list(price_item['terms']['OnDemand'].values())[0]
        price_dimensions = list(on_demand_terms['priceDimensions'].values())[0]
        return float(price_dimensions['pricePerUnit']['USD'])

    except Exception as e:
        print(f"❌ On-demand price fetch failed: {e}")
        return None

def get_spot_price_stats(instance_type):
    now = datetime.utcnow()
    past = now - timedelta(days=PRICE_DURATION_DAYS)

    response = ec2.describe_spot_price_history(
        InstanceTypes=[instance_type],
        ProductDescriptions=['Linux/UNIX'],
        StartTime=past,
        EndTime=now,
        MaxResults=1000
    )

    stats = defaultdict(list)
    for entry in response['SpotPriceHistory']:
        az = entry['AvailabilityZone']
        price = float(entry['SpotPrice'])
        stats[az].append(price)

    return stats

def display_spot_price_summary(instance_type, stats, on_demand_price):
    print(f"\n📊 Spot Price Summary for {instance_type} (last {PRICE_DURATION_DAYS} days):\n")

    for az, prices in stats.items():
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        savings_pct = ((on_demand_price - avg_price) / on_demand_price) * 100 if on_demand_price else None

        print(f"🗺️ {az}")
        print(f"   ⬇️ Min: ${min_price:.4f}")
        print(f"   ⬆️ Max: ${max_price:.4f}")
        print(f"   📉 Avg: ${avg_price:.4f}", end='')

        if savings_pct is not None:
            print(f" — 💸 Saves ~{savings_pct:.1f}% vs On-Demand")
        else:
            print()

def main():
    instance_type = input("🔍 Enter EC2 instance type (e.g., t3.micro): ").strip()
    if not instance_type:
        print("❌ Instance type is required.")
        return

    region = get_region()
    on_demand_price = get_on_demand_price(instance_type, region)

    if on_demand_price:
        print(f"\n💵 On-Demand Price in {region}: ${on_demand_price:.4f}/hr")

    stats = get_spot_price_stats(instance_type)
    if stats:
        display_spot_price_summary(instance_type, stats, on_demand_price)
    else:
        print("❌ No spot price data found.")

if __name__ == "__main__":
    main()
