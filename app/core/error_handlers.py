"""
Global error handlers for FastAPI.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    ChatbotException,
    ThreadNotFoundError,
    PersonaNotFoundError,
    InvalidUserError,
    DatabaseError,
    LLMError,
    ConfigurationError
)
from app.core.logging_config import logger


async def chatbot_exception_handler(request: Request, exc: ChatbotException):
    """Handle custom chatbot exceptions."""
    status_code = 500
    detail = str(exc)
    
    if isinstance(exc, InvalidUserError):
        status_code = 400
    elif isinstance(exc, (ThreadNotFoundError, PersonaNotFoundError)):
        status_code = 404
    elif isinstance(exc, (DatabaseError, LLMError, ConfigurationError)):
        status_code = 500
    
    logger.error(f"ChatbotException: {detail}", exc_info=exc)
    
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "type": exc.__class__.__name__}
    )


def register_error_handlers(app):
    """Register error handlers with the FastAPI app."""
    app.add_exception_handler(ChatbotException, chatbot_exception_handler)
    app.add_exception_handler(InvalidUserError, chatbot_exception_handler)
    app.add_exception_handler(ThreadNotFoundError, chatbot_exception_handler)
    app.add_exception_handler(PersonaNotFoundError, chatbot_exception_handler)
    app.add_exception_handler(DatabaseError, chatbot_exception_handler)
    app.add_exception_handler(LLMError, chatbot_exception_handler)
    app.add_exception_handler(ConfigurationError, chatbot_exception_handler)

