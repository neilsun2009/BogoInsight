# BogoInsight/models/topic.py
from sqlalchemy import Column, String, Integer
from BogoInsight.database.base import BaseModel

class Topic(BaseModel):
    __tablename__ = 'topic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    desc = Column(String(500))
    icon = Column(String(10))
    file_path = Column(String(200))
    tags = Column(String(200))
    order_num = Column(Integer)