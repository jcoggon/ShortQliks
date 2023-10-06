import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql+asyncpg://qlikuser:qlikpassword@postgres:5432/qlikdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'SQ123456789'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+asyncpg://qlikuser:qlikpassword@postgres:5432/qlikdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'SQ123456789'