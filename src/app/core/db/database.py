from typing import Any, List, Dict
from bson.objectid import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
    AsyncIOMotorGridFSBucket
)

from core.config import settings
from core.logger import logger

class MongoDB:
    """
        `MongoDB` is a class instance for interacting with MongoDB cluster.\n
        We use `Motor` which presents a coroutine-based API for non-blocking access to MongoDB from `asyncio`.\n
        Read more:
            https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
    """

    client: AsyncIOMotorClient
    DATABASE_NAME: str
    COLLECTION_NAME: str

    @classmethod
    async def create(cls, doc: dict) -> Dict[str, Any]:
        """Create a document in the MongoDB collection."""
        collection = await cls.get_collection()
        d = collection.insert_one(doc)
        print(d)

    @classmethod
    async def find_many(cls, doc: dict | None = None, length: int | None = None, skip: int = 0) -> list[dict]:
        """Find all documents in the MongoDB collection."""
        collection = await cls.get_collection()
        cursor = collection.find(doc).to_list(length)
        return [j for j in await cursor][skip:]

    @classmethod
    async def find_by(cls, filter: dict | None = None) -> Dict[str, Any]:
        """Find a document by `filter` in the MongoDB collection."""
        collection = await cls.get_collection()
        return await collection.find_one(filter)
 
    @classmethod
    async def update_many(cls, filter: dict, update: dict):
        """Find documents by `filter` in the MongoDB collection."""
        collection = await cls.get_collection()
        collection.update_many(filter, update={"$set": update})

    @classmethod
    async def update_one(cls, filter: dict, update: dict):
        """Find a document by `filter` in the collection and update the document data."""
        collection = await cls.get_collection()
        collection.update_one(filter, {"$set": update})

    @classmethod
    async def delete_document_by(cls, filter: dict) -> bool:
        """Delete a document by 'filter' in the MongoDB collection."""
        collection = await cls.get_collection()
        collection.delete_one(filter)
    
    @classmethod
    async def upload_file(cls, filename: str, f_bytes: int, metadata: Any | None = None) -> ObjectId:
        """Upload a file to MongoDB database"""
        fs = await cls.get_gridfs()
        object_id = fs.upload_from_stream(
            filename, f_bytes, metadata={"type": metadata})
        return object_id
       
    @classmethod
    async def delete_file(cls, file_id: str):
        """Delete a file from MongoDB `fs.file` database."""
        fs = await cls.get_gridfs()
        fs.delete(file_id=file_id)

    @classmethod
    async def download_file(cls, filename: str):
        """Download a file from MongoDB `fs.file` database."""
        fs = await cls.get_gridfs()
        grid_out = await fs.open_download_stream_by_name(filename)
        f_bytes = await grid_out.read()
        with open(filename, "wb") as file:
            file.write(f_bytes)

    @classmethod
    async def get_databases(cls):
        """Get a list of MongoDB Cluster databases."""
        return await cls.client.list_database_names()

    @classmethod
    async def get_collections(cls) -> List[str]:
        """Get a list of database collections."""
        database = await cls.get_database()
        return await database.list_collection_names()

    @classmethod
    async def get_database(cls) -> AsyncIOMotorDatabase:
        """Get a database from the MongoDB Cluster."""
        return cls.client.get_database(name=cls.DATABASE_NAME)

    @classmethod
    async def get_collection(cls) -> AsyncIOMotorCollection:
        """Get a MongoDB database collection."""
        database = await cls.get_database()
        return database.get_collection(name=cls.COLLECTION_NAME)

    @classmethod
    async def get_gridfs(cls) -> AsyncIOMotorGridFSBucket:
        """Load GridFS for storing and retrieving files."""
        database = await cls.get_database()
        return AsyncIOMotorGridFSBucket(database=database, chunk_size_bytes=16)

    @classmethod
    async def __aenter__(cls) -> None:
        """Create a connection between API and MongoDB Cluster."""
        try:
            cls.client = AsyncIOMotorClient(
                f"mongodb+srv://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}.mongodb.net")
            logger.info("MongoDB cluster connected")
        except Exception as err:
            logger.error(err)
    
    @classmethod
    async def __aexit__(cls, exc_type, exc_val, exc_tb) -> None:
        """Disconnect MongoDB Cluster from API."""
        try:
            cls.client.close()
            logger.info("MongoDB cluster disconnected")
        except Exception as err:
            logger.error(err)