import logging
import requests

# --- Extraction from API --- #
    
def fetch_all_countries_data(url):
    """
    Fetches data for all countries from the REST countries API 
    and returns a list of dictionaries.
    """
    logging.info(f"Attempting to fetch data from: {url}")
    try:
        # get request
        response = requests.get(url)
        
        # check if request is successfull
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        # parse json response
        data = response.json()
        return data
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None