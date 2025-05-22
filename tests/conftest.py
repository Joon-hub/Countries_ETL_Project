# tests/conftest.py
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from Database.connection import get_db_connection
import requests_mock

@pytest.fixture(scope="module")
def db_connection():
    conn = get_db_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currency (
            id SERIAL PRIMARY KEY,
            code VARCHAR(10) UNIQUE,
            name TEXT,
            symbol TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS language (
            id SERIAL PRIMARY KEY,
            code VARCHAR(10) UNIQUE,
            name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS country (
            id SERIAL PRIMARY KEY,
            cca2 VARCHAR(2) UNIQUE,
            name TEXT,
            capital TEXT,
            region TEXT,
            subregion TEXT,
            population INTEGER,
            area FLOAT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS country_currency (
            country_id INTEGER REFERENCES country(id),
            currency_id INTEGER REFERENCES currency(id),
            PRIMARY KEY (country_id, currency_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS country_language (
            country_id INTEGER REFERENCES country(id),
            language_id INTEGER REFERENCES language(id),
            PRIMARY KEY (country_id, language_id)
        )
    """)

    yield conn

    # Teardown: Drop all tables
    cursor.execute("DROP TABLE IF EXISTS country_language, country_currency, country, language, currency")
    cursor.close()
    conn.close()

@pytest.fixture(autouse=True)
def clean_tables(db_connection):
    """Clear all tables before each test to ensure a clean state."""
    cursor = db_connection.cursor()
    cursor.execute("TRUNCATE TABLE country_language, country_currency, country, language, currency RESTART IDENTITY CASCADE")
    cursor.close()


@pytest.fixture
def mock_api():
    with requests_mock.Mocker() as m:
        yield m