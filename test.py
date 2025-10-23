
from config import PostgreSQLConfig
from database.client import PostgreSQLClient
from dotenv import load_dotenv
import asyncio
import os

async def main():
    config = PostgreSQLConfig()

    print(f"Connecting to: {config.host}:{config.port}/{config.name}")

    client = PostgreSQLClient(
        host=config.host,
        database=config.name,
        user=config.user,
        password=config.password,
        port=config.port,
        retry_count=3
    )

    result = await client.ping()
    print(f"Ping successful: {result}")

if __name__ == "__main__":
    asyncio.run(main())
