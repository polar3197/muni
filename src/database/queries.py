




class PostgreSQLQueries():
    """
    Defines commonly used queries and returns them as strings
    """

    def ping(self):
        return "SELECT 1+1"
    
    def get_tables(self):
        return f"SELECT table_name FROM information_schema.tables"
        
    def get_most_curr_vehicles(self):
        return f"SELECT * FROM vehicles WHERE timestamp = (SELECT MAX(timestamp) FROM vehicles)"
