# config.py
import os, random
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'PesaFresh.db')}")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    # postgresql://postgresadmin_ya5a_user:NnFXvMCy6a7ZEu9okhpW4ssiNykSmp8o@dpg-crnlrsl6l47c73ai61bg-a.oregon-postgres.render.com/postgresadmin_ya5a
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key" + str(random.randint(1, 1000000000)))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
