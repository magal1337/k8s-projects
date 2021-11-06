from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def print_hello():
    return 'Hello world from first Airflow DAG!'
default_args = {
'owner':'ferreira.lucas',
'start_date': '2021-11-05',
'email': ['lucas.m.e.ferreira@gmail.com'],
'email_on_failure': False,
'email_on_success': False
}

dag = DAG('hello_world', description='Hello World DAG',schedule_interval='0 12 * * *', default_args=default_args, catchup=False)

hello_operator = PythonOperator(task_id='hello_task', python_callable=print_hello, dag=dag)

hello_operator
