from core.config import settings
from core.logger import logger
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection
)
from core import exc
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
    async def find_many(cls, filter: str | None = None, value: Any = None, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
        """Find all documents in the MongoDB collection."""
        collection = await cls.get_collection()
        cursor = collection.find({filter: value} if filter and value else None).to_list(length)
        return [j for j in await cursor][skip:]

    @classmethod
    async def find_by(cls, filter: dict | None = None) -> Dict[str, Any]:
        """Find a document by 'filter' in the MongoDB collection."""
        collection = await cls.get_collection()
        return await collection.find_one(filter)
 
    @classmethod
    async def update_many(cls, filter: dict, update: dict):
        """Find documents by 'filter' in the MongoDB collection."""
        collection = await cls.get_collection()
        collection.update_many(filter, update={"$set": update})

    @classmethod
    async def update_one(cls, filter: dict, update: dict):
        """Find a document by 'filter' in the collection and update the document data."""
        collection = await cls.get_collection()
        collection.update_one(filter, {"$set": update})

    @classmethod
    async def delete_document_by(cls, filter: dict) -> bool:
        """Delete a document by 'filter' in the MongoDB collection."""
        collection = await cls.get_collection()
        collection.delete_one(filter)
  
    @classmethod
    async def count_documents(cls, filter: dict = {}) -> dict | int:
        """Count of documents in the MongoDB collection."""
        result = {}
        collection = await cls.get_collection()
        for key, value in filter.items():
            if isinstance(value, list):
                for j in value:
                    result.update({j: await collection.count_documents({key: j})})
            else:
                result = await collection.count_documents({key: value})
        return result

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
            raise exc.INTERNAL_SERVER_ERROR(detail=err)

    @classmethod
    async def get_collection(cls) -> AsyncIOMotorCollection:
        """Get a MongoDB database collection."""
        database = await cls.get_database()
        try:
            return database.get_collection(name=cls.COLLECTION_NAME)
        except Exception as err:
            raise exc.INTERNAL_SERVER_ERROR(detail=err)

    @classmethod
    def __enter__(cls) -> None:    
        """Create a connection between API and MongoDB Cluster"""
        try:
            cls.client = AsyncIOMotorClient(
                f"mongodb+srv://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}.mongodb.net")
            logger.info("MongoDB Cluster connected")
        except Exception as err:
            logger.error(err)
            raise exc.INTERNAL_SERVER_ERROR(detail=err)

    @classmethod
    def __exit__(cls, exc_type, exc_value, traceback) -> None:
        """Disconnect MongoDB Cluster from API"""
        cls.client.close()
        logger.info("MongoDB Cluster disconnected")