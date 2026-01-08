import pandas as pd
import boto3
import os

s3 = boto3.client('s3',
    aws_access_key_id='nope',
    aws_secret_access_key='nope',
    region_name='us-west-1'
)

temp_file = '/tmp/verify.parquet'

try:
    # Download file first
    print("Downloading from S3...")
    s3.download_file(
        'charlie-muni-pg-backup',
        'vehicle_records/2025/35.parquet',
        temp_file
    )

    # Read local file
    print("Reading parquet file...")
    df_s3 = pd.read_parquet(temp_file)

    print(f"Rows in S3: {len(df_s3)}")
    print(f"Expected: ~1,788,200 rows")

    # Quick sanity check
    print("\nFirst few rows:")
    print(df_s3.head())
    print("\nDataFrame info:")
    print(df_s3.info())

finally:
    # Clean up temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"\nCleaned up {temp_file}")
