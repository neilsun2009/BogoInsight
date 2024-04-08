# BogoInsight/models/data_source.py
from sqlalchemy import Column, String, Integer, ForeignKey
from BogoInsight.database.base import BaseModel

class DataSource(BaseModel):
    __tablename__ = 'data_source'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    desc = Column(String(500))
    latest_version_id = Column(Integer, ForeignKey('data_version.id'))
    crawl_script_path = Column(String(200))
    auto_update_schedule = Column(String(50))
    tags = Column(String(200))
    default_args = Column(String(200))
    source_desc = Column(String(200))
    