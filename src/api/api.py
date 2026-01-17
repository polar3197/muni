from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.client import PostgreSQLClient
from config import PostgreSQLConfig
from typing import Optional
from pydantic import BaseModel
# from openai import AsyncOpenAI
import os

config = PostgreSQLConfig()
pg_client = PostgreSQLClient(config)

# move to openai config soon
# client = AsyncOpenAI()
# tools = [
#     {
#         "type": "function",
#         "name": "get_vehicle_on_route",
#         "description": "Returns a list of vehicle IDs that are currently on route R.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "sign": {
#                     "type": "string",
#                     "description": "An astrological sign like Taurus or Aquarius",
#                 },
#             },
#             "required": ["sign"],
#         },
#     },
# ]
# =====

class promptRequest(BaseModel):
    prompt: str

app = FastAPI(title="MUNI Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MUNI API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        result = await pg_client.ping()
        return{"message": result}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/vehicles/current")
async def get_current_vehicles(route_id: Optional[str] = None):
    """Get the latest position for each vehicle, optionally filtered by route"""
    try:
        vehicles_dict = await pg_client.get_current_vehicles(number=-1)
        return vehicles_dict
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/neighborhoods/{nbrhd}")
async def get_neighborhood_border(nbrhd: str):
    """Get the latest position for each vehicle, optionally filtered by route"""
    try:
        multigon = await pg_client.get_nbrhd(nbrhd)
        return multigon
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/stops/{route_id}")
async def get_stops_on_route(route_id: str):
    try:
        stops = await pg_client.get_stops_on_route(route_id)
        return stops
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/routes")
async def get_static_route_list():
    try:
        routes = await pg_client.get_static_route_list()
        return routes
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}  

@app.get("/neighborhoods")
async def get_static_nhood_list():
    try:
        nhoods = await pg_client.get_static_nhood_list()
        return nhoods
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}  


# @app.post("/api/llm-query")
# async def llm_query(data: promptRequest):
#     """ parses user query, passes to OpenAI and returns response """
#     user_prompt = data.prompt

#     # open connection to OpenAI
#     stream = await client.chat.completions.create(
#         model="gpt-5-nano",
#         messages=[
#             {"role": "system", 
#             "content": """You are a MUNI transit assistant with access to REAL-TIME vehicle data.
#                 IMPORTANT RULES:
#                 - ONLY answer questions using data from the tools/functions you call
#                 - DO NOT use general knowledge about MUNI schedules, routes, or operations
#                 - If you don't have current data to answer, say "I don't have that information in the current data"
#                 - Be concise and casual

#                 When users ask about buses:
#                 1. Use the provided tools to query current vehicle positions
#                 2. Base your response ONLY on what the tools return
#                 3. If the tools return empty results, say so"""
#             },            
#             {"role": "user", "content": f"{user_prompt}"}
#         ],
#         stream=True,
#         max_completion_tokens=1000,
#     )

#     return {
#         "message": f"{response.choices[0].message.content}",
#         "vehicle_ids": []
#     }


