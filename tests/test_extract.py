from etl.extract import fetch_all_countries_data
import pytest

def test_fetch_all_countries_data():
    url = "https://restcountries.com/v3.1/all"
    data = fetch_all_countries_data(url)
    assert isinstance(data, list)  # Check if data is a list
    assert len(data) > 0           # Check if data is not empty