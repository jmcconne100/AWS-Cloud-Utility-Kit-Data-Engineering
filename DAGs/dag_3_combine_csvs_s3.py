from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
from io import StringIO

BUCKET = 'your-bucket-name'
KEY1 = 'input/part1.csv'
KEY2 = 'input/part2.csv'
OUTPUT_KEY = 'combined/full_data.csv'

def combine_csvs():
    s3 = boto3.client('s3')

    df1 = pd.read_csv(s3.get_object(Bucket=BUCKET, Key=KEY1)['Body'])
    df2 = pd.read_csv(s3.get_object(Bucket=BUCKET, Key=KEY2)['Body'])

    combined = pd.concat([df1, df2], ignore_index=True)

    buffer = StringIO()
    combined.to_csv(buffer, index=False)
    s3.put_object(Bucket=BUCKET, Key=OUTPUT_KEY, Body=buffer.getvalue())

with DAG(
    dag_id='combine_csvs_s3',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['s3', 'etl']
) as dag:
    
    combine_task = PythonOperator(
        task_id='combine_csvs',
        python_callable=combine_csvs,
    )
