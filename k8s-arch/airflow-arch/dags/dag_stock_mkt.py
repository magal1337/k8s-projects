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
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor


DAG_ID='stock-mkt-analytics'                                                                                                                                                                                

default_args = {
'owner':'lucas.ferreira',
'start_date': '2021-11-11',
'email_on_failure': False,
'email_on_success': False
}

api_token = Variable.get("alpha_vantage_secret")
minio_id = Variable.get("minio_key")
minio_key = Variable.get("minio_secret_key")

def get_stock_mkt_data_and_send_to_s3(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&outputsize=full&apikey={api_token}&datatype=csv"
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
    client.put_object(
        'stock-market',
        f'lz/{symbol}-{today}.csv',
        data,
        length=content_length,
        content_type='text/csv'
    )
    return logging.info(f'Extract from {symbol} completed!!!')

    

with DAG(DAG_ID, default_args = default_args,tags=["API-REST","MINIO","PYSPARK"], schedule_interval="30 12 * * *") as dag:
    start_spark_job = SparkKubernetesOperator(
        task_id='start_spark_job',
        namespace='proc-layer',
        application_file='spark-stock-analytics.yaml',
        kubernetes_conn_id='digitalOcean',
        do_xcom_push=True)
    monitor_spark_app_status = SparkKubernetesSensor(
        task_id="monitor_spark_app_status",
        namespace="proc-layer",
        application_name="{{ task_instance.xcom_pull(task_ids='start_spark_job')['metadata']['name'] }}",
        kubernetes_conn_id="digitalOcean")
    for company in ['AAPL','MSFT','GOOGL']:
        task = PythonOperator(
            task_id = f'get_stock_mkt_data_and_send_to_s3_{company}',
            python_callable = get_stock_mkt_data_and_send_to_s3,
            op_kwargs = {'symbol': company},
            dag = dag
        )
        task >> start_spark_job >> monitor_spark_app_status    
