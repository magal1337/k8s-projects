import requests
import json
from minio import Minio
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import io
import requests
import logging
from airflow.models import Variable


DAG_ID='stock-mkt-analytics'                                                                                                                                                                                

default_args = {
'owner':'lucas.ferreira',
'start_date': '2021-11-11',
'email_on_failure': False,
'email_on_success': False,
'tags': ['STOCK','API-REST'],
}

api_token = Variable.get("alpha_vantage_secret")
minio_id = Variable.get("minio_key")
minio_key = Variable.get("minio_secret_key")

def get_stock_mkt_data_and_send_to_s3(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&outputsize=full&apikey={api_token}"
    response = requests.get(url, stream=True)
    data = io.BytesIO(response.content)
    content_length = data.getbuffer().nbytes
    client = Minio(
        "minio.storage-layer.svc.cluster.local:9000",
        access_key=f"{minio_id}",
        secret_key=f"{minio_key}",
        secure=False
    )
    
    today = datetime.today().strftime('%Y-%m-%d')
    return client.put_object(
        'stock-market',
        f'lz/{symbol}-{today}.json',
        data,
        length=content_length,
        content_type='application/json'
    )

    

with DAG(DAG_ID, default_args = default_args, schedule_interval="30 12 * * *") as dag:
    for company in ['AAPL','MSFT','GOOGL']:
        task = PythonOperator(
            task_id = f'get_stock_mkt_data_and_send_to_s3_{company}',
            python_callable = get_stock_mkt_data_and_send_to_s3,
            op_kwargs = {'symbol': company},
            dag = dag
        )