from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database
    DB_CONN_STR = os.environ.get('DB_CONN_STR')
    MODE = os.environ.get('MODE')
    DB_NAME = os.environ.get('DB_NAME_DEV')
    if MODE == 'PROD':
        DB_NAME = os.environ.get('DB_NAME_PROD')
    DB_NAME_TEST = os.environ.get('DB_NAME_TEST')

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')

    FLASK_ENV = os.environ.get('FLASK_ENV')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG')

    env = [DB_CONN_STR, MODE, DB_NAME, SECRET_KEY, FLASK_ENV, FLASK_DEBUG]
    for var in env:
        if var is None:
            raise ValueError('One or more environment variables are not set')
