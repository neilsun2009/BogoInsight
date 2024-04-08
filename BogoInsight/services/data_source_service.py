# BogoInsight/services/data_source_service.py
from sqlalchemy.orm import joinedload
from BogoInsight.models.data_source import DataSource
from BogoInsight.models.data_version import DataVersion
from BogoInsight.database.session import Session

class DataSourceService:
    @staticmethod
    def create_data_source(data_source):
        session = Session()
        session.add(data_source)
        session.commit()
        session.refresh(data_source)
        return data_source

    @staticmethod
    def get_data_source(id):
        session = Session()
        data_source = session.query(DataSource).options(joinedload(DataSource.latest_version)).get(id)
        return data_source

    @staticmethod
    def get_data_sources(limit=None, offset=None):
        session = Session()
        data_sources = session.query(DataSource).options(joinedload(DataSource.latest_version)).limit(limit).offset(offset).all()
        return data_sources

    @staticmethod
    def update_data_source(id, data_source_update):
        session = Session()
        data_source = session.query(DataSource).get(id)
        for key, value in data_source_update.items():
            setattr(data_source, key, value)
        session.commit()
        return data_source

    @staticmethod
    def delete_data_source(id):
        session = Session()
        data_source = session.query(DataSource).get(id)
        session.delete(data_source)
        session.commit()