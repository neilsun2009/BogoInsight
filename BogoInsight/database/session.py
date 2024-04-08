# BogoInsight/database/session.py
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from BogoInsight.database.base import Base  # Import your Base from models
from BogoInsight.utils.logger import logger
from BogoInsight.models import ( 
    # Import all of your models, so that they can be created all at once
    data_source,
    data_version,
    topic,
)


DATABASE_URL = f"mysql+mysqlconnector://root:{os.getenv('MYSQL_ROOT_PASSWORD')}@db:3306/bogo_insight"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created.")
    except OperationalError as e:
        logger.error("Error occurred during Table creation!")
        logger.error(e)

create_tables()