
import re
from typing import List

class PostgreSQLQueries():
    """
    Defines commonly used queries and returns them as strings
    """

    def ping(self):
        return "SELECT 1+1"
    
    def get_tables_list(self):
        return f"SELECT table_name FROM information_schema.tables;"

    def get_table_contents(self, table_name):
        return f"SELECT * FROM {table_name};"

    def get_shapes(self, route_id):
        # first join tables on shared shape_id, then select rows that have given route_id
        return f"""
            SELECT s.shape_id, ST_AsGeoJSON(s.route_line) as route_line 
            FROM shapes s 
            JOIN trips t 
            ON t.shape_id = s.shape_id 
            WHERE t.route_id = '{route_id}';
        """

    # def get_active_route_paths(self, route_ids: List[str]):
    #     return f"""
    #         SELECT 
    #             cs.route_id, 
    #             cs.direction_id, 
    #             cs.shape_id as shape_id,
    #             ST_AsGeoJSON(s.route_line) as route_line 
    #         FROM curated_shapes cs
    #         JOIN shapes s ON cs.shape_id = s.shape_id
    #         WHERE cs.route_id = ANY(ARRAY{route_ids});
    #     """

    def get_nearby_shapes(self, lon: float, lat: float, distance_meters: float = 150):
        return f"""
            SELECT shape_id 
            FROM shapes
            WHERE ST_DWithin(
                ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography,
                route_line::geography,
                {distance_meters}
            );
        """
    
    def get_all_route_paths(self):
        return f"""
            SELECT 
                shape_id,
                route_id,
                direction_id,
                shape_polyline
            FROM shapes_json;
        """
    
    def get_static_route_list(self):
        return f"SELECT DISTINCT route_id FROM routes;"
    
    def get_static_nhood_list(self):
        return f"SELECT DISTINCT nhood FROM neighborhoods;"

    def get_table_size(self, table_name):
        return f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}'));"

    def get_neighborhood_border(self, nbrhd):
        return f"SELECT nhood, wkb_geometry FROM neighborhoods WHERE nhood = {nbrhd};"
        
    def get_curr_vehicles(self):
        return f"""SELECT 
                    route_id, 
                    vehicle_id, 
                    ST_X(location) as lon, 
                    ST_Y(location) as lat, 
                    timestamp, occupancy, 
                    direction_id, 
                    shape_id,
                    neighborhood
                    FROM vehicles 
                    WHERE timestamp = (SELECT MAX(timestamp) FROM vehicles);"""

    def get_oldest_partition_name(self):
        return f"""SELECT min(table_name) FROM information_schema.tables
                    WHERE table_name LIKE 'vehicles_partition_%_w%';
            """

# === queries to do with stops ====
    def get_stops_on_route(self, route_id):
        # returns the name, id, lat and lon of bus stops on given route
        # currently returns stops on both sides of the street :(
        return f"""
            SELECT 
                r.route_id, 
                array_agg(
                    json_build_object(
                        'name', s.name,
                        'stop_id', s.stop_id,
                        'lat', s.lat,
                        'lon', s.lon
                    )
                ) as stops
            FROM routes r 
            JOIN stops s ON s.stop_id = ANY(r.stops) 
            WHERE r.route_id = '{route_id.upper()}' 
            GROUP BY r.route_id;
        """
# === queries to do with stops ====

# === queries to do with routes ====
    def get_valid_routes(self):
        return """
            SELECT distinct route_id FROM routes;
        """
# === queries to do with routes ====

    def create_new_vehicles_partition(self, partition_name, start_of_week, end_of_week):
        return f"""
            CREATE TABLE IF NOT EXISTS {partition_name} 
            PARTITION OF vehicles
            FOR VALUES FROM ('{start_of_week}') TO ('{end_of_week}');
            """

    def create_route_idx(self, partition_name):
        return f"""                        
            CREATE INDEX IF NOT EXISTS {partition_name}_route_idx
            ON {partition_name}(route_id);
        """

    def create_timestamp_idx(self, partition_name):
        return f"""  
            CREATE INDEX IF NOT EXISTS {partition_name}_time_idx
            ON {partition_name}(timestamp);
        """

    def insert_vehicles(self):
        # simultaneously enriches vehicle records with their neighborhood. 
        # Thisinfo is technically already within lat, lon, but makes it cleaner
        # than having to join on every query
        return """
            WITH point_data AS (
                SELECT ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) as geom
            ),
            trip_shape AS (
                SELECT shape_id 
                FROM trips 
                WHERE trip_id = :trip_id 
                LIMIT 1
            )
            INSERT INTO vehicles 
                (timestamp, vehicle_id, lat, lon, occupancy, 
                direction_id, bearing, current_status, 
                current_stop_sequence, stop_id, active, 
                speed_mph, trip_id, route_id, location, neighborhood, shape_id) 
            SELECT 
                :timestamp, 
                :vehicle_id, 
                :lat, 
                :lon, 
                :occupancy,
                :direction_id, 
                :bearing, 
                :current_status,
                :current_stop_sequence, 
                :stop_id, 
                :active,
                :speed_mph, 
                :trip_id, 
                :route_id,
                p.geom,
                n.nhood,
                ts.shape_id
            FROM point_data p
            CROSS JOIN trip_shape ts
            LEFT JOIN neighborhoods n 
                ON ST_Within(p.geom, n.wkb_geometry)
        """

    def drop_partition(self, partition_name):
        return f"""
            DROP TABLE {partition_name};
        """

