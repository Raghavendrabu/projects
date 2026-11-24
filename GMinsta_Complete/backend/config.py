import os
from datetime import timedelta
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'gminsta')
    SECRET_KEY = os.getenv('SECRET_KEY', 'my-secret-key')
    JWT_EXPIRATION_DELTA = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))