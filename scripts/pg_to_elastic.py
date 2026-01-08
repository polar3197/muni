
from elasticsearch import Elasticsearch
from config import PostgreSQLConfig
from database.client import PostgreSQLClient
import asyncio
from elasticsearch.helpers import bulk


async def main():
    pg_config = PostgreSQLConfig()
    pg_client = PostgreSQLClient(pg_config)

    es = Elasticsearch(
        ["http://192.168.0.32:9200"],
        basic_auth=("elastic", "AbwG0fzG")
    )

    print("Fetching current vehicles from PostgreSQL...")
    vehicles = await pg_client.get_current_vehicles(number=-1)
    print(f"Found {len(vehicles)} vehicles")

    # transform to elastic docs
    docs = []
    for vehicle in vehicles:
        docs.append({
            "_index": "muni-vehicles",
            "_source": {
                "vehicle_id": vehicle.get("vehicle_id"),
                "route_id": vehicle.get("route_id"),
                "timestamp": vehicle.get("timestamp").isoformat() if vehicle.get("timestamp") else None,
                "location": {
                    "lat": vehicle.get("lat"),
                    "lon": vehicle.get("lon")
                } if vehicle.get("lat") and vehicle.get("lon") else None,
                "speed": vehicle.get("speed"),
                "heading": vehicle.get("heading"),
            }
        })
    
    # Bulk index to Elasticsearch
    print("Indexing to Elasticsearch...")
    success, failed = bulk(es, docs, raise_on_error=False)
    print(f"Indexed {success} documents, {len(failed)} failed")

if __name__ == "__main__":
    asyncio.run(main())