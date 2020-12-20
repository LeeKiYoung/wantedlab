import os

NAME = os.environ.get('DB_NAME').strip()
USER = os.environ.get('DB_USERNAME').strip()
PASSWORD = os.environ.get('DB_PASSWORD').strip()
HOST = os.environ.get('DB_HOST').strip()
PORT = os.environ.get('DB_PORT').strip()

SQLALCHEMY_DATABASE_URI = f'mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = False