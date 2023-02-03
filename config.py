from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database
    DB_CONN_STR = os.environ.get('DB_CONN_STR')
    DB_NAME = os.environ.get('DB_NAME')

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
