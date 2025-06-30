from typing import Optional
import redis.asyncio as aioredis

from core.logger import logger
from core.config import settings

class RedisClient:
    _instance: Optional["RedisClient"] = None
    _client: Optional[aioredis.Redis] = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def connect(cls):
        """
        Establish Redis connection.
        """
        try:
            cls._client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                db=settings.REDIS_DB
            )
            alive = await cls._client.ping()
            if not alive:
                logger.error(f"Couldn't connect to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}.")
                return None
            logger.info("[+] Successfully connected to Redis.")
            return cls._client
        except aioredis.ConnectionError as err:
            logger.error({ "msg": "An error occured while connecting to Redis.", "detail": err})
            return None

    @classmethod
    async def close(cls):
        """
        Close Redis connection.
        """
        if cls._client is not None:
            try:
                await cls._client.aclose()
                logger.info("[+] Redis connection closed.")
            except Exception as err:
                logger.error({"msg": "[x] Error closing Redis connection.", "detail": err})
            finally:
                cls._client = None
