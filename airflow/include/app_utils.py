from minio import Minio
import pandas as pd
from pandas import json_normalize
import io, json, logging, os, csv

# MinIO creds
host = 'host.docker.internal:9000'
ACCESS_KEY = 'aiQyeVOd1Ji3tsPJfEcR'
SECRET_KEY = 'IDFNxvUHkIuss5D2Hzt6rjPovCl1kJ3XK2Jqkcb5'

# MinIO connection
client = Minio(
    host,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False
)

# Get JSONL files from bucket
def get_jsonl(bucket_name, object_name):
    response = client.get_object(bucket_name, object_name)
    json_lines = response.data.decode('utf-8').split('\n')
    return [line for line in json_lines if line.strip()]

# List JSONL files in path
def list_jsonl_files(bucket_name, prefix):
    objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects if obj.object_name.endswith('.jsonl')]

# Convert JSONL to CSV using in-memory file buffer
def convert_jsonl_to_csv(json_lines):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write the header (assuming the first object in `results` has all possible keys)
    first_line = json.loads(json_lines[0])
    first_results = first_line['_airbyte_data']['results']
    if first_results:
        headers = list(first_results[0].keys())
        writer.writerow(headers)
    
        # Write the first line
        for result in first_results:
            writer.writerow([result.get(header, '') for header in headers])
    
    # Write the remaining lines
    for line in json_lines[1:]:
        data = json.loads(line)
        results = data['_airbyte_data']['results']
        for result in results:
            writer.writerow([result.get(header, '') for header in headers])
    
    output.seek(0)
    return output

# Upload to silver path as csv
def upload_csv(bucket_name, object_name, data_frame):
    csv_buffer = io.StringIO()
    data_frame.to_csv(csv_buffer, index=False)
    client.put_object(
        bucket_name,
        object_name,
        data=io.BytesIO(csv_buffer.getvalue().encode('utf-8')),
        length=len(csv_buffer.getvalue().encode('utf-8')),
        content_type='application/csv'
    )

# List CSV files in path
def list_csv_files(bucket_name, prefix):
    objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects if obj.object_name.endswith('.csv')]

# Delete CSV files
def delete_csv_files(bucket_name, prefix):
    csv_files = list_csv_files(bucket_name, prefix)
    for file in csv_files:
        client.remove_object(bucket_name, file)
        print(f"Deleted file: {file}")

# Get CSV files from bucket
def get_csv(bucket_name, object_name):
    response = client.get_object(bucket_name, object_name)
    return pd.read_csv(io.BytesIO(response.data))
