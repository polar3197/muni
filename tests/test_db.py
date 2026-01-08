
from config import PostgreSQLConfig
from database.client import PostgreSQLClient
import asyncio

async def fetch_most_recent():
    config = PostgreSQLConfig()

    print(f"Connecting to: {config.host}:{config.port}/{config.name}")

    client = PostgreSQLClient(config, retry_count=2)

    result = await client.get_current_vehicles(10)
    print("Success!")
    for vehicle in result:
        print(f"time: {vehicle['timestamp']}, route: {vehicle['route_id']}")
        print()
        print()

async def fetch_table_as_parquet(year: int, week: int):
    table_name = f"vehicles_partition_{year}_w{week}"
    config = PostgreSQLConfig()
    client = PostgreSQLClient(config)
    success = await client.export_table_to_df(table_name)

async def fetch_oldest_partition_name():
    config = PostgreSQLConfig()
    client = PostgreSQLClient(config)
    table_name = await client.get_oldest_partition_name()
    print(table_name)

if __name__ == "__main__":
    # asyncio.run(fetch_most_recent())

    #asyncio.run(fetch_table_as_parquet(2025, 35))

    asyncio.run(fetch_oldest_partition_name())
