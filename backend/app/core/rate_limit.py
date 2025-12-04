"""
Rate limiting middleware and utilities.
Uses in-memory storage for simplicity, but can be extended to use Redis.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict
import asyncio
from fastapi import Request, HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with in-memory storage.
    
    In production, replace with Redis-based implementation for
    distributed rate limiting across multiple instances.
    """
    
    def __init__(self):
        # Store: {key: {'tokens': int, 'last_update': datetime}}
        self._buckets: Dict[str, Dict] = defaultdict(
            lambda: {'tokens': 0, 'last_update': datetime.utcnow()}
        )
        self._lock = asyncio.Lock()
    
    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> Tuple[bool, int, int]:
        """
        Check if a request is allowed under rate limit.
        
        Args:
            key: Unique identifier (e.g., user_id, IP address)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (allowed, remaining_requests, reset_time_seconds)
        """
        async with self._lock:
            now = datetime.utcnow()
            bucket = self._buckets[key]
            
            # Calculate time since last update
            time_passed = (now - bucket['last_update']).total_seconds()
            
            # Replenish tokens based on time passed
            tokens_to_add = (time_passed / window_seconds) * max_requests
            bucket['tokens'] = min(max_requests, bucket['tokens'] + tokens_to_add)
            bucket['last_update'] = now
            
            # Check if request is allowed
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                remaining = int(bucket['tokens'])
                reset_seconds = int(window_seconds * (1 - bucket['tokens'] / max_requests))
                return True, remaining, reset_seconds
            else:
                # Calculate when bucket will have tokens again
                reset_seconds = int(window_seconds * (1 - bucket['tokens'] / max_requests))
                return False, 0, reset_seconds
    
    def _cleanup_old_buckets(self, max_age_seconds: int = 3600):
        """Remove old buckets to prevent memory leaks."""
        cutoff = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        keys_to_remove = [
            key for key, bucket in self._buckets.items()
            if bucket['last_update'] < cutoff
        ]
        for key in keys_to_remove:
            del self._buckets[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_rate_limit_key(request: Request, user_id: Optional[str] = None) -> str:
    """
    Generate a unique key for rate limiting.
    Uses user_id if available, otherwise falls back to IP.
    """
    if user_id:
        return f"user:{user_id}"
    
    # Get client IP from headers (handle proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    
    return f"ip:{ip}"


async def check_rate_limit(
    request: Request,
    user_id: Optional[str] = None,
    max_requests: Optional[int] = None,
    endpoint_type: str = "default"
) -> None:
    """
    Check rate limit and raise exception if exceeded.
    
    Args:
        request: FastAPI request object
        user_id: User ID if authenticated
        max_requests: Override default max requests
        endpoint_type: Type of endpoint (default, llm, etc.)
    """
    # Determine rate limit based on endpoint type
    if max_requests is None:
        if endpoint_type == "llm":
            max_requests = settings.RATE_LIMIT_LLM_PER_MINUTE
        else:
            max_requests = settings.RATE_LIMIT_PER_MINUTE
    
    key = get_rate_limit_key(request, user_id)
    allowed, remaining, reset_seconds = await rate_limiter.is_allowed(
        key, max_requests, window_seconds=60
    )
    
    # Add rate limit headers
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_reset = reset_seconds
    
    if not allowed:
        logger.warning(f"Rate limit exceeded for {key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": reset_seconds,
                "message": f"Too many requests. Please try again in {reset_seconds} seconds."
            },
            headers={
                "Retry-After": str(reset_seconds),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_seconds)
            }
        )


class RateLimitMiddleware:
    """
    Middleware for applying rate limits to all requests.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/docs", "/api/v1/openapi.json"]:
            await self.app(scope, receive, send)
            return
        
        # Get user ID from token if available
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload:
                    user_id = payload.get("sub")
            except:
                pass
        
        # Determine endpoint type for rate limiting
        endpoint_type = "default"
        if "/chat" in request.url.path or "/validation" in request.url.path:
            endpoint_type = "llm"
        
        # Check rate limit
        try:
            await check_rate_limit(request, user_id, endpoint_type=endpoint_type)
        except HTTPException as e:
            # Send 429 response
            response_headers = [
                (b"content-type", b"application/json"),
                (b"retry-after", str(e.headers.get("Retry-After", "60")).encode()),
            ]
            
            import json
            body = json.dumps(e.detail).encode()
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": response_headers,
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return
        
        await self.app(scope, receive, send)
