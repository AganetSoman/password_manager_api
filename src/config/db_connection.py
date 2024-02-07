from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from src.env_config import USERNAME, PASSWORD, HOST, DATABASE

connection_string = URL.create(
    'postgresql',
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    database=DATABASE,
)

engine = create_engine(connection_string)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()
