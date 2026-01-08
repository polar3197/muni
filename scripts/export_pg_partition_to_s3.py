from config import PostgreSQLConfig, S3Config, AWSConfig
from database.client import PostgreSQLClient
import asyncio
import os
import io
import re
import boto3
from boto3.s3.transfer import TransferConfig
import time
import threading


db_config = PostgreSQLConfig()
db_client = PostgreSQLClient(db_config)

s3_config = S3Config()
aws_config = AWSConfig()

async def export_oldest_partition():
    """
    """

    # attempt to fetch partition dataframe from PostgreSQL
    try:
        # fetch oldest vehicle partition in database
        table_name = await db_client.get_oldest_partition_name()
        print(f"Exporting partition: {table_name}")

        # extract week and year from name
        match = re.search(r'(\d{4})_w(\d{2})', table_name)
        if not match:
            print(f"Failed to extract date info from table name: {table_name}")
            return
        
        year = match.group(1)
        week = match.group(2)

        # extract it into DataFrame
        temp_file = f"{table_name}.parquet"

        print(f"writing to {temp_file}")
        oldest_partition_df = await db_client.export_table_to_file(table_name, temp_file)
        
        print("Finished loading table to parquet file")
    except Exception as e:
        print(f"Error creating new vehicles partition: {e}")
        return

    try:
        s3_key = f"vehicle_records/{year}/{week}.parquet"
        print(f"\nUploading to s3://{s3_config.bucket_name}/{s3_key}")
        
        s3_client = boto3.client('s3',
            aws_access_key_id=aws_config.access_key_id,
            aws_secret_access_key=aws_config.secret_access_key,
            region_name=s3_config.region
        )

        with open(temp_file, 'rb') as f:
            s3_client.upload_fileobj(f, s3_config.bucket_name, s3_key)
        
        print(f"Successfully backed up {table_name}")

        # Then delete temp file and partition from database
        if os.path.exists(temp_file):
            os.remove(temp_file)
        await db_client.drop_partition(table_name)
        
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return


if __name__ == "__main__":
    asyncio.run(export_oldest_partition())
