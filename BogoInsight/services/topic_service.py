# BogoInsight/services/topic_service.py
from BogoInsight.models.topic import Topic
from BogoInsight.database.session import Session

class TopicService:
    @staticmethod
    def create_topic(topic):
        session = Session()
        session.add(topic)
        session.commit()
        session.refresh(topic)
        return topic

    @staticmethod
    def get_topic(id):
        session = Session()
        topic = session.query(Topic).get(id)
        return topic

    @staticmethod
    def get_topics(limit=None, offset=None):
        session = Session()
        topics = session.query(Topic).limit(limit).offset(offset).all()
        return topics

    @staticmethod
    def update_topic(id, topic_update):
        session = Session()
        topic = session.query(Topic).get(id)
        for key, value in topic_update.items():
            setattr(topic, key, value)
        session.commit()
        return topic

    @staticmethod
    def delete_topic(id):
        session = Session()
        topic = session.query(Topic).get(id)
        session.delete(topic)
        session.commit()