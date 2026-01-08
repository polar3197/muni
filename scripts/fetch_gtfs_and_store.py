from config import GTFSConfig, PostgreSQLConfig
from gtfs.fetcher import GTFSFetcher
from database.client import PostgreSQLClient
import asyncio

async def fetch_and_store_rt_gtfs():
    gtfs_config = GTFSConfig()
    gtfs_fetcher = GTFSFetcher(gtfs_config)
    
    db_config = PostgreSQLConfig()
    db_client = PostgreSQLClient(db_config)

    try:
        vehicles = gtfs_fetcher.fetch_live_vehicles()

        # handle case where no vehicles are fetched (don't insert into db)
        if not vehicles:
            print("No vehicles fetched")
            return
        print(f"Fetched {len(vehicles)} vehicles")
    except Exception as e:
        print(f"Error fetching vehicles: {e}")

    try:
        await db_client.insert_vehicles(vehicles)
        print("Successfully inserted the vehicles")
    except Exception as e:
        print(f"Error storing vehicles in db: {e}")
    
    return

if __name__ == "__main__":
    asyncio.run(fetch_and_store_rt_gtfs())


