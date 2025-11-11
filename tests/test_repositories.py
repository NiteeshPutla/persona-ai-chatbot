"""
Tests for repository layer.
"""
import pytest
from app.repositories.thread_repository import ThreadRepository
from app.core.exceptions import DatabaseError, ThreadNotFoundError


def test_create_thread(repository):
    """Test thread creation."""
    thread = repository.create_thread(
        user_id="test_user",
        thread_name="mentor",
        persona_prompt="You are a mentor."
    )
    
    assert thread.id is not None
    assert thread.user_id == "test_user"
    assert thread.thread_name == "mentor"
    assert thread.persona_prompt == "You are a mentor."


def test_get_thread(repository, sample_thread):
    """Test retrieving a thread."""
    thread = repository.get_thread("test_user", "mentor")
    
    assert thread is not None
    assert thread.user_id == "test_user"
    assert thread.thread_name == "mentor"


def test_get_thread_not_found(repository):
    """Test retrieving a non-existent thread."""
    thread = repository.get_thread("test_user", "nonexistent")
    assert thread is None


def test_get_thread_by_id(repository, sample_thread):
    """Test retrieving a thread by ID."""
    thread = repository.get_thread_by_id(sample_thread.id)
    
    assert thread is not None
    assert thread.id == sample_thread.id


def test_get_thread_by_id_not_found(repository):
    """Test retrieving a thread by non-existent ID."""
    with pytest.raises(ThreadNotFoundError):
        repository.get_thread_by_id(99999)


def test_add_message(repository, sample_thread):
    """Test adding a message to a thread."""
    message = repository.add_message(
        thread_id=sample_thread.id,
        role="user",
        content="Hello, mentor!"
    )
    
    assert message.id is not None
    assert message.thread_id == sample_thread.id
    assert message.role == "user"
    assert message.content == "Hello, mentor!"


def test_get_thread_messages(repository, sample_thread):
    """Test retrieving messages from a thread."""
    # Add some messages
    repository.add_message(sample_thread.id, "user", "Hello")
    repository.add_message(sample_thread.id, "assistant", "Hi there!")
    repository.add_message(sample_thread.id, "user", "How are you?")
    
    messages = repository.get_thread_messages(sample_thread.id)
    
    assert len(messages) == 3
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi there!"
    assert messages[2].content == "How are you?"


def test_get_most_recent_thread(repository):
    """Test getting the most recent thread."""
    # Create multiple threads
    thread1 = repository.create_thread("test_user", "mentor", "Mentor prompt")
    thread2 = repository.create_thread("test_user", "investor", "Investor prompt")
    
    # Add a message to thread2 to make it more recent
    repository.add_message(thread2.id, "user", "Test")
    
    recent = repository.get_most_recent_thread("test_user")
    
    assert recent is not None
    assert recent.thread_name == "investor"


def test_get_user_chat_history(repository):
    """Test retrieving user chat history."""
    # Create threads and messages
    thread1 = repository.create_thread("test_user", "mentor", "Mentor prompt")
    thread2 = repository.create_thread("test_user", "investor", "Investor prompt")
    
    repository.add_message(thread1.id, "user", "Hello mentor")
    repository.add_message(thread2.id, "user", "Hello investor")
    
    history = repository.get_user_chat_history("test_user")
    
    assert "mentor" in history
    assert "investor" in history
    assert len(history["mentor"]["messages"]) == 1
    assert len(history["investor"]["messages"]) == 1

