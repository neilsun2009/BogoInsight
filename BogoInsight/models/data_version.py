# BogoInsight/models/data_version.py
from sqlalchemy import Column, String, Integer
from BogoInsight.database.base import BaseModel

class DataVersion(BaseModel):
    __tablename__ = 'data_version'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    args = Column(String(200))
    file_path = Column(String(200))