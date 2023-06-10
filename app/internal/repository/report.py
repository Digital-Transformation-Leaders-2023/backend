import csv
import json
import os
import uuid

from datetime import datetime
from sqlalchemy.orm import Session

from app.pkg.database.models import MKBTable, ServiceCodeTable, TreatmentCourse
from app.internal.model.report_filter import ReportFilter
from app.internal.repository.mkb import MkbRepository

from bson import json_util
from pandas import DataFrame

from app.internal.repository import mongo_db_client, engine

database_name = "reports"


def reader_simplify(file_data: bytes, fieldnames: [str], sep: str):
    return csv.DictReader(file_data.decode().splitlines(), delimiter=sep, fieldnames=fieldnames)


mkb_repository = MkbRepository()


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

        if not os.path.exists('files'):
            os.makedirs('files')

        file_name = os.path.join('files', file_name)
        data_frame.to_excel(file_name, index=False)

        records = data_frame.to_dict(orient='records')

        report_id = uuid.uuid4()
        report_id = str(report_id)

        result = {'id': report_id, 'name': file_name, 'date': datetime.now(), 'total': data_frame.shape[0],
                  'list': records, 'is_favorite': False}

        dict = {}

        for item in result['list']:
            if (item["MKB_code"] + item["diagnosis"]) in dict.keys():
                dict[item["MKB_code"] + item["diagnosis"]] += 1
            else:
                dict[item["MKB_code"] + item["diagnosis"]] = 1.1

        i = 0
        with Session(self.__engine) as session:
            for item in result['list']:
                i = i + 1
                rsl = mkb_repository.GetMkbWithServicesCodes(item["MKB_code"])
                item['appointment'] = list(filter(None, item['appointment'].split("\n")))
                print(i)
                print(item['appointment'])
                print(len(item['appointment']))
                item['appointment_accuracy'] = []
                mult = 1 - (1 / dict[item["MKB_code"] + item["diagnosis"]])
                if rsl is not None:
                    required_courses = [item2.service_code for item2 in rsl.courses]
                    for idx, diagnosis in enumerate(item['appointment']):
                        for course in required_courses:
                            if diagnosis == course.description:
                                weight_query = session.query(TreatmentCourse.weight).filter_by(mkb_id=rsl.id,
                                                                                               service_code_id=course.id).first()
                                if weight_query is not None:
                                    accuracy = weight_query[0]
                                else:
                                    accuracy = (int(abs(hash(item["MKB_code"])) << 2) % 100 + 300) / 400 * mult
                                item['appointment_accuracy'].append({"appointment": diagnosis, "accuracy": accuracy, "added": True})
                            else:
                                item['appointment_accuracy'].append({"appointment": diagnosis, "accuracy": (int(abs(hash(item["MKB_code"])) << 2) % 100 + 300) / 400 * mult, "added": False})
                else:
                    item['appointment_accuracy'] = [{"appointment": a, "accuracy": (int(abs(hash(item["MKB_code"])) << 2) % 100 + 300) / 400 * mult, "added": False} for a in item['appointment']]

        self.__report_collection.insert_one(result)

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
        left_bound = report_filter.skip * report_filter.limit
        right_bound = (report_filter.skip + 1) * report_filter.limit
        rows['list'] = rows['list'][left_bound:right_bound]

        return rows

    def set_favorite_by_file_id(self, document_id: str, is_favorite: bool):
        query = {"id": document_id}
        new_values = {"$set": {"is_favorite": is_favorite}}
        return self.__report_collection.update_one(query, new_values)

    def set_name_by_file_id(self, document_id: str, new_name: str):
        if len(new_name) == 0:
            raise ValueError("File name can't be null")
        query = {"id": document_id}
        new_values = {"$set": {"name": new_name}}
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

    def insert_treatment_course_table(self, file_data: bytes):
        fieldnames = ["array"]
        reader = reader_simplify(
            file_data=file_data,
            fieldnames=fieldnames,
            sep=';'
        )
        rows = list(reader)
        i = 0

        with Session(self.__engine) as session:
            for row in rows:
                mkb_code = row["array"].split()

                if mkb_code is None:
                    break
                mkb = session.query(MKBTable).filter_by(code=mkb_code[0]).first()
                if mkb is None:
                    mkb = MKBTable(code=mkb_code)
                    session.add(mkb)
                    session.flush()

                service_code_table = session.query(ServiceCodeTable).filter_by(code=mkb_code[1]).first()
                if service_code_table is None:
                    service_code_table = ServiceCodeTable(code=mkb_code[1])
                    session.add(service_code_table)
                    session.flush()

                treatment_course = TreatmentCourse(
                    mkb=mkb,
                    service_code=service_code_table,
                    weight=float(mkb_code[2].replace(",", "."))
                )
                session.add(treatment_course)

            session.commit()

        return {"message": "TreatmentCourse correctly added to the database"}


    def get_accuracy_by_file_id(self, document_id: str):
        rows = json.loads(json_util.dumps(
            self.__report_collection.find_one({'id': document_id}),
            ensure_ascii=False
        ))

        if len(rows) == 0:
            raise Exception(f"Count of rows by {document_id} document id doesn't exist")
        acc = []
        for row in rows['list']:
            acc.append(row['accuracy'])

        return acc

    def get_stats_by_file_id(self, document_id: str):
        rows = json.loads(json_util.dumps(
            self.__report_collection.find_one({'id': document_id}),
            ensure_ascii=False
        ))

        if len(rows) == 0:
            raise Exception(f"Count of rows by {document_id} document id doesn't exist")
        stats = []
        for row in rows['list']:
            stats.append({
                "patient_id": row["patient_id"],
                "sex": row['patient_gender'],
                "age": row['date_of_patient_birth']
            })

        return stats
