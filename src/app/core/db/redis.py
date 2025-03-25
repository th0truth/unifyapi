import redis.asyncio as aioredis

from core.config import settings
from core.logger import logger

class Redis:
    def __init__(
            self,
            db: str | int,
            protocol: int = 2
        ) -> aioredis.Redis:
        self.db = db
        self.protocol = protocol

    async def __aenter__(self) -> aioredis.Redis:
        """Create a connection to Redis cluster."""
        try:
            self.client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                protocol=self.protocol,
                decode_responses=True,
                db=self.db,
            )
            alive = await self.client.ping()
            if not alive:
                logger.error(f"Couldn't connect to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}.")
            logger.info("Redis cluster connected")
            return self.client
        except aioredis.ConnectionError:
            logger.error("An error occured while connecting to Redis.")

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Disconnect Redis cluster from API."""
        await self.client.close()
        logger.info("Redis cluster disconnected")