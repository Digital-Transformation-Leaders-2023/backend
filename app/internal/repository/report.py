import json
import os
import uuid

from datetime import datetime
from pymongo.errors import ConnectionFailure
from app.internal.model.report_filter import ReportFilter

from bson import json_util
from pandas import DataFrame

from app.internal.repository import mongo_db_client

database_name = "reports"


class ReportRepository:
    def __init__(self):
        self.__client = mongo_db_client
        self.__report_collection = self.__client["report_collection"]

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

        result = {}
        result['id'] = report_id
        result['date'] = datetime.now()
        result['total'] = data_frame.shape[0]
        result['list'] = records
        result['is_favorite'] = False

        self.__report_collection.insert_one(result)

        return report_id

    def get_all_files(self, limit: int = 10, skip: int = 0, is_favorite: bool = False):
        result = {}
        table_rows = []

        collection = self.__report_collection
        files_in_collection = [json.loads(json_util.dumps(doc, ensure_ascii=False))
                               for doc in collection.find()][skip: skip + limit]

        if files_in_collection:  # Если в коллекции есть файлы
            table_rows.extend(files_in_collection)  # Добавляем файлы напрямую в список

        filtered_rows = []
        for row in table_rows:
            if row['is_favorite'] == is_favorite:
                filtered_rows.append(row)

        result['reports'] = filtered_rows  # Присваиваем список файлов полю 'records'
        result['total_files'] = len(files_in_collection)

        return result

    def get_file_by_id(self, document_id: str, report_filter: ReportFilter):
        rows = json.loads(json_util.dumps(
            self.__report_collection.find_one({'id': document_id}),
            ensure_ascii=False
        ))
        rows['list'] = rows['list'][{}]
        rows['list'] = rows['list'][:report_filter.skip + report_filter.limit]
        return rows

    def set_favorite_by_file_id(self, document_id: str, is_favorite: bool):
        query = {"id": document_id}
        new_values = {"$set": {"is_favorite": is_favorite}}
        return self.__report_collection.update_one(query, new_values)
