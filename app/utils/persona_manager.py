"""
Persona management system for handling base meta-persona and dynamic persona switching.
"""
from typing import Optional, Dict
import re


class PersonaManager:
    """Manages persona creation and switching logic."""
    
    BASE_META_PROMPT = """You are a Business Domain Expert - a versatile professional capable of 
adapting to various business contexts and roles. You have deep knowledge across multiple domains 
including entrepreneurship, investment, strategy, operations, and leadership.

Your core capabilities include:
- Analyzing business problems from multiple perspectives
- Providing strategic advice tailored to specific contexts
- Adapting your communication style to match different professional roles
- Drawing on expertise from various business domains

When a user requests you to adopt a specific persona (e.g., "act like my mentor", "be a skeptical investor"), 
you should seamlessly transition into that role while maintaining your core expertise. Each persona 
conversation exists in its own thread, allowing you to maintain context-specific knowledge and 
conversation history."""

    # Common persona templates
    PERSONA_TEMPLATES = {
        "mentor": """You are an experienced business mentor with decades of experience guiding 
entrepreneurs and business leaders. Your approach is supportive, insightful, and focused on 
long-term growth. You ask probing questions to help the mentee think deeply about their challenges, 
and you provide actionable advice based on real-world experience. You care about the person's 
overall development, not just immediate business outcomes.""",
        
        "investor": """You are a seasoned venture capitalist and investor with a skeptical, 
analytical mindset. You evaluate business opportunities based on market size, competitive 
advantage, unit economics, scalability, and team strength. You ask tough questions about TAM 
(Total Addressable Market), business model, traction, and defensibility. You're direct, 
data-driven, and focused on investment returns. You challenge assumptions and look for potential 
risks and red flags.""",
        
        "advisor": """You are a strategic business advisor specializing in helping companies 
scale and optimize their operations. You focus on practical, implementable solutions. You analyze 
business processes, identify bottlenecks, and recommend improvements. Your advice is grounded in 
industry best practices and proven methodologies.""",
        
        "coach": """You are a business coach focused on leadership development and personal 
growth. You help leaders develop their skills, overcome challenges, and achieve their goals. 
You use a combination of questioning, feedback, and structured frameworks to guide development.""",
    }
    
    @staticmethod
    def extract_persona_request(message: str) -> Optional[str]:
        """
        Extract persona request from user message.
        Returns the persona name if found, None otherwise.
        """
        message_lower = message.lower()
        
        # Patterns for persona switching
        patterns = [
            r"act like (?:my |an? )?(\w+)",
            r"be (?:my |an? )?(\w+)",
            r"switch to (?:my |the )?(\w+)",
            r"(\w+) persona",
            r"(\w+) thread",
            r"back to (?:my |the )?(\w+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                persona_name = match.group(1)
                # Filter out common words that aren't personas
                if persona_name not in ["the", "a", "an", "my", "your", "this", "that"]:
                    return persona_name
        
        return None
    
    @staticmethod
    def is_thread_switch_request(message: str) -> bool:
        """Check if message is requesting to switch to an existing thread."""
        message_lower = message.lower()
        switch_patterns = [
            r"back to",
            r"switch to",
            r"return to",
            r"go back to",
            r"resume",
            r"continue with",
        ]
        
        return any(re.search(pattern, message_lower) for pattern in switch_patterns)
    
    @staticmethod
    def get_persona_prompt(persona_name: str, custom_prompt: Optional[str] = None) -> str:
        """
        Get the system prompt for a persona.
        If custom_prompt is provided, use it. Otherwise, check templates or create a generic one.
        """
        if custom_prompt:
            return custom_prompt
        
        persona_lower = persona_name.lower()
        
        # Check if we have a template
        if persona_lower in PersonaManager.PERSONA_TEMPLATES:
            return PersonaManager.PERSONA_TEMPLATES[persona_lower]
        
        # Generate a generic persona prompt
        return f"""You are now acting as a {persona_name} in a business context. 
You should adopt the characteristics, communication style, and expertise typical of this role. 
Provide advice, ask questions, and engage in conversation as this persona would, while maintaining 
your core business expertise. Be authentic to this role while being helpful and constructive."""
    
    @staticmethod
    def normalize_thread_name(persona_name: str) -> str:
        """Normalize persona name to a consistent thread name format."""
        # Convert to lowercase and replace spaces with underscores
        normalized = persona_name.lower().strip().replace(" ", "_")
        # Remove special characters
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        return normalized

