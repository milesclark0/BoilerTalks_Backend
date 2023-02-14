from dotenv import load_dotenv
from datetime import timedelta
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

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_SAMESITE = 'None'
    JWT_COOKIE_SECURE = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


    env = [DB_CONN_STR, MODE, DB_NAME, SECRET_KEY, FLASK_ENV, FLASK_DEBUG, JWT_SECRET_KEY]
    for var in env:
        if var is None:
            raise ValueError('One or more environment variables are not set')
