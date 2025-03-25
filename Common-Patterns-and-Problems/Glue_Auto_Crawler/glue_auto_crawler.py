import boto3
import time

BUCKET = 'my-data-pipeline'
PREFIX = 'bronze-zone/'
DATABASE_NAME = 'auto_discovery'
CRAWLER_NAME = 'auto_discovery_crawler'

s3 = boto3.client('s3')
glue = boto3.client('glue')

def create_database_if_not_exists(db_name):
    try:
        glue.get_database(Name=db_name)
        print(f"✅ Database '{db_name}' already exists.")
    except glue.exceptions.EntityNotFoundException:
        glue.create_database(DatabaseInput={'Name': db_name})
        print(f"✅ Created Glue database: {db_name}")

def create_or_update_crawler(name, bucket, prefix, database):
    path = f"s3://{bucket}/{prefix}"
    try:
        glue.get_crawler(Name=name)
        print(f"🔁 Updating crawler: {name}")
        glue.update_crawler(
            Name=name,
            Role='AWSGlueServiceRoleDefault',
            Targets={'S3Targets': [{'Path': path}]},
            DatabaseName=database
        )
    except glue.exceptions.EntityNotFoundException:
        print(f"🆕 Creating crawler: {name}")
        glue.create_crawler(
            Name=name,
            Role='AWSGlueServiceRoleDefault',
            Targets={'S3Targets': [{'Path': path}]},
            DatabaseName=database,
            TablePrefix='auto_',
        )

def run_and_wait_for_crawler(name):
    glue.start_crawler(Name=name)
    print(f"🚀 Running crawler: {name}")
    while True:
        status = glue.get_crawler(Name=name)['Crawler']['State']
        if status == 'READY':
            print(f"✅ Crawler '{name}' finished.")
            break
        print(f"⌛ Waiting... Current state: {status}")
        time.sleep(5)

def main():
    create_database_if_not_exists(DATABASE_NAME)
    create_or_update_crawler(CRAWLER_NAME, BUCKET, PREFIX, DATABASE_NAME)
    run_and_wait_for_crawler(CRAWLER_NAME)

if __name__ == "__main__":
    main()
