from pymongo import MongoClient
from dotenv import load_dotenv

import os

# init mongo configuration
# TODO: mongo_db client -> app.pkg
mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_port = os.environ.get("MONGO_PORT", 27017)
mongo_user = os.environ.get("MONGO_USER", "myuser")
mongo_password = os.environ.get("MONGO_PASSWORD", "mypassword")
mongo_database = os.environ.get("MONGO_DATABASE", "mydatabase")

mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"

client = MongoClient(mongo_uri)
