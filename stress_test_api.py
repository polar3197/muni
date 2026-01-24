from locust import HttpUser, task, between
from pydantic import BaseModel
from typing import List

class RouteIdsRequest(BaseModel):
    route_ids: List[str]

class TransitUser(HttpUser):
    wait_time = between(1, 3)  # Users wait 1-3 seconds between requests
    
    @task(10)  # Weight: 3x more common
    def get_vehicles(self):
        self.client.get("/vehicles/current")
    
    @task(2)
    def get_paths(self):
        payload = RouteIdsRequest(route_ids=['N', 'J', '38', '19', '18', '29', '43', '5', '1', '33', '22', '39', '9', '8', 'L', 'K'])
        self.client.post("/paths/active", json=payload.model_dump())
    
    # @task(1)
    # def get_specific_route(self):
    #     self.client.get("/routes")
    
    # @task(1)
    # def search_stops(self):
    #     self.client.get("/neighborhoods")

    # def on_start(self):
    #     # Called once per user when they start
    #     pass
