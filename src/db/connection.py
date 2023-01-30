import imp, json, pdb, sys, os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from models.staff_models import user_request_schemas, user_table_schema

load_dotenv()  # take the environment variables from .env file.
# local connection
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_SSL_MODE = os.getenv('DB_SSL_MODE')

connection_string = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

