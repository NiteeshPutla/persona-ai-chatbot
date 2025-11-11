"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User's message")
    thread_name: Optional[str] = Field(None, description="Optional thread name to use")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    thread_name: str = Field(..., description="Thread name used for this conversation")
    thread_id: int = Field(..., description="Thread ID")


class MessageSchema(BaseModel):
    """Schema for a single message."""
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class ThreadSchema(BaseModel):
    """Schema for a thread with its messages."""
    thread_id: int
    persona_prompt: str
    created_at: Optional[str]
    updated_at: Optional[str]
    messages: List[MessageSchema]


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history endpoint."""
    user_id: str
    threads: Dict[str, ThreadSchema] = Field(..., description="Threads organized by thread name")

