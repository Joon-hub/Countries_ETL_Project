import psycopg2 as pg
import logging



# ---Loading to Postgres Database--- #
def insert_data_to_db(conn,data):
    """
    Insert the transformed data into the PostgreSQL database.
    """

    logging.info("Inserting data into the database...")
    cursor = conn.cursor()

    try:
        # --- Insert Currencies with UPSERT ---
        logging.info(f"Inserting {len(data['currencies'])} currencies...")
        currency_insert_query = """
        INSERT INTO currency (code, name, symbol)
        VALUES (%s, %s, %s)
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name, symbol = EXCLUDED.symbol;
        """

        currency_values =[(c['code'],c['name'],c['symbol']) for c in data['currencies']]
        if currency_values:
            cursor.executemany(currency_insert_query, currency_values)
        logging.info("Currencies inserted/updated.")


        # --- Insert Language with UPSERT ---
        logging.info(f"Inserting {len(data['languages'])} languages...")
        language_insert_query = """
        INSERT INTO language (code, name)
        VALUES (%s, %s)
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name;
        """
        
        language_values = [(lang['code'],lang['name']) for lang in data['languages']]
        if language_values:
            cursor.executemany(language_insert_query, language_values)
        logging.info("Languages inserted/updated.")

        # --- Insert Countries with UPSERT and get IDs ---
        logging.info(f"Inserting {len(data['countries'])} countries...")
        country_insert_query = """
        INSERT INTO country (cca2, name, capital, region, subregion, population, area)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (cca2) DO UPDATE
        SET
            name = EXCLUDED.name,
            capital = EXCLUDED.capital,
            region = EXCLUDED.region,
            subregion = EXCLUDED.subregion,
            population = EXCLUDED.population,
            area = EXCLUDED.area
        RETURNING id, cca2; -- Return the generated/existing ID and cca2
        """
        country_values = [(
            c['cca2'],c['name'],c['capital'],c['region']
            ,c['subregion'],c['population'],c['area']
        ) for c in data['countries']]

        country_id_map = {}
        if country_values:
           # Execute and fetch the returned IDs and cca2s    
           for country in country_values:
               cursor.execute(country_insert_query, country)
               row = cursor.fetchone()
               if row:
                   country_id_map[row[1]] = row[0]  # Map cca2 to id

        logging.info("Countries inserted/updated and ID's fetched.")

        # --- Get Currency and Language IDs for junction table ---
        # Fetch IDs for currencies and languages based on their codes
        currency_id_map = {}
        if data['currencies']:
            cursor.execute("SELECT id, code FROM currency WHERE code IN %s", (tuple(c['code'] for c in data['currencies']),))
            currency_id_map = {row[1]: row[0] for row in cursor.fetchall()}

        language_id_map = {}
        if data['languages']:
            cursor.execute("SELECT id, code FROM language WHERE code IN %s", (tuple(lang['code'] for lang in data['languages']),))
            language_id_map = {row[1]: row[0] for row in cursor.fetchall()}

        logging.info("Fetched currency and language IDs.")

        # --- Insert country_currency junction tables with UPSERT ---
        logging.info(f"Inserting {len(data['country_currency'])} country-currency relationships...")
        
        country_currency_values = []
        for cc in data['country_currency']:
            country_id = country_id_map.get(cc['country_cca2'])
            currency_id = currency_id_map.get(cc['currency_code'])
            if country_id is not None and currency_id is not None:
                country_currency_values.append((country_id, currency_id))

        # use ON CONFLICT DO NOTHING for junction tables as the composite PK handles uniqueness
        country_currency_insert_query = """
        INSERT INTO country_currency (country_id, currency_id)
        VALUES (%s, %s)
        ON CONFLICT (country_id, currency_id) DO NOTHING;
        """
        if country_currency_values:
            cursor.executemany(country_currency_insert_query, country_currency_values)
        logging.info("Country-currency relationships inserted/updated.")

        # --- Insert into country_language Junction table with UPSERT ---
        logging.info(f"Inserting {len(data['country_language'])} country-language relationships...")

        country_language_values = []
        for cl in data['country_language']:
            country_id = country_id_map.get(cl['country_cca2'])  # Corrected: country_cca2 instead of country_cca3
            language_id = language_id_map.get(cl['language_code'])
            if country_id is not None and language_id is not None:
                country_language_values.append((country_id, language_id))
        
        country_language_insert_query = """
        INSERT INTO country_language (country_id, language_id)
        VALUES (%s, %s)
        ON CONFLICT (country_id, language_id) DO NOTHING;
        """

        if country_language_values:
            cursor.executemany(country_language_insert_query, country_language_values)
        logging.info("Country-language relationships inserted/updated.")

        # --- Commit the transaction ---
        conn.commit()
        logging.info("All data successfully loaded and transaction committed.")

    except pg.Error as e:
        # Rollback the transaction if any error occurs
        conn.rollback()
        logging.error(f"Database error during loading: {e}")
    finally:
        # Close the cursor
        cursor.close()
        logging.info("Database cursor closed.")