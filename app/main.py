import os
from io import BytesIO

from fastapi import FastAPI, File, UploadFile
import pandas as pd

app = FastAPI()


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

    print(df)

    return {"filename": file.filename, "message": "File uploaded successfully"}
