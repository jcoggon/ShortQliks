import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+asyncpg://qlikuser:qlikpassword@postgres:5432/qlikdb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'SQ123456789')

class TestingConfig(Config):
    TESTING = True
    # You can specify a different database URI for testing if needed
    # SQLALCHEMY_DATABASE_URI = 'your_testing_database_uri'
