## environment set-up 
- pipenv shell
- pipenv install requests
- pipenv run python data_ingestion.py


## SQL 
- composite primpary key
- indexing on foreingn keys for better performance


-- create indexes for faster querying
CREATE INDEX idx_country_currency_country_id ON country_currency(country_id);
CREATE INDEX idx_country_currency_currency_id ON country_currency(currency_id);
CREATE INDEX idx_country_language_country_id ON country_language(country_id);
CREATE INDEX idx_country_language_language_id ON country_language(language_id);

Indexing is performed on single column for e.g. 'country_id' and it works on principle of B-Tree


## ETL CODE
import requests
import psycopg2
import os # Used for accessing environment variables
from dotenv import load_dotenv # Recommended for loading environment variables from a .env file
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Configuration ---
API_URL = "https://restcountries.com/v3.1/all"

# Database connection details from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost") # Default to localhost if not set
DB_NAME = os.getenv("DB_NAME", "country_db") # Default database name
DB_USER = os.getenv("DB_USER", "user")     # Default user
DB_PASSWORD = os.getenv("DB_PASSWORD", "password") # Default password
DB_PORT = os.getenv("DB_PORT", "5432")     # Default PostgreSQL port

# --- Database Connection ---
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.connection or None: The database connection object, or None if connection fails.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        logging.info("Database connection established successfully.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        return None

# --- Extraction (E) ---
def fetch_all_countries_data(url):
    """
    Fetches data for all countries from the REST Countries API.

    Args:
        url (str): The API endpoint URL.

    Returns:
        list or None: A list of country dictionaries if successful, None otherwise.
    """
    logging.info(f"Attempting to fetch data from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        logging.info(f"Successfully fetched data for {len(data)} countries.")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return None

# --- Transformation (T) ---
def transform_country_data(raw_data):
    """
    Transforms the raw API data into a format suitable for the database schema.

    Args:
        raw_data (list): A list of raw country dictionaries from the API.

    Returns:
        dict: A dictionary containing lists of transformed data for each table.
              e.g., {'countries': [...], 'currencies': [...], 'languages': [...],
                     'country_currencies': [...], 'country_languages': [...]}
    """
    logging.info("Starting data transformation.")
    transformed = {
        'countries': [],
        'currencies': {}, # Use dict to easily track unique currencies by code
        'languages': {},  # Use dict to easily track unique languages by code
        'country_currencies': [],
        'country_languages': []
    }

    for country in raw_data:
        # Extract core country data
        # Use .get() with a default value (like None or an empty list/dict)
        # to handle cases where a field might be missing in the API response.
        cca3 = country.get('cca3')
        if not cca3: # Skip countries without a valid cca3 code
            logging.warning(f"Skipping country with missing cca3: {country.get('name', {}).get('common', 'Unknown')}")
            continue

        name = country.get('name', {}).get('common')
        capital_list = country.get('capital', [])
        capital = capital_list[0] if capital_list else None # Take the first capital if available
        region = country.get('region')
        subregion = country.get('subregion')
        population = country.get('population')
        area = country.get('area')

        transformed['countries'].append({
            'cca3': cca3,
            'name': name,
            'capital': capital,
            'region': region,
            'subregion': subregion,
            'population': population,
            'area': area
        })

        # Process currencies
        currencies = country.get('currencies', {})
        for code, details in currencies.items():
            currency_name = details.get('name')
            currency_symbol = details.get('symbol')
            if code and currency_name: # Ensure code and name are present
                 # Add to unique currencies dictionary if not already present
                if code not in transformed['currencies']:
                    transformed['currencies'][code] = {'code': code, 'name': currency_name, 'symbol': currency_symbol}

                # Add entry for country_currency junction table (uses cca3 for now, will link by ID later)
                transformed['country_currencies'].append({'country_cca3': cca3, 'currency_code': code})


        # Process languages
        languages = country.get('languages', {})
        for code, name in languages.items():
            if code and name: # Ensure code and name are present
                # Add to unique languages dictionary if not already present
                if code not not in transformed['languages']:
                    transformed['languages'][code] = {'code': code, 'name': name}

                # Add entry for country_language junction table (uses cca3 for now, will link by ID later)
                transformed['country_languages'].append({'country_cca3': cca3, 'language_code': code})

    # Convert unique currency and language dictionaries back to lists of dictionaries
    transformed['currencies'] = list(transformed['currencies'].values())
    transformed['languages'] = list(transformed['languages'].values())

    logging.info(f"Transformation complete. Found {len(transformed['countries'])} countries, {len(transformed['currencies'])} unique currencies, and {len(transformed['languages'])} unique languages.")
    return transformed

# --- Loading (L) ---
def insert_data_to_db(conn, data):
    """
    Inserts the transformed data into the PostgreSQL database.

    Args:
        conn (psycopg2.connection): The database connection object.
        data (dict): The dictionary containing transformed data lists.
    """
    logging.info("Starting data loading into the database.")
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
        currency_values = [(c['code'], c['name'], c['symbol']) for c in data['currencies']]
        if currency_values:
            cursor.executemany(currency_insert_query, currency_values)
        logging.info("Currencies inserted/updated.")

        # --- Insert Languages with UPSERT ---
        logging.info(f"Inserting {len(data['languages'])} languages...")
        language_insert_query = """
        INSERT INTO language (code, name)
        VALUES (%s, %s)
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name;
        """
        language_values = [(lang['code'], lang['name']) for lang in data['languages']]
        if language_values:
             cursor.executemany(language_insert_query, language_values)
        logging.info("Languages inserted/updated.")

        # --- Insert Countries with UPSERT and get IDs ---
        logging.info(f"Inserting {len(data['countries'])} countries...")
        # Use a dictionary to map cca3 to database ID after insertion
        country_id_map = {}
        country_insert_query = """
        INSERT INTO country (cca3, name, capital, region, subregion, population, area)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (cca3) DO UPDATE
        SET
            name = EXCLUDED.name,
            capital = EXCLUDED.capital,
            region = EXCLUDED.region,
            subregion = EXCLUDED.subregion,
            population = EXCLUDED.population,
            area = EXCLUDED.area
        RETURNING id, cca3; -- Return the generated/existing ID and cca3
        """
        country_values = [(
            c['cca3'], c['name'], c['capital'], c['region'],
            c['subregion'], c['population'], c['area']
        ) for c in data['countries']]

        if country_values:
            # Execute and fetch the returned IDs and cca3s
            cursor.executemany(country_insert_query, country_values)
            for row in cursor.fetchall():
                country_id_map[row[1]] = row[0] # Map cca3 to id

        logging.info("Countries inserted/updated and IDs fetched.")

        # --- Get Currency and Language IDs for Junction Tables ---
        # Fetch IDs for currencies and languages based on their codes
        currency_id_map = {}
        if data['currencies']:
            cursor.execute("SELECT id, code FROM currency WHERE code IN %s", (tuple(c['code'] for c in data['currencies']),))
            for row in cursor.fetchall():
                currency_id_map[row[1]] = row[0]

        language_id_map = {}
        if data['languages']:
            cursor.execute("SELECT id, code FROM language WHERE code IN %s", (tuple(lang['code'] for lang in data['languages']),))
            for row in cursor.fetchall():
                language_id_map[row[1]] = row[0]

        logging.info("Fetched currency and language IDs.")

        # --- Insert into country_currency Junction Table with UPSERT ---
        logging.info(f"Inserting {len(data['country_currencies'])} country-currency relationships...")
        country_currency_values = []
        for cc in data['country_currencies']:
            country_id = country_id_map.get(cc['country_cca3'])
            currency_id = currency_id_map.get(cc['currency_code'])
            if country_id is not None and currency_id is not None:
                country_currency_values.append((country_id, currency_id))

        # Use ON CONFLICT DO NOTHING for junction tables as the composite PK handles uniqueness
        country_currency_insert_query = """
        INSERT INTO country_currency (country_id, currency_id)
        VALUES (%s, %s)
        ON CONFLICT (country_id, currency_id) DO NOTHING;
        """
        if country_currency_values:
            cursor.executemany(country_currency_insert_query, country_currency_values)
        logging.info("Country-currency relationships inserted/updated.")

        # --- Insert into country_language Junction Table with UPSERT ---
        logging.info(f"Inserting {len(data['country_languages'])} country-language relationships...")
        country_language_values = []
        for cl in data['country_languages']:
            country_id = country_id_map.get(cl['country_cca3'])
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

    except psycopg2.Error as e:
        # Rollback the transaction if any error occurs
        conn.rollback()
        logging.error(f"Database error during loading: {e}")
    finally:
        # Close the cursor
        cursor.close()
        logging.info("Database cursor closed.")


# --- Main Execution ---
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



## step4 sql queries 
-- SQL queries for data querying and analysis on the country database

-- Example Query 1: Find all countries in Asia with a population greater than 100 million.
-- This query selects the country name and population from the 'country' table,
-- filtering by region 'Asia' and population greater than 100,000,000.
SELECT
    name,
    population
FROM
    country
WHERE
    region = 'Asia' AND population > 100000000;

-- Example Query 2: List currencies used in European countries.
-- This query joins the 'currency', 'country_currency', and 'country' tables
-- to find the names and symbols of currencies used in countries located in 'Europe'.
-- DISTINCT is used to list each currency only once.
SELECT DISTINCT
    cur.name,
    cur.symbol
FROM
    currency cur
JOIN
    country_currency cc ON cur.id = cc.currency_id
JOIN
    country c ON cc.country_id = c.id
WHERE
    c.region = 'Europe';

-- Example Query 3: Identify countries that share the same currency (e.g., USD).
-- This query joins the 'country', 'country_currency', and 'currency' tables
-- to find the names of countries that use a specific currency code (e.g., 'USD').
-- Replace 'USD' with the currency code you want to query for.
SELECT
    c.name
FROM
    country c
JOIN
    country_currency cc ON c.id = cc.country_id
JOIN
    currency cur ON cc.currency_id = cur.id
WHERE
    cur.code = 'USD'; -- <<< Replace 'USD' with the desired currency code

-- Example Query 4: Count the number of languages spoken in Africa.
-- This query joins the 'language', 'country_language', and 'country' tables
-- to count the distinct languages associated with countries in 'Africa'.
SELECT
    COUNT(DISTINCT lang.id) AS number_of_languages_in_africa
FROM
    language lang
JOIN
    country_language cl ON lang.id = cl.language_id
JOIN
    country c ON cl.country_id = c.id
WHERE
    c.region = 'Africa';

-- Example Query 5 (Optional): Find all languages spoken in a specific country (e.g., France - FRA).
-- This query joins the 'language', 'country_language', and 'country' tables
-- to list the names of languages spoken in a country with a specific cca3 code.
-- Replace 'FRA' with the desired country cca3 code.
SELECT
    lang.name
FROM
    language lang
JOIN
    country_language cl ON lang.id = cl.language_id
JOIN
    country c ON cl.country_id = c.id
WHERE
    c.cca3 = 'FRA'; -- <<< Replace 'FRA' with the desired country cca3 code

-- Example Query 6 (Optional): Find all countries that speak a specific language (e.g., Spanish - spa).
-- This query joins the 'country', 'country_language', and 'language' tables
-- to list the names of countries where a language with a specific code is spoken.
-- Replace 'spa' with the desired language code.
SELECT
    c.name
FROM
    country c
JOIN
    country_language cl ON c.id = cl.country_id
JOIN
    language lang ON cl.language_id = lang.id
WHERE
    lang.code = 'spa'; -- <<< Replace 'spa' with the desired language code



Project Outline

🚀 Project Plan: Country Info Database with REST Countries API
1. Project Goal
Build a local PostgreSQL database to store detailed country information fetched from REST Countries API. This project will help you practice:

Making API requests in Python

Handling and transforming JSON data

Designing a normalized database schema

Inserting data into PostgreSQL (bulk insert or upsert)

Querying and analyzing the stored data

2. Data Source
REST Countries API endpoint:
https://restcountries.com/v3.1/all
(returns info about all countries in JSON)

3. Outline of Steps
Step 1: Explore the API
Use tools like Postman or curl to see what data fields are available.

Identify important fields you want to store, e.g.

name.common (country name)

cca3 (3-letter country code)

capital

region, subregion

population

languages (object)

currencies (object)

area (land size)

timezones

Step 2: Design PostgreSQL Schema
Example tables:

Table	Columns	Notes
country	id (PK), cca3 (unique), name, capital, region, subregion, population, area	Main country info
currency	id (PK), code, name, symbol	List of currencies (many-to-many)
country_currency	country_id (FK), currency_id (FK)	Relationship table for many-to-many relation
language	id (PK), code, name	List of languages (many-to-many)
country_language	country_id (FK), language_id (FK)	Relationship table

Step 3: Write Python code to:
Fetch data from REST Countries API

Parse JSON response

Transform nested fields (currencies, languages) into normalized tables

Connect to PostgreSQL

Insert data (handle duplicates with UPSERT logic)

Step 4: Query and Analyze Data
Example queries:

Find all countries in Asia with population > 100 million

List currencies used in countries in Europe

Find countries using the same currency

Count languages spoken in Africa

Step 5: (Optional) Wrap as a modular Python package or notebook
Functions for fetching, parsing, and inserting

Make code reusable and clean

4. Tips to Improve
Use psycopg2 or sqlalchemy for DB connection

Use environment variables or .env files for DB credentials

Add exception handling for API failures or DB errors

Use batch inserts for efficiency

Use logging to monitor ETL progress

Version control with Git and clear commit messages

Write README explaining project and setup instructions

5. Extra Challenge
Schedule this ETL to run weekly to update the database

Add a simple Flask API to serve country info from your database

Visualize data with matplotlib or Plotly inside Jupyter

Would you like me to help you draft:

A sample DB schema SQL script?

Python code snippets for API extraction?

The ETL pipeline structure?

Query examples?

Just say what you want next!