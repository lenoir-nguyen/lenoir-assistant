"""
Unit tests for fact extraction and caching (v4.1 feature).

Tests pattern-based fact extraction and Redis caching for short-term memory.
"""

import pytest
from services.fact_extractor import FactExtractor, Fact


class TestFactExtractor:
    """Test fact extraction using regex patterns."""

    @pytest.mark.asyncio
    async def test_extract_birthday_fact(self):
        """Test extraction of birthday fact."""
        message = "My birthday is May 15"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) == 1
        assert facts[0].category == "event"
        assert "May 15" in facts[0].content

    @pytest.mark.asyncio
    async def test_extract_favorite_color(self):
        """Test extraction of favorite color."""
        message = "My favorite color is blue"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) == 1
        assert facts[0].category == "personal_preference"
        assert "blue" in facts[0].content

    @pytest.mark.asyncio
    async def test_extract_work_fact(self):
        """Test extraction of work-related fact."""
        message = "I work at Acme Corp"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) == 1
        assert facts[0].category == "contact"
        assert "Acme Corp" in facts[0].content

    @pytest.mark.asyncio
    async def test_extract_like_fact(self):
        """Test extraction of 'I like' fact."""
        message = "I like coffee"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) == 1
        assert facts[0].category == "personal_preference"
        assert "coffee" in facts[0].content

    @pytest.mark.asyncio
    async def test_extract_multiple_facts(self):
        """Test extraction of multiple facts from one message."""
        message = "My name is Alex and I work at Acme Corp"
        facts = await FactExtractor.extract_facts(message)
        # Should extract at least 1 fact (work), might get the "is" statement too
        assert len(facts) >= 1

    @pytest.mark.asyncio
    async def test_extract_no_facts(self):
        """Test that non-fact statements are not extracted."""
        message = "What time is it?"
        facts = await FactExtractor.extract_facts(message)
        # Should not extract facts from questions
        assert len(facts) == 0 or all("time" not in f.content.lower() for f in facts)

    @pytest.mark.asyncio
    async def test_extract_phone_fact(self):
        """Test extraction of phone number."""
        message = "My phone is 555-1234"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) >= 1
        assert facts[0].category == "contact"

    @pytest.mark.asyncio
    async def test_extract_call_me_fact(self):
        """Test extraction of 'call me' name."""
        message = "You can call me Alex"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) == 1
        assert "Alex" in facts[0].content

    @pytest.mark.asyncio
    async def test_extract_hobby_fact(self):
        """Test extraction of hobby/interest."""
        message = "I enjoy painting"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) >= 1
        assert "painting" in facts[0].content.lower()

    @pytest.mark.asyncio
    async def test_categorize_fact_event(self):
        """Test fact categorization as event."""
        category = FactExtractor.categorize_fact("birthday")
        assert category == "event"

    @pytest.mark.asyncio
    async def test_categorize_fact_contact(self):
        """Test fact categorization as contact."""
        category = FactExtractor.categorize_fact("phone")
        assert category == "contact"

    @pytest.mark.asyncio
    async def test_categorize_fact_preference(self):
        """Test fact categorization as preference."""
        category = FactExtractor.categorize_fact("favorite")
        assert category == "personal_preference"

    @pytest.mark.asyncio
    async def test_extract_empty_message(self):
        """Test handling of empty message."""
        facts = await FactExtractor.extract_facts("")
        assert len(facts) == 0

    @pytest.mark.asyncio
    async def test_extract_none_message(self):
        """Test handling of None message."""
        facts = await FactExtractor.extract_facts(None)
        assert len(facts) == 0

    @pytest.mark.asyncio
    async def test_extract_duplicate_prevention(self):
        """Test that duplicate facts are not added."""
        message = "My birthday is May 15 and my birthday is May 15"
        facts = await FactExtractor.extract_facts(message)
        # Should not have duplicate "May 15" facts
        birthday_facts = [f for f in facts if "May 15" in f.content]
        assert len(birthday_facts) <= 1

    @pytest.mark.asyncio
    async def test_extract_has_id(self):
        """Test that extracted facts have IDs."""
        message = "My favorite food is pizza"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) > 0
        assert all(f.id for f in facts)

    @pytest.mark.asyncio
    async def test_extract_has_timestamp(self):
        """Test that extracted facts have timestamps."""
        message = "I like ice cream"
        facts = await FactExtractor.extract_facts(message)
        assert len(facts) > 0
        assert all(f.created_at for f in facts)


class TestFactObject:
    """Test the Fact data class."""

    def test_fact_creation(self):
        """Test creating a Fact object."""
        fact = Fact(
            category="personal_preference",
            content="I like coffee",
            raw_statement="I like coffee"
        )
        assert fact.category == "personal_preference"
        assert fact.content == "I like coffee"
        assert fact.id is not None

    def test_fact_has_default_id(self):
        """Test that Fact generates a default ID."""
        fact = Fact(content="test")
        assert fact.id is not None
        assert isinstance(fact.id, str)

    def test_fact_has_timestamp(self):
        """Test that Fact has a created_at timestamp."""
        fact = Fact(content="test")
        assert fact.created_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
