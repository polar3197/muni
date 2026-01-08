
import re

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

    def get_table_size(self, table_name):
        return f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}'));"

    def get_neighborhood_border(self, nbrhd):
        return f"SELECT nhood, wkb_geometry FROM neighborhoods WHERE nhood == {nbrhd};"
        
    def get_most_curr_vehicles(self):
        return f"SELECT * FROM vehicles WHERE timestamp = (SELECT MAX(timestamp) FROM vehicles);"

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
            INSERT INTO vehicles 
                (timestamp, vehicle_id, lat, lon, occupancy, 
                direction_id, bearing, current_status, 
                current_stop_sequence, stop_id, active, 
                speed_mph, trip_id, route_id, neighborhood) 
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
                n.nhood FROM (
                        SELECT ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) as point
                    ) p
                    LEFT JOIN neighborhoods n 
                        ON ST_Within(p.point, n.wkb_geometry)
        """

    # r.name FROM (
    #                     SELECT ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) as point
    #                 ) p
    #                 LEFT JOIN neighborhoods n 
    #                     ON ST_Within(p.point, n.wkb_geometry)

    def drop_partition(self, partition_name):
        return f"""
            DROP TABLE {partition_name};
        """

