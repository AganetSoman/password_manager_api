import os
from dotenv import load_dotenv

load_dotenv('.env')

USERNAME = os.getenv('USERID')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')
