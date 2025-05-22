import psycopg2 as pg
import logging
from Database.connection import get_db_connection

def init_database():
    """
    Initializes the database by creating all necessary tables.
    """
    conn = get_db_connection()
    if not conn:
        logging.error("Failed to connect to database for initialization")
        return False

    try:
        with conn.cursor() as cur:
            # Read and execute the schema file
            with open('SQL/DB_Schema.sql', 'r') as schema_file:
                schema_sql = schema_file.read()
                cur.execute(schema_sql)
            
            conn.commit()
            logging.info("Database tables created successfully")
            return True
    except Exception as e:
        conn.rollback()
        logging.error(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()
        logging.info("Database connection closed after initialization") 