# tests/test_load.py
import pytest
from Database.load import insert_data_to_db

def test_insert_data_to_db(db_connection):
    # Sample data matching the expected structure
    test_data = {
        "currencies": [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"}
        ],
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"}
        ],
        "countries": [
            {
                "cca2": "US",
                "name": "United States",
                "capital": "Washington, D.C.",
                "region": "Americas",
                "subregion": "North America",
                "population": 331000000,
                "area": 9833517.0
            },
            {
                "cca2": "ES",
                "name": "Spain",
                "capital": "Madrid",
                "region": "Europe",
                "subregion": "Southern Europe",
                "population": 47350000,
                "area": 505990.0
            }
        ],
        "country_currency": [
            {"country_cca2": "US", "currency_code": "USD"},
            {"country_cca2": "ES", "currency_code": "EUR"}
        ],
        "country_language": [
            {"country_cca2": "US", "language_code": "en"},
            {"country_cca2": "ES", "language_code": "es"}
        ]
    }

    # Call the function
    insert_data_to_db(db_connection, test_data)

    # Verify the data was inserted correctly
    cursor = db_connection.cursor()

    # Check currencies
    cursor.execute("SELECT code, name, symbol FROM currency ORDER BY code")
    currencies = cursor.fetchall()
    assert currencies == [
        ("EUR", "Euro", "€"),
        ("USD", "US Dollar", "$")
    ], f"Expected currencies did not match: {currencies}"

    # Check languages
    cursor.execute("SELECT code, name FROM language ORDER BY code")
    languages = cursor.fetchall()
    assert languages == [
        ("en", "English"),
        ("es", "Spanish")
    ], f"Expected languages did not match: {languages}"

    # Check countries
    cursor.execute("SELECT cca2, name, capital FROM country ORDER BY cca2")
    countries = cursor.fetchall()
    assert countries == [
        ("ES", "Spain", "Madrid"),
        ("US", "United States", "Washington, D.C.")
    ], f"Expected countries did not match: {countries}"

    # Check country_currency relationships
    cursor.execute("""
        SELECT c.cca2, cur.code
        FROM country_currency cc
        JOIN country c ON cc.country_id = c.id
        JOIN currency cur ON cc.currency_id = cur.id
        ORDER BY c.cca2
    """)
    country_currencies = cursor.fetchall()
    assert country_currencies == [
        ("ES", "EUR"),
        ("US", "USD")
    ], f"Expected country-currency relationships did not match: {country_currencies}"

    # Check country_language relationships
    cursor.execute("""
        SELECT c.cca2, l.code
        FROM country_language cl
        JOIN country c ON cl.country_id = c.id
        JOIN language l ON cl.language_id = l.id
        ORDER BY c.cca2
    """)
    country_languages = cursor.fetchall()
    assert country_languages == [
        ("ES", "es"),
        ("US", "en")
    ], f"Expected country-language relationships did not match: {country_languages}"

    cursor.close()