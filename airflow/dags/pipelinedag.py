from airflow import DAG
from airflow.decorators import dag, task, task_group
from airflow.utils.dates import days_ago
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.airbyte.sensors.airbyte import AirbyteJobSensor
from datetime import datetime, timedelta
from include.app_utils import *
from include.transform_helper import *
import logging, os
from airflow.operators.python_operator import PythonOperator

from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig, DbtTaskGroup
from cosmos.profiles import SnowflakeUserPasswordProfileMapping

# Snowflake profile config
profile_config = ProfileConfig(
    profile_name='default',
    target_name='dev',
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id='snowflake_default',
        profile_args={'database': 'AIRBYTE_DATABASE', 'schema': 'dbt_schema'},
    )
)

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG
@dag(
    'ram_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False
)

# Main DAG func
def ram_pipeline():
    
    """
    Bronze tier task group uses the airbyte an airbyte connection
    to extract the API in streams using pagination and putting the
    objects inside the Datalake.
    """
    
    # Bronze Tier task_group
    @task_group(group_id='bronze_tier')

    def bronze_tier():
        
        # Async Airbyte trigger task
        async_airbyte_connection = AirbyteTriggerSyncOperator(
            task_id='api_extraction',
            airbyte_conn_id='airbyte-conn-api',
            connection_id='84993854-cc63-462d-9e6c-f25001e39435',
            asynchronous=True,
        )
        # Airbyte Sensor
        airbyte_sensor = AirbyteJobSensor(
            task_id='store_to_datalake',
            airbyte_conn_id='airbyte-conn-api',
            airbyte_job_id=async_airbyte_connection.output
        )
        
        # Function to convert JSON files to CSV and some var
        bucket_name = 'datalake'
        bronze_prefixes = ['bronze/bronze_Characters', 'bronze/bronze_Episodes', 'bronze/bronze_Locations']
        silver_prefixes = ['silver/silver_Characters', 'silver/silver_Episodes', 'silver/silver_Locations']
        
        # Function to convert JSONL files to CSV and some var
        def convert_and_upload_files(bronze_prefix, silver_prefix):
            try:
                jsonl_files = list_jsonl_files(bucket_name, bronze_prefix)
                if not jsonl_files:
                    logging.warning(f"No JSONL files found in {bronze_prefix}")
                    return
                for jsonl_file in jsonl_files:
                    logging.info(f"Processing file: {jsonl_file}")
                    json_lines = get_jsonl(bucket_name, jsonl_file)
                    
                    # Convert JSONL to CSV in-memory
                    csv_buffer = convert_jsonl_to_csv(json_lines)
                    
                    # Define the CSV file path in the S3 bucket
                    csv_file_path = jsonl_file.replace('bronze', 'silver').replace('.jsonl', '.csv')
                    
                    # Delete the CSV file to the S3 bucket
                    delete_csv_files(bucket_name, silver_prefix)  
                    
                    # Upload the CSV file to the S3 bucket
                    upload_csv(bucket_name, csv_file_path, pd.read_csv(io.StringIO(csv_buffer.getvalue())))
                    
                    logging.info(f"Uploaded CSV file to: {csv_file_path}")
            except Exception as e:
                logging.error(f"Error processing files in {bronze_prefix}: {e}")
                raise

                    
        convert_characters = PythonOperator(
            task_id='convert_characters',
            python_callable=convert_and_upload_files,
            op_kwargs={'bronze_prefix': 'bronze/bronze_Characters', 'silver_prefix': 'silver/silver_Characters'},
        )

        convert_episodes = PythonOperator(
            task_id='convert_episodes',
            python_callable=convert_and_upload_files,
            op_kwargs={'bronze_prefix': 'bronze/bronze_Episodes', 'silver_prefix': 'silver/silver_Episodes'},
        )

        convert_locations = PythonOperator(
            task_id='convert_locations',
            python_callable=convert_and_upload_files,
            op_kwargs={'bronze_prefix': 'bronze/bronze_Locations', 'silver_prefix': 'silver/silver_Locations'},
        )        
        
        # task order
        async_airbyte_connection >> airbyte_sensor >> [convert_characters, convert_episodes, convert_locations]
    
    
    """
    Silver tier task group uses the transform_helper packages
    to transform each s3 path to get ready for the Gold tier
    """
    
    # Silver Tier task_group
    @task_group(group_id='silver_tier')
    
    def silver_tier():
        # Bucket name
        bucket_name = 'datalake'
        
        def process_and_upload_files(silver_prefix, gold_prefix):
            try:
                csv_files = list_csv_files(bucket_name, silver_prefix)
                if not csv_files:
                    logging.warning(f"No CSV files found in {silver_prefix}")
                    return
                
                for csv_file in csv_files:
                    logging.info(f"Processing file {csv_file}")
                    df = get_csv(bucket_name, csv_file)
                    
                    # Transform based on prefix
                    if 'Characters' in silver_prefix:
                        silver_transform = silver_characters
                    elif 'Episodes' in silver_prefix:
                        silver_transform = silver_episodes
                    elif 'Locations' in silver_prefix:
                        silver_transform = silver_locations
                    else:
                        logging.error(f"Uknown prefix: {silver_prefix}")
                        return
                    
                    df_silver = silver_transform(df)
                    gold_file_path = csv_file.replace('silver', 'gold')
                    delete_csv_files(bucket_name, gold_prefix)
                    upload_csv(bucket_name, gold_file_path, df_silver)
                    logging.info(f"Uploaded Gold CSV file to: {gold_file_path}")
                
            except Exception as e:
                logging.error(f"Error processing files in {silver_prefix}: {e}")
                raise
        
        process_characters = PythonOperator(
            task_id='process_characters',
            python_callable=process_and_upload_files,
            op_kwargs={
                'silver_prefix': 'silver/silver_Characters', 
                'gold_prefix': 'gold/gold_Characters',
            },
        )

        process_episodes = PythonOperator(
            task_id='process_episodes',
            python_callable=process_and_upload_files,
            op_kwargs={
                'silver_prefix': 'silver/silver_Episodes', 
                'gold_prefix': 'gold/gold_Episodes',
            },
        )

        process_locations = PythonOperator(
            task_id='process_locations',
            python_callable=process_and_upload_files,
            op_kwargs={
                'silver_prefix': 'silver/silver_Locations', 
                'gold_prefix': 'gold/gold_Locations',
            },
        )        
        
        # task order
        [process_characters, process_episodes, process_locations] 
               
    # Gold Tier task_group
    @task_group(group_id="gold_tier")
    
    def gold_tier():
                # Async Airbyte trigger task
        async_airbyte_connection = AirbyteTriggerSyncOperator(
            task_id='get_schema',
            airbyte_conn_id='airbyte-conn-api',
            connection_id='ed8ad6bc-6bfb-4912-9296-6755ec6c241b',
            asynchronous=True,
        )
        # Airbyte Sensor
        airbyte_sensor = AirbyteJobSensor(
            task_id='store_to_warehouse',
            airbyte_conn_id='airbyte-conn-api',
            airbyte_job_id=async_airbyte_connection.output
        )
    
        async_airbyte_connection >> airbyte_sensor
        
    # DBT transformations
    @task_group(group_id="dbt_transformations")
    
    def dbt_snowflake_dag():
        transform_data=DbtTaskGroup(
            group_id="transform_data",
            project_config=ProjectConfig('/usr/local/airflow/dags/dbt/dbt_ram',),
            operator_args={'install_deps': True},
            profile_config=profile_config,
            execution_config=ExecutionConfig(dbt_executable_path=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt"),
        )
        
        transform_data
    
    # Medallion Tiers     
    bronze_tier() >> silver_tier() >> gold_tier() >> dbt_snowflake_dag()

# Call main DAG   
ram_pipeline()
