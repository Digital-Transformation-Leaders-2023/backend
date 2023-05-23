import os
from io import BytesIO

from fastapi import FastAPI, File, UploadFile
import pandas as pd
from pymongo import MongoClient

import os
from dotenv import load_dotenv

from .database import Session, engine
from . import models

load_dotenv()

app = FastAPI()

mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_port = os.environ.get("MONGO_PORT", 27017)
mongo_user = os.environ.get("MONGO_USER", "myuser")
mongo_password = os.environ.get("MONGO_PASSWORD", "mypassword")
mongo_database = os.environ.get("MONGO_DATABASE", "mydatabase")

mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"

client = MongoClient(mongo_uri)

os.environ['DATABASE_URL'] = 'postgresql://user:password@db:5432/mydatabase'

def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


files = {}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # transform the XLSX file to a Pandas DataFrame
    df = pd.read_excel(BytesIO(contents))

    # создаем директорию "files", если ее нет
    if not os.path.exists('files'):
        os.makedirs('files')

    # сохраняем файл в директорию "files" с помощью Pandas
    file_name = os.path.join('files', file.filename)
    df.to_excel(file_name, index=False)

    record = df.to_dict(orient='records')

    db = client[mongo_database]
    collection = db['reports']

    collection.insert_many(record)

    print(df)

    return {"filename": file.filename, "message": "File uploaded successfully"}


@app.on_event("shutdown")
def shutdown_event():
    client.close()
