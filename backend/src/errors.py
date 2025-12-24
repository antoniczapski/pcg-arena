"""
PCG Arena Backend - Error Handling
Protocol: arena/v0

Provides consistent error handling with standard error responses.
"""

from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from models import ErrorResponse, ErrorCode


class APIError(HTTPException):
    """
    Custom exception for API errors that will be handled by the global exception handler.
    
    This exception includes error code, message, retryable flag, and optional details.
    """
    def __init__(
        self,
        code: str,
        message: str,
        retryable: bool = False,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API error.
        
        Args:
            code: Error code (from ErrorCode enum or string)
            message: Human-readable error message
            retryable: Whether the error is retryable (default: False)
            status_code: HTTP status code (default: 400)
            details: Optional additional error details
        """
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details
        super().__init__(status_code=status_code, detail=message)


def raise_api_error(
    code: Union[str, ErrorCode],
    message: str,
    retryable: bool = False,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Raise an API error with standard format.
    
    This is a convenience function that raises an APIError exception,
    which will be caught by the global exception handler and converted
    to a standard ErrorResponse JSON.
    
    Args:
        code: Error code (use ErrorCode enum values or string)
        message: Human-readable error message
        retryable: Whether the error is retryable (default: False)
        status_code: HTTP status code (default: 400)
        details: Optional additional error details dictionary
    
    Raises:
        APIError: Always raises an APIError exception
    
    Example:
        raise_api_error(
            ErrorCode.BATTLE_NOT_FOUND,
            "Battle with ID 'btl_123' not found",
            retryable=False,
            status_code=404
        )
    """
    # Convert ErrorCode enum to string if needed
    code_str = code.value if isinstance(code, ErrorCode) else code
    
    raise APIError(
        code=code_str,
        message=message,
        retryable=retryable,
        status_code=status_code,
        details=details
    )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Global exception handler for APIError exceptions.
    
    Converts APIError exceptions into standard ErrorResponse JSON format.
    
    Args:
        request: FastAPI request object
        exc: The APIError exception that was raised
    
    Returns:
        JSONResponse with ErrorResponse format
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get request_id if available from middleware
    request_id = getattr(request.state, "request_id", None)
    request_id_str = f" request_id={request_id}" if request_id else ""
    
    logger.warning(
        f"APIError: code={exc.code} message={exc.message} "
        f"status_code={exc.status_code} path={request.url.path}{request_id_str}"
    )
    
    error_response = ErrorResponse.create(
        code=exc.code,
        message=exc.message,
        retryable=exc.retryable,
        details=exc.details
    )
    
    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )
    
    # Include request_id in response header if available
    if request_id:
        response.headers["X-Request-Id"] = request_id
    
    return response


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for standard FastAPI HTTPException.
    
    Converts HTTPException to standard ErrorResponse format.
    Used for validation errors and other HTTP exceptions.
    
    Args:
        request: FastAPI request object
        exc: The HTTPException that was raised
    
    Returns:
        JSONResponse with ErrorResponse format
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get request_id if available from middleware
    request_id = getattr(request.state, "request_id", None)
    request_id_str = f" request_id={request_id}" if request_id else ""
    
    # Determine error code based on status code
    if exc.status_code == 422:  # Validation error
        code = ErrorCode.INVALID_PAYLOAD
        retryable = False
    elif exc.status_code == 404:
        code = ErrorCode.BATTLE_NOT_FOUND
        retryable = False
    elif exc.status_code >= 500:
        code = ErrorCode.INTERNAL_ERROR
        retryable = True
    else:
        code = ErrorCode.INVALID_PAYLOAD
        retryable = False
    
    logger.warning(
        f"HTTPException: code={code} status_code={exc.status_code} "
        f"path={request.url.path}{request_id_str}"
    )
    
    error_response = ErrorResponse.create(
        code=code,
        message=str(exc.detail) if exc.detail else "An error occurred",
        retryable=retryable
    )
    
    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )
    
    # Include request_id in response header if available
    if request_id:
        response.headers["X-Request-Id"] = request_id
    
    return response


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unexpected exceptions.
    
    Catches any unhandled exceptions and converts them to INTERNAL_ERROR.
    This ensures all errors return the standard ErrorResponse format.
    
    Args:
        request: FastAPI request object
        exc: The exception that was raised
    
    Returns:
        JSONResponse with ErrorResponse format
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get request_id if available from middleware
    request_id = getattr(request.state, "request_id", None)
    request_id_str = f" request_id={request_id}" if request_id else ""
    
    # Log the full exception for debugging
    logger.exception(
        f"Unhandled exception: {exc} path={request.url.path}{request_id_str}"
    )
    
    error_response = ErrorResponse.create(
        code=ErrorCode.INTERNAL_ERROR,
        message="An internal error occurred",
        retryable=True
    )
    
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )
    
    # Include request_id in response header if available
    if request_id:
        response.headers["X-Request-Id"] = request_id
    
    return response

