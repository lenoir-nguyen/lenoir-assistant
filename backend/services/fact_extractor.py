import re
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Fact:
    """Represents an extracted fact from user message."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""  # "event", "personal_preference", "contact", "habit"
    content: str = ""  # The extracted fact text
    raw_statement: str = ""  # Original user text where fact was found
    created_at: datetime = field(default_factory=datetime.utcnow)


class FactExtractor:
    """Extract facts from user messages using pattern matching."""

    # Regex patterns for different types of facts
    PATTERNS = [
        # Personal attributes: "My X is Y"
        (r"My\s+(\w+)\s+is\s+(.+?)(?:\.|,|!|\?|$)", "personal_preference", "My {0} is {1}"),

        # Preferences: "I like X"
        (r"I\s+like\s+(.+?)(?:\.|,|!|\?|$)", "personal_preference", "I like {0}"),

        # Favorite: "My favorite X is Y"
        (r"My\s+favorite\s+(\w+)\s+is\s+(.+?)(?:\.|,|!|\?|$)", "personal_preference", "My favorite {0} is {1}"),

        # Contact info: "My X is Y" (phone, email, address)
        (r"My\s+(phone|email|address|number|website)\s+is\s+(.+?)(?:\.|,|!|\?|$)", "contact", "My {0} is {1}"),

        # Name: "You can call me X" or "Call me X"
        (r"(?:You\s+can\s+)?[Cc]all\s+me\s+(\w+)", "personal_preference", "You can call me {0}"),

        # Work/Job: "I work at X"
        (r"I\s+work\s+at\s+(.+?)(?:\.|,|!|\?|$)", "contact", "I work at {0}"),

        # Job title: "I'm a X"
        (r"I'm\s+a\s+(.+?)(?:\.|,|!|\?|$)", "contact", "I'm a {0}"),

        # Possession: "I have X"
        (r"I\s+have\s+a?\s+(.+?)(?:\.|,|!|\?|$)", "personal_preference", "I have {0}"),

        # Activities: "I do X"
        (r"I\s+do\s+(.+?)(?:\.|,|!|\?|$)", "personal_preference", "I do {0}"),

        # Hobbies/Interests: "I enjoy X"
        (r"I\s+enjoy\s+(.+?)(?:\.|,|!|\?|$)", "personal_preference", "I enjoy {0}"),

        # Family: "I have X [siblings/children]"
        (r"I\s+have\s+(\d+)\s+(siblings|brothers|sisters|children|kids)(?:\.|,|!|\?|$)", "personal_preference", "I have {0} {1}"),

        # Age: "I'm X years old" or "I am X years old"
        (r"I'?m\s+(\d+)\s+years\s+old", "event", "I'm {0} years old"),

        # Birthday: "My birthday is X"
        (r"My\s+birthday\s+is\s+(.+?)(?:\.|,|!|\?|$)", "event", "My birthday is {0}"),

        # Anniversary: "My anniversary is X"
        (r"My\s+anniversary\s+is\s+(.+?)(?:\.|,|!|\?|$)", "event", "My anniversary is {0}"),
    ]

    @staticmethod
    async def extract_facts(user_message: str) -> list[Fact]:
        """
        Extract facts from user message using pattern matching.

        Args:
            user_message: The user's message text

        Returns:
            List of extracted Fact objects
        """
        facts = []

        if not user_message or not isinstance(user_message, str):
            return facts

        try:
            for pattern, category, format_template in FactExtractor.PATTERNS:
                matches = re.finditer(pattern, user_message, re.IGNORECASE)

                for match in matches:
                    # Extract groups
                    groups = match.groups()

                    # Skip if this looks like a non-fact statement
                    if len(groups) > 0 and groups[0]:
                        # Format the fact content
                        try:
                            content = format_template.format(*groups)
                        except (IndexError, KeyError):
                            content = groups[0]

                        # Create fact object
                        fact = Fact(
                            category=category,
                            content=content.strip(),
                            raw_statement=match.group(0).strip()
                        )

                        # Avoid duplicate facts
                        if not any(f.content.lower() == fact.content.lower() for f in facts):
                            facts.append(fact)

        except Exception as e:
            # Log error but don't break chat flow
            print(f"[FactExtractor] Error extracting facts: {str(e)}")
            pass

        return facts

    @staticmethod
    def categorize_fact(attribute: str) -> str:
        """Categorize a fact based on the attribute name."""
        attribute_lower = attribute.lower()

        # Event-related
        if any(word in attribute_lower for word in ["birthday", "anniversary", "age", "born"]):
            return "event"

        # Contact-related
        if any(word in attribute_lower for word in ["phone", "email", "address", "number", "website", "work", "company", "job", "occupation"]):
            return "contact"

        # Default to personal preference
        return "personal_preference"
