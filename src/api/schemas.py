from pydantic import BaseModel
from typing import List

class RouteIdsRequest(BaseModel):
    route_ids: List[str]

class NearbyRoutesRequest(BaseModel):
    lon: float
    lat: float
