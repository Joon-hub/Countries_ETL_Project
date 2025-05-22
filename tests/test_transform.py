# tests/test_transform.py
import pytest
import logging
from etl.transform import transform_country_data

@pytest.fixture
def sample_raw_data():
    return [
        {
            "cca2": "US",
            "name": {"common": "United States"},
            "capital": ["Washington, D.C."],
            "region": "Americas",
            "subregion": "North America",
            "population": 331000000,
            "area": 9833517.0,
            "currencies": {
                "USD": {"name": "US Dollar", "symbol": "$"}
            },
            "languages": {
                "en": "English"
            }
        },
        {
            "cca2": "ES",
            "name": {"common": "Spain"},
            "capital": ["Madrid"],
            "region": "Europe",
            "subregion": "Southern Europe",
            "population": 47350000,
            "area": 505990.0,
            "currencies": {
                "EUR": {"name": "Euro", "symbol": "€"}
            },
            "languages": {
                "es": "Spanish"
            }
        }
    ]

@pytest.mark.transform
def test_transform_country_data_valid(sample_raw_data):
    """Test transformation of valid country data."""
    result = transform_country_data(sample_raw_data)
    expected = {
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
        "currencies": [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"}
        ],
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"}
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
    assert result == expected, f"Transformation output did not match expected: {result}"

@pytest.mark.transform
@pytest.mark.parametrize(
    "raw_data, expected",
    [
        # Empty input
        (
            [],
            {
                "countries": [],
                "currencies": [],
                "languages": [],
                "country_currency": [],
                "country_language": []
            }
        ),
        # Country with missing cca2
        (
            [{"name": {"common": "Unknown"}, "capital": [None], "region": None, "subregion": None, "population": 0, "area": 0}],
            {
                "countries": [],
                "currencies": [],
                "languages": [],
                "country_currency": [],
                "country_language": []
            }
        ),
        # Country with missing currencies and languages
        (
            [{
                "cca2": "XX",
                "name": {"common": "Test Country"},
                "capital": ["Test Capital"],
                "region": "Test Region",
                "subregion": "Test Subregion",
                "population": 1000,
                "area": 1000.0,
                "currencies": {},
                "languages": {}
            }],
            {
                "countries": [{
                    "cca2": "XX",
                    "name": "Test Country",
                    "capital": "Test Capital",
                    "region": "Test Region",
                    "subregion": "Test Subregion",
                    "population": 1000,
                    "area": 1000.0
                }],
                "currencies": [],
                "languages": [],
                "country_currency": [],
                "country_language": []
            }
        ),
        # Country with missing currency name
        (
            [{
                "cca2": "XX",
                "name": {"common": "Test Country"},
                "capital": ["Test Capital"],
                "region": "Test Region",
                "subregion": "Test Subregion",
                "population": 1000,
                "area": 1000.0,
                "currencies": {"XXX": {"symbol": "X"}},
                "languages": {}
            }],
            {
                "countries": [{
                    "cca2": "XX",
                    "name": "Test Country",
                    "capital": "Test Capital",
                    "region": "Test Region",
                    "subregion": "Test Subregion",
                    "population": 1000,
                    "area": 1000.0
                }],
                "currencies": [],
                "languages": [],
                "country_currency": [],
                "country_language": []
            }
        )
    ]
)
def test_transform_country_data_edge_cases(raw_data, expected):
    """Test transformation with edge cases like empty input or missing data."""
    result = transform_country_data(raw_data)
    assert result == expected, f"Edge case transformation failed: {result}"

@pytest.mark.transform
def test_transform_country_data_deduplication(sample_raw_data):
    """Test deduplication of currencies and languages."""
    raw_data = sample_raw_data + [
        {
            "cca2": "CA",
            "name": {"common": "Canada"},
            "capital": ["Ottawa"],
            "region": "Americas",
            "subregion": "North America",
            "population": 38000000,
            "area": 9984670.0,
            "currencies": {
                "USD": {"name": "US Dollar", "symbol": "$"}  # Duplicate USD
            },
            "languages": {
                "en": "English"  # Duplicate English
            }
        }
    ]
    result = transform_country_data(raw_data)
    assert len(result["currencies"]) == 2, f"Expected 2 unique currencies, got {len(result['currencies'])}"
    assert len(result["languages"]) == 2, f"Expected 2 unique languages, got {len(result['languages'])}"
    assert result["currencies"] == [
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"}
    ]
    assert result["languages"] == [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"}
    ]
    assert len(result["country_currency"]) == 3, f"Expected 3 country-currency pairs, got {len(result['country_currency'])}"
    assert len(result["country_language"]) == 3, f"Expected 3 country-language pairs, got {len(result['country_language'])}"

@pytest.mark.transform
def test_transform_country_data_logging(caplog, sample_raw_data):
    """Test logging behavior during transformation."""
    caplog.set_level(logging.INFO)
    transform_country_data(sample_raw_data)
    assert "starting data transformation" in caplog.text
    assert "Transformation complete. Found 2 countries, 2 unique currencies, and 2 unique languages." in caplog.text

@pytest.mark.transform
def test_transform_country_data_missing_cca2_warning(caplog, sample_raw_data):
    """Test warning log for missing cca2."""
    caplog.set_level(logging.WARNING)
    raw_data = sample_raw_data + [{"name": {"common": "Unknown"}}]
    transform_country_data(raw_data)
    assert "Skipping country with missing cca2: Unknown" in caplog.text