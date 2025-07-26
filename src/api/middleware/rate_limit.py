from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests per client IP."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 3600):
        """Initialize the middleware with rate limit settings."""
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: defaultdict[str, list[datetime]] = defaultdict(list)

    async def dispatch(self, request, call_next):
        """Apply rate limiting to all requests based on client IP."""
        client_ip = request.client.host
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > window_start
        ]
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
            )

        self.requests[client_ip].append(now)

        return await call_next(request)
