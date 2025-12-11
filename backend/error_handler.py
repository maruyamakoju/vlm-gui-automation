#!/usr/bin/env python3
"""
Unified Error Handling for VLM GUI Automation API

Provides consistent error response format across all endpoints.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# --- Error Response Models ---

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str  # Error code (e.g., "VALIDATION_ERROR", "INTERNAL_ERROR")
    message: str  # User-friendly error message
    details: Optional[Dict[str, Any]] = None  # Additional error context


class ErrorResponse(BaseModel):
    """Standardized error response format."""
    success: bool = False
    error: ErrorDetail
    timestamp: str  # ISO 8601 format


# --- Error Codes ---

class ErrorCode:
    """Standard error codes for the API."""

    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VLM_ERROR = "VLM_ERROR"
    GPT_ERROR = "GPT_ERROR"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


# --- Custom Exception Classes ---

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(APIError):
    """Validation error (400)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class NotFoundError(APIError):
    """Resource not found (404)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class InternalError(APIError):
    """Internal server error (500)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.INTERNAL_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class VLMError(APIError):
    """VLM processing error (500)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.VLM_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class NotImplementedError(APIError):
    """Feature not implemented (501)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.NOT_IMPLEMENTED,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            details=details
        )


# --- Error Response Builder ---

def create_error_response(
    code: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create standardized error response.

    Args:
        code: Error code from ErrorCode class
        message: User-friendly error message
        status_code: HTTP status code
        details: Optional additional error context

    Returns:
        JSONResponse with standardized error format
    """
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details
        ),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )


# --- Exception Handlers ---

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom APIError exceptions."""
    logger.error(f"API Error: {exc.code} - {exc.message}", exc_info=True)

    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors."""
    logger.warning(f"Validation Error: {exc.errors()}")

    return create_error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": exc.errors()}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return create_error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"exception_type": type(exc).__name__}
    )


# --- Register Handlers ---

def register_error_handlers(app):
    """
    Register all error handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Error handlers registered")
