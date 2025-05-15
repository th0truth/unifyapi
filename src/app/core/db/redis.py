import redis.asyncio as aioredis

from core.logger import logger
from core.config import settings

class RedisClient:
    client: aioredis.Redis = None

    @classmethod
    async def connect(cls):
        """
        Create a connection to Redis cluster.
        """
        try:
            cls.client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                db=0
            )
            alive = await cls.client.ping()
            if not alive:
                logger.error(f"Couldn't connect to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}.")
                return None
            
            logger.info("Redis cluster connected")
            return cls.client
        except aioredis.ConnectionError as err:
            logger.error(
                {
                    "msg": "An error occured while connecting to Redis.",
                    "detail": err
                })
            return None

    @classmethod
    async def disconnect(cls):
        """
        Disconnect Redis cluster from API.
        """
        if cls.client:
            await cls.client.close()
            logger.info("Redis cluster disconnected")