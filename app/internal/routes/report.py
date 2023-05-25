from fastapi import APIRouter, UploadFile, File
from io import BytesIO
from app.internal.repository.report import ReportRepository

import pandas as pd

router = APIRouter(
    prefix='/api/v1/report'
)

report_repository = ReportRepository()


@router.post('/upload_file')
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))
    report_id = report_repository.create_upload_file(df, file.filename)
    return {"filename": report_id, "message": "File uploaded successfully"}


@router.get('/get_all_files')
async def get_all_files(limit: int = 10, skip: int = 0):
    return report_repository.get_all_files(limit, skip)


@router.get("/get_by_document_id/{document_id}")
async def get_by_document_id(document_id: str, limit: int = 10, skip: int = 0):
    return report_repository.get_file_by_id(document_id, limit, skip)


@router.post("set_favorite_by_file_id/{document_id}")
async def set_favorite_by_file_id(document_id: str, is_favorite: bool):
    report_repository.set_favorite_by_file_id(document_id, is_favorite)
    return {"file_id": document_id, "message": "Success, is_favorite field correctly changed"}
