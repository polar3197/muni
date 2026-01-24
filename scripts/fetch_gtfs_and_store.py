from config import GTFSConfig, PostgreSQLConfig
from gtfs.fetcher import GTFSFetcher
from database.client import PostgreSQLClient
import asyncio
# import redis
import json

# rd = redis.Redis(host='localhost', port=6379, db=0)

async def fetch_and_store_rt_gtfs():
    gtfs_config = GTFSConfig()
    gtfs_fetcher = GTFSFetcher(gtfs_config)
    
    db_config = PostgreSQLConfig()
    db_client = PostgreSQLClient(db_config)

    vehicles = None
    try:
        vehicles = gtfs_fetcher.fetch_live_vehicles()

        # handle case where no vehicles are fetched (don't insert into db)
        if not vehicles:
            print("No vehicles fetched")
            return
        print(f"Fetched {len(vehicles)} vehicles")
    except Exception as e:
        print(f"Error fetching vehicles: {e}")

    # insert into DB
    try:
        await db_client.insert_vehicles(vehicles)
        print(f"{vehicles[0]['timestamp'].time()}: Successfully inserted {len(vehicles)} vehicles into database")
    except Exception as e:
        print(f"Error storing vehicles in db: {e}")

    # insert into Redis cache
    # try:
    #     # push the hot vehicles to redis cache
    #     success = rd.set("cv", json.dumps(vehicles_for_redis))
    #     print("Success of importing vehicles to redis: ", success)
    # except Exception as e:
    #     print(f"Error storing vehicles in Redis: {e}")


if __name__ == "__main__":
    asyncio.run(fetch_and_store_rt_gtfs())


