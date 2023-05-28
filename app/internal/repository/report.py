import csv
import json
import os
import uuid

from datetime import datetime
from sqlalchemy.orm import Session

from app.pkg.database.models import MKBTable, ServiceCodeTable
from app.internal.model.report_filter import ReportFilter

from bson import json_util
from pandas import DataFrame

from datetime import date

from app.internal.repository import mongo_db_client, engine

database_name = "reports"


def reader_simplify(file_data: bytes, fieldnames: [str], sep: str):
    return csv.DictReader(file_data.decode().splitlines(), delimiter=sep, fieldnames=fieldnames)


class ReportRepository:
    def __init__(self):
        self.__client = mongo_db_client
        self.__report_collection = self.__client["report_collection"]
        self.__engine = engine

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

        # ВОТ ТУТ ВАЛИДАЦИЯ!
        # try:
        #     # проверить есть ли КОД МКБ-10 в таблице
        #     with Session(self.__engine) as session:
        #         query = session.query(MKBTable.code) \
        #             .filter(~MKBTable.code.in_(data_frame['MKB_code'])) \
        #             .distinct()
        #         result = query.all()
        #         if len(result) > 0:
        #             print(result)
        # except:
        #     raise Exception("Something went wrong with PostgreSql connection")

        return report_id

    def get_all_files(
            self,
            limit: int = 10,
            skip: int = 1,
            is_favorite: bool = False,
            fiter: ReportFilter = ReportFilter()
    ):
        result = {}
        table_rows = []

        collection = self.__report_collection
        files = [json.loads(json_util.dumps(doc, ensure_ascii=False))
                 for doc in collection.find()]

        files_in_collection = files[skip: skip + limit]

        if files_in_collection:
            table_rows.extend(files_in_collection)

        filtered_rows = []
        for row in files_in_collection:
            if row['is_favorite'] == is_favorite:
                filtered_rows.append(row)

        result['reports'] = filtered_rows
        result['total_files'] = len(files)

        return result

    @staticmethod
    def __predicate(key, fltr: ReportFilter):
        # age = date.today().year - date(key["date_of_patient_birth"]).year
        if key["patient_gender"] != fltr.sex and fltr.sex is not None:
            return False
        if key["MKB_code"] != fltr.mkb_code and fltr.mkb_code is not None:
            return False
        return True

    def get_file_by_id(self, document_id: str, report_filter: ReportFilter):
        rows = json.loads(json_util.dumps(
            self.__report_collection.find_one({'id': document_id}),
            ensure_ascii=False
        ))

        rows['list'] = [k for k in rows['list'] if self.__predicate(k, report_filter)]
        rows['list'] = rows['list'][:report_filter.skip + report_filter.limit]

        return rows

    def set_favorite_by_file_id(self, document_id: str, is_favorite: bool):
        query = {"id": document_id}
        new_values = {"$set": {"is_favorite": is_favorite}}
        return self.__report_collection.update_one(query, new_values)

    def insert_MKB_table(self, file_data: bytes):
        fieldnames = ["code", "description"]
        reader = reader_simplify(
            file_data=file_data,
            fieldnames=fieldnames,
            sep=','
        )
        rows = list(reader)
        try:
            with Session(self.__engine) as session:
                session.bulk_insert_mappings(MKBTable, rows)
                session.commit()
                session.close()
            return {"message": "MKBTable correctly add in base"}
        except Exception as error:
            raise error

    def insert_service_code_table(self, file_data: bytes):
        fieldnames = ["code", "description"]
        reader = reader_simplify(
            file_data=file_data,
            fieldnames=fieldnames,
            sep=';'
        )
        rows = list(reader)
        try:
            with Session(self.__engine) as session:
                session.bulk_insert_mappings(ServiceCodeTable, rows)
                session.commit()
                session.close()
            return {"message": "ServiceCode correctly add in base"}
        except Exception as error:
            raise error
