from database.queries import PostgreSQLQueries
from config import PostgreSQLConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from functools import partial, cached_property
from urllib.parse import quote_plus
import asyncio

class PostgreSQLClient():

    # In database/client.py __init__
    def __init__(self, config: PostgreSQLConfig, retry_count: int = 3):
        self.connection_string = config.connection_string  # Use pre-built string
        self.retry_count = retry_count
        self.queries = PostgreSQLQueries()
        # Don't need individual host, user, etc.

    @cached_property
    def engine(self):
        print(f"conn string: {self.connection_string}")
        return create_async_engine(self.connection_string)

    async def get_result(self, query: str):
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text(query))
                return result
        except Exception as e:
            #LOG HERE
            print(f"Running query '{query}' failed -- {e}")

    async def ping(self):
        try:
            result = await self.get_result(self.queries.ping())
            row = result.fetchone()
            return row[0] == 2
        except Exception as e:
            print(f"exception: {e}")
            return False
    
    # async def get_current_vehicles(self, number: int):
    #     return await anext(
    #         fetch(
    #             cursor
    #         )
    #     )
