import requests
import json
import boto3  
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

DAG_ID='stock-mkt-analytics'                                                                                                                                                                                

default_args = {
'owner':'lucas.ferreira',
'start_date': '2021-11-11',
'email_on_failure': False,
'email_on_success': False,
'tags': ['STOCK','API-REST'],
}

def get_stock_mkt_data_and_send_to_s3(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&outputsize=full&apikey={{var.alpha_vantage_secret}}"
    response = requests.get(url)
    data = response.json()
    s3 = boto3.resource('s3',aws_access_key_id='{{var.minio_key}}', aws_secret_access_key='{{var.minio_secret_key}}')
    today = datetime.today().strftime('%Y-%m-%d')
    s3object = s3.Object('stock-market', f'lz/{symbol}-{today}.json')

    return s3object.put(
        Body=(bytes(json.dumps(data).encode('UTF-8')))
)

with DAG(DAG_ID, default_args = default_args, schedule_interval="30 12 * * *") as dag:
    for company in ['AAPL','MSFT','GOOGL']:
        task = PythonOperator(
            task_id = f'get_stock_mkt_data_and_send_to_s3_{company}',
            python_callable = get_stock_mkt_data_and_send_to_s3,
            op_kwargs = {'symbol': company},
            dag = dag
        )