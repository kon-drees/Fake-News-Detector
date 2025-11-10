from pymongo import MongoClient
from app.core.config import get_settings

settings = get_settings()

def get_client() -> MongoClient:
    return MongoClient(settings.MONGO_URL)

def get_articles_collection():
    client = get_client()
    db = client[settings.MONGO_DB_NAME]
    return db["articles"]