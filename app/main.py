import uuid
from io import BytesIO
from dotenv import load_dotenv
from bson import json_util
from fastapi import FastAPI, File, UploadFile
from pymongo import MongoClient

import pandas as pd
import os
import locale
import json

load_dotenv()

app = FastAPI()

mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_port = os.environ.get("MONGO_PORT", 27017)
mongo_user = os.environ.get("MONGO_USER", "myuser")
mongo_password = os.environ.get("MONGO_PASSWORD", "mypassword")
mongo_database = os.environ.get("MONGO_DATABASE", "mydatabase")

mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"

client = MongoClient(mongo_uri)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


files = {}
db = client[mongo_database]

@app.post("/upload_file/")
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

    report_id = uuid.uuid4()
    report_id = str(report_id)

    collection = db[report_id]

    collection.insert_many(record)

    return {"filename": report_id, "message": "File uploaded successfully"}

@app.get("/get_all_data")
async def get_all_data():
    all_data = {}

    # Получаем список всех коллекций в базе данных
    collection_names = db.list_collection_names()

    # Проходимся по всем коллекциям и получаем все документы в каждой
    for collection_name in collection_names:
        collection = db[collection_name]
        all_data[collection_name] = [json.loads(json_util.dumps(doc, ensure_ascii=False))
                                     for doc in collection.find()]

    return all_data

@app.get("/get_by_document_id/{document_id}")
async def get_all_data(document_id: str):
    return json.loads(json_util.dumps(db.get_collection(document_id).find(), ensure_ascii=False))

@app.on_event("shutdown")
def shutdown_event():
    client.close()