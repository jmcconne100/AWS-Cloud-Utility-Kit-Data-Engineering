from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
from io import StringIO

BUCKET = 'your-bucket-name'
INPUT_KEY = 'input/sample.csv'
OUTPUT_KEY = 'output/sample_with_flag.csv'

def transform_csv():
    s3 = boto3.client('s3')
    
    # Download CSV
    obj = s3.get_object(Bucket=BUCKET, Key=INPUT_KEY)
    df = pd.read_csv(obj['Body'])

    # Simple transformation
    df['processed_flag'] = True

    # Upload modified CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=BUCKET, Key=OUTPUT_KEY, Body=csv_buffer.getvalue())

with DAG(
    dag_id='basic_etl_s3',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['s3', 'etl']
) as dag:
    
    process_csv = PythonOperator(
        task_id='process_csv',
        python_callable=transform_csv,
    )
