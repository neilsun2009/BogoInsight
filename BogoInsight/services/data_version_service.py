# BogoInsight/services/data_version_service.py
from BogoInsight.models.data_version import DataVersion
from BogoInsight.database.session import Session

class DataVersionService:
    @staticmethod
    def create_data_version(data_version):
        session = Session()
        session.add(data_version)
        session.commit()
        session.refresh(data_version)
        return data_version

    @staticmethod
    def get_data_version(id):
        session = Session()
        data_version = session.query(DataVersion).get(id)
        return data_version

    @staticmethod
    def get_data_versions(limit=None, offset=None):
        session = Session()
        data_versions = session.query(DataVersion).limit(limit).offset(offset).all()
        return data_versions

    @staticmethod
    def update_data_version(id, data_version_update):
        session = Session()
        data_version = session.query(DataVersion).get(id)
        for key, value in data_version_update.items():
            setattr(data_version, key, value)
        session.commit()
        return data_version

    @staticmethod
    def delete_data_version(id):
        session = Session()
        data_version = session.query(DataVersion).get(id)
        session.delete(data_version)
        session.commit()