from config import PostgreSQLConfig
from database.client import PostgreSQLClient
import asyncio

async def fetch_and_store_rt_gtfs():
    db_config = PostgreSQLConfig()
    db_client = PostgreSQLClient(db_config)

    try:
        await db_client.create_new_vehicles_partition(weeks_in_advance=1)

        # handle case where no vehicles are fetched (don't insert into db)
    except Exception as e:
        print(f"Error creating new vehicles partition: {e}")


if __name__ == "__main__":
    asyncio.run(fetch_and_store_rt_gtfs())
