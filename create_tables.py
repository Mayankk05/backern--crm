import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database parameters from user

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "",
    "host": "db.reslibwqwawflgpdohmw.supabase.co",
    "port": "5432"
}

def create_tables():
    try:
        # Connect to the database using parameters
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Read the schema.sql file
        with open("schema.sql", "r") as f:
            sql = f.read()
            
        # Execute the SQL
        print("Executing schema.sql...")
        cur.execute(sql)
        
        # Commit the changes
        conn.commit()
        print("Tables created successfully!")
        
        # Close connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
