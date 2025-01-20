from core import exceptions
from core.config import settings
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection   
)
from typing import (
    Any, 
    List,
    Dict,
)

# motor docs: https://motor.readthedocs.io/en/stable/tutorial-asyncio.html

class MongoDB:
    client: AsyncIOMotorClient

    DATABASE_NAME: str
    COLLECTION_NAME: str

    @classmethod
    async def create(cls, doc: dict) -> Dict[str, Any]:
        """Create a document in the MongoDB collection."""
        collection = await cls.get_collection()
        collection.insert_one(doc)

    @classmethod
    async def find_all(cls, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
        """Find all documents in the MongoDB collection."""
        collection = await cls.get_collection()
        cursor = collection.find().to_list(length)
        return [j for j in await cursor][skip:]

    @classmethod
    async def find_by(cls, filter: Any | None = None) -> Dict[str, Any]:
        """Find a document by 'filter' in the MongoDB collection."""
        collection = await cls.get_collection()
        return await collection.find_one(filter)
 
    @classmethod
    async def find_one_and_update(cls, filter: dict | Any, update: dict | Any):
        collection = await cls.get_collection()
        return collection.find_one_and_update(filter, update)

    @classmethod
    async def delete_document_by(cls, filter: dict) -> bool:
        """Delete a document by 'filter' in the MongoDB collection."""
        collection = await cls.get_collection()
        collection.delete_one(filter)
  
    @classmethod
    async def count_documents(cls, filter: Any = {}) -> int:
        """Count of documents in the MongoDB collection."""
        collection = await cls.get_collection()
        return await collection.count_documents(filter)

    @classmethod
    async def get_databases(cls):
        return await cls.client.list_database_names()

    @classmethod
    async def get_collections(cls) -> List[str]:
        database = await cls.get_database()
        return await database.list_collection_names()

    @classmethod
    async def get_database(cls) -> AsyncIOMotorDatabase:
        """Get a MongoDB database."""
        try:
            return cls.client.get_database(name=cls.DATABASE_NAME)
        except Exception as err:
            raise exceptions.INTERNAL_SERVER_ERROR(detail=err)

    @classmethod
    async def get_collection(cls) -> AsyncIOMotorCollection:
        """Get a MongoDB database collection."""
        database = await cls.get_database()
        try:
            return database.get_collection(name=cls.COLLECTION_NAME)
        except Exception as err:
            raise exceptions.INTERNAL_SERVER_ERROR(detail=err)

    @classmethod
    def __enter__(cls) -> None:    
        """Create a connection between API and MongoDB Cluster"""
        try:
            cls.client = AsyncIOMotorClient(
                f"mongodb+srv://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}.mongodb.net")
        except Exception as err:
            raise exceptions.INTERNAL_SERVER_ERROR(detail=err)

    @classmethod
    def __exit__(cls, exc_type, exc_value, traceback) -> None:
        """Disconnect MongoDB Cluster from API"""
        cls.client.close()