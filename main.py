try:
    
    import utils.logger
    import logging
    from etl.extract import fetch_all_countries_data
    from etl.transform import transform_country_data

    from Database.connection import get_db_connection
    from Database.load import insert_data_to_db

    from config.settings import API_URL

except ImportError as e:
    print(f"Error importing modules: {e}")
    exit(1)

print("Starting ETL process...")
# --- Main Execution --- #
if __name__ == "__main__":
    # 1. Fetch data
    raw_country_data = fetch_all_countries_data(API_URL)

    if raw_country_data:
        # 2. Transform data
        transformed_data = transform_country_data(raw_country_data)

        # 3. Get database connection
        db_connection = get_db_connection()

        if db_connection:
            # 4. Insert data into the database
            insert_data_to_db(db_connection, transformed_data)

            # Close the database connection
            db_connection.close()
            logging.info("Database connection closed.")
        else:
            logging.error("Could not connect to the database. Data loading aborted.")

    else:
        logging.error("Could not fetch raw country data. ETL process aborted.")