# scripts/reload_gtfs_static.py
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Path to GTFS files
GTFS_PATH = "/Users/charlie/Code/projects/webapps/muni/data/muni_gtfs-current"

def reload_trips():
    print("Loading trips.txt...")
    trips = pd.read_csv(f"{GTFS_PATH}/trips.txt")
    
    print(f"Found {len(trips)} trips")
    
    with engine.connect() as conn:
        # Clear old data
        conn.execute(text("TRUNCATE TABLE trips CASCADE"))
        conn.commit()
        
        # Load new data
        trips.to_sql('trips', conn, if_exists='append', index=False)
        
    print("✅ Trips loaded")

def reload_shapes():
    print("Loading shapes.txt...")
    shapes_raw = pd.read_csv(f"{GTFS_PATH}/shapes.txt")
    
    print(f"Found {len(shapes_raw)} shape points")
    print("Grouping into LineStrings...")
    
    # Group shape points into LineStrings
    with engine.connect() as conn:
        # Clear old shapes
        conn.execute(text("TRUNCATE TABLE shapes CASCADE"))
        conn.commit()
        
        # Get unique shape_ids
        shape_ids = shapes_raw['shape_id'].unique()
        print(f"Processing {len(shape_ids)} unique shapes...")
        
        for i, shape_id in enumerate(shape_ids):
            if i % 100 == 0:
                print(f"  Processed {i}/{len(shape_ids)} shapes...")
            
            # Get points for this shape, ordered by sequence
            shape_points = shapes_raw[shapes_raw['shape_id'] == shape_id].sort_values('shape_pt_sequence')
            
            # Build WKT LineString
            coords = [f"{row['shape_pt_lon']} {row['shape_pt_lat']}" 
                     for _, row in shape_points.iterrows()]
            wkt = f"LINESTRING({', '.join(coords)})"
            
            # Get total distance if available
            total_dist = shape_points['shape_dist_traveled'].max() if 'shape_dist_traveled' in shape_points.columns else None
            
            # Insert into database
            query = text("""
                INSERT INTO shapes (shape_id, route_line, total_distance)
                VALUES (:shape_id, ST_GeomFromText(:wkt, 4326), :total_distance)
            """)
            
            conn.execute(query, {
                "shape_id": shape_id,
                "wkt": wkt,
                "total_distance": total_dist
            })
        
        conn.commit()
    
    print(f"✅ {len(shape_ids)} shapes loaded")

def reload_routes():
    print("Loading routes.txt...")
    routes = pd.read_csv(f"{GTFS_PATH}/routes.txt")
    
    print(f"Found {len(routes)} routes")
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE routes CASCADE"))
        conn.commit()
        
        routes.to_sql('routes', conn, if_exists='append', index=False)
    
    print("✅ Routes loaded")

def rebuild_route_shapes():
    print("Rebuilding route_shapes...")
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE route_shapes CASCADE"))
        
        query = text("""
            INSERT INTO route_shapes (route_id, trip_id, direction_id, shape_id)
            SELECT DISTINCT route_id, trip_id, direction_id, shape_id
            FROM trips
            WHERE shape_id IS NOT NULL
        """)
        
        result = conn.execute(query)
        conn.commit()
        
    print(f"✅ Route shapes rebuilt")

if __name__ == "__main__":
    print("=== Reloading GTFS Static Data ===\n")
    
    reload_trips()
    reload_shapes()
    reload_routes()
    rebuild_route_shapes()
    
    print("\n=== All done! ===")
    print("\nVerify with:")
    print("  SELECT COUNT(*) FROM trips;")
    print("  SELECT COUNT(*) FROM shapes;")
    print("  SELECT COUNT(*) FROM route_shapes;")