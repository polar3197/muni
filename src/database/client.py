from database.queries import PostgreSQLQueries
from config import PostgreSQLConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine # for sync pandas ops
from sqlalchemy import text
from functools import partial, cached_property
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import asyncio
import pytz

class PostgreSQLClient():

    # In database/client.py __init__
    def __init__(self, config: PostgreSQLConfig, retry_count: int = 3):
        self.config = config
        self.connection_string = config.connection_string  # Use pre-built string
        self.retry_count = retry_count
        self.queries = PostgreSQLQueries()
        # Don't need individual host, user, etc.

    @cached_property
    def engine(self):
        """
        Starts async engine to connect to db

        Args:

        Returns:
            - A sqlalchemy engine
        """
        return create_async_engine(self.connection_string())

    async def get_result(self, query: str):
        """
        Merges engine and query to return result

        Args:
            - postgres query

        Returns:
            - result object from query
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(query))
                return result
        except Exception as e:
            #LOG HERE
            print(f"Running query '{query}' failed -- {e}")

    async def ping(self):
        """
        Tests connection to db

        Args:

        Returns:
            - True or False
        """
        try:
            result = await self.get_result(self.queries.ping())
            row = result.fetchone()
            return row[0] == 2
        except Exception as e:
            print(f"exception: {e}")
            return False

    async def get_static_route_list(self):
        try:
            result = await self.get_result(self.queries.get_static_route_list())
            rows = result.fetchall()
            return [row.route_id for row in rows]
            # return [dict(row) for row in rows]
        except Exception as e:
            print(f"exception: {e}")
            return []

    async def get_static_nhood_list(self):
        try:
            result = await self.get_result(self.queries.get_static_nhood_list())
            rows = result.fetchall()
            return [row.nhood for row in rows]
        except Exception as e:
            print(f"exception: {e}")
            return []

    async def get_oldest_partition_name(self):
        """
        Tests connection to db

        Args:

        Returns:
            - True or False
        """
        try:
            result = await self.get_result(self.queries.get_oldest_partition_name())
            return result.fetchone()[0]
        except Exception as e:
            print(f"exception: {e}")
            return None
    
    async def get_current_vehicles(self, number: int):
        """
        returns vehicles from most recent timestamp

        Args: number of current vehicles to return, -1 fetches all

        Returns:
            A list of dictionaries, each representing a vehicle
        """
        try:
            result = await self.get_result(self.queries.get_most_curr_vehicles())
            column_names = list(result.keys())
            if number == -1:
                rows = result.fetchall()
            else:
                rows = result.fetchmany(number)
            
            pacific = pytz.timezone("America/Los_Angeles")
            vehicles = []
            
            for row in rows:
                vehicle = dict(zip(column_names, row))
                # Convert UTC to Pacific
                if vehicle.get('timestamp') and vehicle['timestamp'].tzinfo:
                    vehicle['timestamp'] = vehicle['timestamp'].astimezone(pacific)
                vehicles.append(vehicle)
            
            return vehicles
        except Exception as e:
            print(f"exception: {e}")
            return []

    async def get_nbrhd(self, nbrhd: str):
        """
        Returns a multigon representation of the specified neighborhood if it exists in 
        neighborhood table
        """
        try:
            result = await self.get_result(self.queries.get_neighborhood_border(nbrhd))
            column_names = list(result.keys())
            rows = result.fetchall()
            
            neighborhoods = []
            
            for row in rows:
                hood = dict(zip(column_names, row))
                neighborhoods.append(hood)
            
            return neighborhoods
        except Exception as e:
            print(f"exception: {e}")
            return []

    async def get_stops_on_route(self, route_id: str):
        """
        Returns a list of stop names and locations along the specified route
        """
        try:
            result = await self.get_result(self.queries.get_stops_on_route(route_id))
            column_names = list(result.keys())
            rows = result.fetchall()
            
            stops = []
            
            for row in rows:
                stop = dict(zip(column_names, row))
                stops.append(stop)
            
            return stops
        except Exception as e:
            print(f"exception: {e}")
            return []

    async def get_valid_routes(self):
        """
        Returns a list of stop names and locations along the specified route
        """
        try:
            result = await self.get_result(self.queries.get_valid_routes())
            routes = result.fetchall()            
            return [r[0] for r in routes]
        except Exception as e:
            print(f"exception: {e}")
            return []
    
    async def export_table_to_file(self, table_name, output_file) -> Optional[pd.DataFrame]:
        """
        Exports table with table_name into parquet foormat

        Args: table_name (name of the table)

        Returns: pandas dataframe of the table
        """
        try:
            result = await self.get_result(self.queries.get_table_size(table_name))
            size = result.fetchone()[0]
            print(f"Reading full table of size {size} from PostgreSQL...")
            # start separate thread to run synchronous pd function
            # Create a synchronous engine to pass to the thread
            
            connection_str = self.config.connection_string(asynch=False)
            sync_engine = create_engine(self.config.connection_string(asynch=False))
            query = self.queries.get_table_contents(table_name)

            def write_streaming():
                first_chunk = True
                for i, chunk in enumerate(pd.read_sql(query, sync_engine, chunksize=50000)):
                    print(f"Processing chunk {i+1} ({len(chunk):,} rows)...")
                    
                    # First chunk: create file; subsequent chunks: append
                    chunk.to_parquet(
                        output_file,
                        engine='fastparquet',  # fastparquet supports append mode
                        compression='snappy',
                        append=(not first_chunk),
                        index=False
                    )
                    first_chunk = False
            
            await asyncio.to_thread(write_streaming)
        except Exception as e:
            print(f"exception: {e}")
            return None

    async def create_new_vehicles_partition(self, weeks_in_advance=1) -> bool: 
        """
        Creates partition for upcoming week, in preparation.

        Args:

        Returns:
        """
        
        # start and end of next week is on monday
        now = datetime.now()
        start_of_week = now + timedelta(weeks=weeks_in_advance) - timedelta(days=(datetime.weekday(now)))

        # get year and week of year for partition creation 
        year, week, _ = start_of_week.isocalendar()
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0)
        end_of_week = (start_of_week + timedelta(weeks=1) - timedelta(days=1)).replace(hour=23, minute=59, second=0)
        

        # calculate timestamp range next week
        partition_name = f"vehicles_partition_{year}_w{week:02d}"

        # create new partition
        creation_query = self.queries.create_new_vehicles_partition(
            partition_name, start_of_week,end_of_week
        )
        creation_result = await self.get_result(creation_query)

        # add route index to new partition
        route_query = self.queries.create_route_idx(partition_name)
        route_result = await self.get_result(route_query)

        # add timestamp index to new partition
        timestamp_query = self.queries.create_timestamp_idx(partition_name)
        timestamp_result = await self.get_result(timestamp_query)

        print(f"Successfully created {partition_name}, spanning {start_of_week}-{end_of_week}")

    async def insert_vehicles(self, vehicles: List[dict]):  
        if not vehicles:
            return 0
        
        query = self.queries.insert_vehicles()

        async with self.engine.begin() as conn:
            result = await conn.execute(text(query), vehicles)
            return result.rowcount

    async def drop_partition(self, partition_name):  
        
        query = self.queries.drop_partition(partition_name)

        async with self.engine.begin() as conn:
            result = await conn.execute(text(query))
            return result.rowcount
        
