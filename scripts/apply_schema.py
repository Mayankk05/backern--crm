import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA_FILE = "schema.sql"

def apply_schema():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env file.")
        return

    print("Connecting to database...")
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()

        # Read schema.sql
        print(f"Reading {SCHEMA_FILE}...")
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            sql = f.read()

        # Execute SQL
        print("Applying schema (this may take a few seconds)...")
        # Split by semicolon to execute one by one (optional, but safer for some drivers)
        # However, gen_random_uuid() and other extensions might be needed.
        # We'll try executing the whole block first.
        try:
            cur.execute(sql)
            print("Schema applied successfully!")
        except Exception as e:
            print(f"Error executing SQL: {e}")
            print("Trying to execute statement by statement...")
            # Fallback: simple split by semicolon (not perfect for complex SQL but works for basic schemas)
            statements = sql.split(";")
            for statement in statements:
                if statement.strip():
                    try:
                        cur.execute(statement)
                    except Exception as stmt_error:
                        print(f"Error in statement: {statement[:50]}... -> {stmt_error}")
            print("Finished executing available statements.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    apply_schema()
