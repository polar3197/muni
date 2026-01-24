from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from typing import Optional, List
from datetime import datetime
import asyncio
# import redis
import time
import json
import os

from database.client import PostgreSQLClient
from config import PostgreSQLConfig
from api.schemas import RouteIdsRequest, NearbyRoutesRequest

_cache = {
    "vehicles": {"data": List[dict], "updated": 0},
    "routes": None,
    "neighborhoods": None,
    "route_paths": {},
    "nearby_shapes": {} # {f"{lon}_{lat}": List[shape_ids]}
}

# Database setup
config = PostgreSQLConfig()
pg_client = PostgreSQLClient(config)

# Redis setup
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# rd = redis.Redis(host=REDIS_HOST , port=REDIS_PORT, db=0)

# FastAPI setup
app = FastAPI(title="MUNI Tracker API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    print("Loading static data into memory...")
    
    # Load static data once
    _cache["routes"] = await pg_client.get_static_route_list()
    _cache["neighborhoods"] = await pg_client.get_static_nhood_list()
    
    # Immediately load current vehicle data into cache
    try:
        # cache = rd.get("cv")
        # if cache:
        vehicles = await pg_client.get_current_vehicles(number=-1)
        _cache["vehicles"]["data"] = vehicles
        _cache["vehicles"]["updated"] = time.time()
        print(f"Loaded {len(vehicles)} initial vehicles")
    except Exception as e:
        print(f"Error loading initial vehicles: {e}")
    
    # Start background refresh
    asyncio.create_task(refresh_vehicles_loop())

async def refresh_vehicles_loop():
    """Background task to refresh vehicle data every 15 seconds"""
    while True:
        try:
            vehicles = await pg_client.get_current_vehicles(number=-1)
            _cache["vehicles"]["data"] = vehicles
            _cache["vehicles"]["updated"] = time.time()
            print(f"Refreshed {len(vehicles)} vehicles at {datetime.now()}")
        except Exception as e:
            print(f"Error refreshing vehicles: {e}")
        await asyncio.sleep(45)

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
async def get_current_vehicles():
    """Instant response from memory"""
    data = _cache["vehicles"]["data"]
    if data is None:
        raise HTTPException(status_code=503, detail="Vehicle data not yet loaded")
    return data

@app.get("/neighborhoods/{nbrhd}")
async def get_neighborhood_border(nbrhd: str):
    """ kk"""
    # REDIS CACHE
    try:
        multigon = await pg_client.get_nbrhd(nbrhd)
        return multigon
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/paths")
async def get_all_route_paths():
    if _cache["route_paths"]:
        return _cache["route_paths"]
    else: 
        result = await pg_client.get_all_route_paths()
        _cache["route_paths"] = result
        return result

@app.get("/routes")
async def get_static_route_list():
    # REDIS CACHE
    try:
        routes = await pg_client.get_static_route_list()
        return routes
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}  

@app.get("/neighborhoods")
async def get_static_nhood_list():
    # REDIS CACHE
    try:
        nhoods = await pg_client.get_static_nhood_list()
        return nhoods
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}  

@app.post("/nearby-shapes")
async def get_nearby_shapes(
    point: NearbyRoutesRequest
):
    try:
        shape_ids = await pg_client.get_nearby_shapes(point.lon, point.lat)
        return shape_ids
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)} 