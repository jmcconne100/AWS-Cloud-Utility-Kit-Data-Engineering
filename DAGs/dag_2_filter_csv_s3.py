from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
from io import StringIO

BUCKET = 'your-bucket-name'
INPUT_KEY = 'input/users.csv'
OUTPUT_KEY = 'filtered/active_users.csv'

def filter_csv():
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=BUCKET, Key=INPUT_KEY)
    df = pd.read_csv(obj['Body'])

    # Filter condition
    filtered = df[df['status'] == 'active']

    # Upload result
    buffer = StringIO()
    filtered.to_csv(buffer, index=False)
    s3.put_object(Bucket=BUCKET, Key=OUTPUT_KEY, Body=buffer.getvalue())

with DAG(
    dag_id='filter_active_users',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['s3', 'etl']
) as dag:
    
    filter_task = PythonOperator(
        task_id='filter_csv',
        python_callable=filter_csv,
    )
