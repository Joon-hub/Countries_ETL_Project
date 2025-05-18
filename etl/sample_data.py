import requests
import json
import os
from dotenv import load_dotenv

# Define the API endpoint URL
API_URL = os.getenv('API_URL')

def fetch_all_countries_data(url):
    """
    Fetches data for all countries from the REST countries API 
    and returns a list of dictionaries.
    """
    print("Attempting to fetch data from: {url}")
    try:
        response = requests.get(url)
        data = response.json()
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
    
# -- Main Execution -- #

if __name__ == "__main__":
    country_data = fetch_all_countries_data(API_URL)
    if country_data:
        print('length of data: ', len(country_data))
        if country_data:
            print("\n --- structure of first country object ---")
            print(json.dumps(country_data[0], indent=4))
            print("\n--- End of structure of first country object ---")
        else:
            print(" fetched data is empty. ")
    else:
        print("failed to fetch the print data. ")

