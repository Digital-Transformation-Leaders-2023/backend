from fastapi import APIRouter, UploadFile, File
from io import BytesIO

import pandas as pd
import os

router = APIRouter(
    prefix='/api/v1/report'
)


@router.post('/')
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
