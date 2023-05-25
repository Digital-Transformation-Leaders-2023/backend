import json
import os
import uuid
from datetime import datetime

from bson import json_util
from pandas import DataFrame

from app.internal.repository import mongo_db_client


class ReportRepository:
    def __init__(self):
        self.__client = mongo_db_client

    def create_upload_file(self, data_frame: DataFrame, file_name: str):
        data_frame = data_frame.rename(columns={
            'ID пациента': 'patient_id',
            'Дата оказания услуги': 'date_of_service',
            'Дата рождения пациента': 'date_of_patient_birth',
            'Диагноз': 'diagnosis',
            'Должность': 'job_title',
            'Код МКБ-10': 'MKB_code',
            'Назначения': 'appointment',
            'Пол пациента': 'patient_gender',
        })

        # создаем директорию "files", если ее нет
        if not os.path.exists('files'):
            os.makedirs('files')

        # сохраняем файл в директорию "files" с помощью Pandas
        file_name = os.path.join('files', file_name)
        data_frame.to_excel(file_name, index=False)

        records = data_frame.to_dict(orient='records')

        report_id = uuid.uuid4()
        report_id = str(report_id)
        collection = self.__client[report_id]

        result = {}
        result['id'] = report_id
        result['date'] = datetime.now()
        result['total'] = data_frame.shape[0]
        result['list'] = records

        collection.insert_one(result)

        return report_id

    def get_all_files(self, limit: int = 10, skip: int = 0):
        all_data = {}

        # Получаем список всех коллекций в базе данных
        collection_names = self.__client.list_collection_names()

        # Проходимся по всем коллекциям и получаем все документы в каждой
        for collection_name in collection_names:
            collection = self.__client[collection_name]
            all_data[collection_name] = [json.loads(json_util.dumps(doc, ensure_ascii=False))
                                         for doc in collection.find()][skip: skip + limit]

        return all_data

    def get_file_by_id(self, document_id: str, limit: int = 10, skip: int = 0):
        rows = json.loads(json_util.dumps(self.__client.get_collection(document_id).find(), ensure_ascii=False))
        for row in rows:
            row['list'] = row['list'][:skip + limit]
        return rows
