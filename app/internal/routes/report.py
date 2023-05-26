from fastapi import APIRouter, UploadFile, File, Depends
from io import BytesIO
from app.internal.repository.report import ReportRepository
from app.internal.model.report_filter import ReportFilter

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
async def get_all_files(limit: int = 10, skip: int = 0, is_favorite: bool = False):
    return report_repository.get_all_files(limit, skip, is_favorite)


@router.get("/get_by_document_id/{document_id}")
async def get_by_document_id(
        document_id: str,
        report_filter: ReportFilter = Depends(ReportFilter)
):
    return report_repository.get_file_by_id(document_id, report_filter)


@router.post("/set_favorite_by_file_id/{document_id}")
async def set_favorite_by_file_id(document_id: str, is_favorite: bool):
    report_repository.set_favorite_by_file_id(document_id, is_favorite)
    return {"file_id": document_id, "message": "Success, is_favorite field correctly changed"}
