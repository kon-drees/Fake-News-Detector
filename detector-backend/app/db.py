from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from app.core.config import Settings


class Database:
    """
    Manager for MongoDB connections and collection access.
    """

    _client: MongoClient = None

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _get_client(self) -> MongoClient:
        # Ensure a single connection is used across the instance.
        if self._client is None:
            self._client = MongoClient(self.settings.MONGO_URL)

        return self._client

    def get_articles_collection(self) -> Collection:
        db = self._get_client()[self.settings.MONGO_DB_NAME]

        return db["articles"]

    def close(self) -> None:
        if self._client:
            self._client.close()
