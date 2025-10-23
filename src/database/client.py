from database.queries import PostgreSQLQueries
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from functools import partial, cached_property
from urllib.parse import quote_plus
import asyncio

class PostgreSQLClient():

    def __init__(
        self,
        host,
        database,
        user,
        password,
        port,
        retry_count
    ):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.queries = PostgreSQLQueries()
        self.retry_count = retry_count

    @cached_property
    def engine(self):
        connection_string = f"postgresql+asyncpg://{self.user}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
        return create_async_engine(
            connection_string,
        )

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
            return False
    
    # async def get_current_vehicles(self, number: int):
    #     return await anext(
    #         fetch(
    #             cursor
    #         )
    #     )