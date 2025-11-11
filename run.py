"""
Entry point for running the application.
This is a convenience script that can be used instead of: python -m app.main
"""
import uvicorn
from app.core.config import settings
from app.core.logging_config import logger

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )

