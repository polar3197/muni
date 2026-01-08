from config import GTFSConfig
from google.transit import gtfs_realtime_pb2
import requests
from typing import Optional, List
from datetime import datetime, timezone
import pytz

class GTFSFetcher():
    def __init__(self, config=GTFSConfig):
        self.config = config
        self.api_key = config.api_key
        self.static_url = f"http://api.511.org/transit/datafeeds?api_key={self.api_key}&operator_id=RG"
        self.live_url = f"http://api.511.org/transit/vehiclepositions?api_key={self.api_key}&agency=SF"

    def fetch_live_vehicles(self) -> Optional[List[dict]]:
        """
        Fetches current vehicle records from SFMTA GTFS API

        Args:

        Returns:
            A list of dictionaries, each representing a vehicle
        """
        try:
            response = requests.get(self.live_url, timeout=30)
            response.raise_for_status()
            # use GTFS tool to parse protocol buffer into FeedMessage object
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            vehicles = []
            # iterate through entities (potential vehicles)
            for entity in feed.entity:
                vehicle = self.extract_validate_vehicle(entity)
                # check if vehicle was complete
                if vehicle:
                    vehicles.append(vehicle)
            return vehicles
        except Exception as e:
            # LOGGING HERE
            print(f"exception in fetching live vehicles: {e}")

    def extract_validate_vehicle(self, entity) -> Optional[dict]:
        """
        Fetches current vehicle records from SFMTA GTFS API

        Args:

        Returns:
            A dictionaries, each representing a vehicle
        """
        # filter out: non-vehicles, non-active vehicles,
        #             vehicles that don't report position
        if (not entity.HasField("vehicle") or
           not entity.vehicle.HasField("trip") or
           not entity.vehicle.HasField("position")):
            #print(f"non-vehicle entitity: {entity}")
            return None
        try:
            # Time conversion
            dt = datetime.fromtimestamp(entity.vehicle.timestamp, tz=timezone.utc)
            dt_local = dt.astimezone(pytz.timezone("America/Los_Angeles"))

            # trip data
            trip_id = getattr(entity.vehicle.trip, 'trip_id', None)
            route_id = getattr(entity.vehicle.trip, 'route_id', None)
            direction_id = getattr(entity.vehicle.trip, 'direction_id', None)
            
            # Position data
            lat = getattr(entity.vehicle.position, 'latitude', None)
            lon = getattr(entity.vehicle.position, 'longitude', None)
            bearing = getattr(entity.vehicle.position, 'bearing', None)
            speed_mph = getattr(entity.vehicle.position, 'speed', None)
            
            # Vehicle status
            vehicle_id_raw = getattr(entity.vehicle.vehicle, 'id', None)
            stop_id_raw = getattr(entity.vehicle, 'stop_id', None)
            current_stop_sequence = getattr(entity.vehicle, 'current_stop_sequence', None)
            current_status = getattr(entity.vehicle, 'current_status', None) 
            occupancy = getattr(entity.vehicle, 'occupancy_status', None)

            # Convert to int, handling empty strings and None
            vehicle_id = int(vehicle_id_raw) if vehicle_id_raw and vehicle_id_raw != '' else None
            stop_id = int(stop_id_raw) if stop_id_raw and stop_id_raw != '' else None
            
            return {
                'timestamp': dt_local,
                'active': bool(trip_id),
                'trip_id': trip_id,
                'route_id': route_id,
                'direction_id': direction_id,
                'vehicle_id': vehicle_id,
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'speed_mph': speed_mph,
                'current_stop_sequence': current_stop_sequence,
                'current_status': current_status,
                'stop_id': stop_id,
                'occupancy': occupancy,
            }
        except Exception as e:
            print(f"Couldn't fetch: {e}")
            return None


    # def fetch_static_transit_data(self) -> 
