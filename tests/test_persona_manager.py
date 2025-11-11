"""
Tests for persona manager.
"""
from app.utils.persona_manager import PersonaManager


def test_extract_persona_request():
    """Test persona extraction from messages."""
    assert PersonaManager.extract_persona_request("act like my mentor") == "mentor"
    assert PersonaManager.extract_persona_request("be an investor") == "investor"
    assert PersonaManager.extract_persona_request("switch to advisor") == "advisor"
    assert PersonaManager.extract_persona_request("back to my mentor thread") == "mentor"
    assert PersonaManager.extract_persona_request("Hello, how are you?") is None


def test_normalize_thread_name():
    """Test thread name normalization."""
    assert PersonaManager.normalize_thread_name("Mentor") == "mentor"
    assert PersonaManager.normalize_thread_name("Business Advisor") == "business_advisor"
    assert PersonaManager.normalize_thread_name("Investor!") == "investor"
    assert PersonaManager.normalize_thread_name("Test-Thread") == "testthread"


def test_get_persona_prompt():
    """Test persona prompt generation."""
    # Test with known persona
    prompt = PersonaManager.get_persona_prompt("mentor")
    assert "mentor" in prompt.lower()
    assert len(prompt) > 0
    
    # Test with unknown persona
    prompt = PersonaManager.get_persona_prompt("custom_persona")
    assert "custom_persona" in prompt.lower()
    assert len(prompt) > 0


def test_is_thread_switch_request():
    """Test thread switch detection."""
    assert PersonaManager.is_thread_switch_request("back to mentor") is True
    assert PersonaManager.is_thread_switch_request("switch to investor") is True
    assert PersonaManager.is_thread_switch_request("return to advisor") is True
    assert PersonaManager.is_thread_switch_request("Hello, how are you?") is False

