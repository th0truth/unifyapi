from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, status 
from datetime import datetime, timezone
from fastapi.responses import Response
from fastapi import Request
from starlette.types import ASGIApp
import hashlib
import json

from core.db import RedisClient

class DeviceLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract info device
        local_IP_address = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")
        timestamp = datetime.now(timezone.utc)

        # Create a unique device identifier
        device_id = hashlib.sha256(f"{local_IP_address}{user_agent}".encode()).hexdigest()

        # Data to store
        device_data = {
            "device_id": device_id,
            "ip_address": {
                "local": local_IP_address,
            },
            "user_agent": user_agent,
            "timestamp": timestamp.isoformat(),
            "endpoint": str(request.url.path) 
        }

        # Store in Redis
        await RedisClient._client.setex(f"logs:{device_id}:{timestamp.strftime('%Y-%m-%d %H.%M.%S')}", 3600, json.dumps(device_data))

        # Rate limiting
        rate_limit_key = f"ratelimit:{device_id}"
        count = await RedisClient._client.incr(rate_limit_key)
        if count:
            await RedisClient._client.expire(rate_limit_key, 60)
        if count > 100:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded."
            )
        
        response = await call_next(request)
        return response