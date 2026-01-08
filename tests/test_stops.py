
from database.client import PostgreSQLClient
from config import PostgreSQLConfig
import asyncio

if __name__ == "__main__":
    # route_id = input("enter route_id: ")
    pgconf = PostgreSQLConfig()
    pgcli = PostgreSQLClient(pgconf)
    routes = asyncio.run(pgcli.get_valid_routes())
    # stops = asyncio.run(pgcli.get_stops_on_route('N'))
    clean_routes = [r[0] for r in routes]
    print(clean_routes)