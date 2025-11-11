"""
Custom exceptions for the application.
"""


class ChatbotException(Exception):
    """Base exception for all chatbot-related errors."""
    pass


class ThreadNotFoundError(ChatbotException):
    """Raised when a thread is not found."""
    pass


class PersonaNotFoundError(ChatbotException):
    """Raised when a persona is not found."""
    pass


class InvalidUserError(ChatbotException):
    """Raised when user_id is invalid or missing."""
    pass


class DatabaseError(ChatbotException):
    """Raised when a database operation fails."""
    pass


class LLMError(ChatbotException):
    """Raised when LLM operation fails."""
    pass


class ConfigurationError(ChatbotException):
    """Raised when configuration is invalid."""
    pass

