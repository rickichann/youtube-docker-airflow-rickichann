from airflow import DAG
from airflow.operators.python_operator import PythonOperator 
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd


def extract_data(ti):

    # Initialize the postgres hook
    postgres_hook = PostgresHook(postgres_conn_id='dbmaster')

    # Execute your SQL
    sql = "SELECT * FROM transaction_data"
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    # Create a pandas dataframe
    df = pd.DataFrame(results, columns=column_names)

    # push to next func
    ti.xcom_push(key='transaction_data', value=df.to_json())


def transform_data(ti):
    df_json = ti.xcom_pull(key='transaction_data', task_ids = 'extract_task')
    df = pd.read_json(df_json)

    df['totalPrice'] = df['Quantity'] * df['UnitPrice']
    dfg = df[['Country','StockCode','Description','Quantity','totalPrice']]
    dfg = dfg.groupby(by=['Country','StockCode','Description']).sum().reset_index()

    ti.xcom_push(key='transaction_groupby', value=dfg.to_json())


def load_data(ti):
    df_json = ti.xcom_pull(key='transaction_groupby', task_ids='transform_task')
    df = pd.read_json(df_json)
    df.columns = df.columns.str.lower()
    # Get the PostgreSQL connection using PostgresHook
    postgres_hook = PostgresHook(postgres_conn_id='dbwarehouse')
    conn = postgres_hook.get_conn()
    
    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transaction_groupby (
                country VARCHAR(100),
                stockcode VARCHAR(50),
                description TEXT,
                quantity INT,
                totalprice FLOAT
            );
        """)

        cur.execute("DELETE FROM transaction_groupby;")
        conn.commit()

        # Using SQLAlchemy engine from PostgresHook
        engine = postgres_hook.get_sqlalchemy_engine()
        df.to_sql('transaction_groupby', con=engine, if_exists='append', index=False)
    
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    finally:
        cur.close()
        conn.close()




default_args = {
    'owner' : 'rickichann',
    'start_date': datetime(2023,1,1),
    'retries': 1
}

dag = DAG(
    'summary_transaction',
    default_args = default_args,
    description = "A simple dag to extract data from postgres",
    schedule_interval='0 2 * * *',
    max_active_runs = 1,
    catchup = False
)


extract_task = PythonOperator( 
    task_id = 'extract_task',
    python_callable = extract_data,
    dag=dag

)

transform_task = PythonOperator( 
    task_id = 'transform_task',
    python_callable = transform_data,
    dag=dag

)

load_task = PythonOperator( 
    task_id = 'load_task',
    python_callable = load_data,
    dag=dag

)

extract_task >> transform_task >> load_task