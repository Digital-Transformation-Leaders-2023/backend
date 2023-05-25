import os

from sqlalchemy import create_engine

DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://myuser:mypassword@localhost:5432/mydatabase')
engine = create_engine(DATABASE_URI)