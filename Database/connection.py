import psycopg2 as pg
import os
import logging
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

# -- Database Connection -- #
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        conn = pg.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        logging.info("Database connection established.")
        return conn
    except pg.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        return None