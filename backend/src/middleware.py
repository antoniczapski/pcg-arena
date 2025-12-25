"""
PCG Arena Backend - Request Logging Middleware
Protocol: arena/v0

Provides request correlation IDs and logging for all HTTP requests.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a correlation ID to each request and logs request details.
    
    Features:
    - Generates UUID for each request (request_id)
    - Logs: method, path, status_code, duration_ms, request_id
    - Adds X-Request-Id header to response
    - Stores request_id in request.state for use in handlers
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with logging.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain
            
        Returns:
            Response with X-Request-Id header
        """
        # Generate correlation ID
        request_id = str(uuid.uuid4())
        
        # Store in request state for use in handlers
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # If an exception occurs, we still want to log it
            duration_ms = (time.time() - start_time) * 1000
            status_code = 500
            logger.error(
                f"Request failed: method={request.method} path={request.url.path} "
                f"status_code={status_code} duration_ms={duration_ms:.2f} "
                f"request_id={request_id} error={type(e).__name__}: {str(e)}"
            )
            raise
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Get status code
        status_code = response.status_code
        
        # Extract session_id from request if present (for battles and votes)
        session_id = None
        if request.method == "POST":
            try:
                # Try to get session_id from request body if it was parsed
                if hasattr(request.state, "session_id"):
                    session_id = request.state.session_id
            except:
                pass
        
        # Log request details (S1-B4: Enhanced with session_id)
        log_msg = (
            f"Request: method={request.method} path={request.url.path} "
            f"status_code={status_code} duration_ms={duration_ms:.2f} "
            f"request_id={request_id}"
        )
        if session_id:
            log_msg += f" session_id={session_id}"
        
        logger.info(log_msg)
        
        # Add correlation ID to response headers
        response.headers["X-Request-Id"] = request_id
        
        return response

