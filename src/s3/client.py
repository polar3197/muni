import asyncio
import pandas as pd
import boto3

class S3Client():
    def __init__(config):
        self.config = config

    

    def insert_to_bucket(self, df: pd.Dataframe):
        df.to_parquet(f"{table_name}.parquet")
        print("Successfully converted to parquet!")
    
