import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://qlikuser:qlikpassword@localhost:5432/qlikdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
