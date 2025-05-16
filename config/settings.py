import os 
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# -- Configuration -- #
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME','country_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD','password')
DB_PORT = os.getenv('DB_PORT', '5432')

API_URL = os.getenv('API_URL')