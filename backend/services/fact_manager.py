import json
from services.fact_extractor import Fact
from cache import cache_get, cache_set, cache_delete, redis_client
from config import get_settings

settings = get_settings()


class FactManager:
    """Manage fact caching in Redis."""

    FACT_PREFIX = "facts"
    FACTS_INDEX_PREFIX = "facts:session"

    @staticmethod
    async def cache_fact(session_id: str, fact: Fact, ttl: int = 86400) -> bool:
        """
        Cache a fact in Redis with TTL.

        Args:
            session_id: Session UUID
            fact: Fact object to cache
            ttl: Time to live in seconds (default: 86400 = 24h for owners)

        Returns:
            True if cached successfully, False otherwise
        """
        try:

            # Key: facts:{session_id}:{fact_id}
            fact_key = f"{FactManager.FACT_PREFIX}:{session_id}:{fact.id}"

            # Serialize fact to JSON
            fact_data = {
                "id": fact.id,
                "category": fact.category,
                "content": fact.content,
                "raw_statement": fact.raw_statement,
                "created_at": fact.created_at.isoformat()
            }

            # Cache the fact
            await cache_set(fact_key, fact_data, ttl)

            # Add to index: facts:session:{session_id} → set of fact IDs
            index_key = f"{FactManager.FACTS_INDEX_PREFIX}:{session_id}"
            redis_client.sadd(index_key, fact.id)
            redis_client.expire(index_key, ttl)

            return True

        except Exception as e:
            print(f"[FactManager] Error caching fact: {str(e)}")
            return False

    @staticmethod
    async def get_cached_facts(session_id: str) -> list[Fact]:
        """
        Retrieve all cached facts for a session.

        Args:
            session_id: Session UUID

        Returns:
            List of Fact objects cached for this session
        """
        try:
            # Get all fact IDs from index
            index_key = f"{FactManager.FACTS_INDEX_PREFIX}:{session_id}"
            fact_ids = redis_client.smembers(index_key)

            if not fact_ids:
                return []

            facts = []
            for fact_id in fact_ids:
                fact_key = f"{FactManager.FACT_PREFIX}:{session_id}:{fact_id}"
                fact_data = await cache_get(fact_key)

                if fact_data:
                    try:
                        # Deserialize fact
                        fact = Fact(
                            id=fact_data.get("id", ""),
                            category=fact_data.get("category", ""),
                            content=fact_data.get("content", ""),
                            raw_statement=fact_data.get("raw_statement", "")
                        )
                        facts.append(fact)
                    except Exception as e:
                        print(f"[FactManager] Error deserializing fact: {str(e)}")
                        continue

            return facts

        except Exception as e:
            print(f"[FactManager] Error retrieving cached facts: {str(e)}")
            return []

    @staticmethod
    async def clear_session_facts(session_id: str) -> bool:
        """
        Clear all cached facts for a session (e.g., on logout).

        Args:
            session_id: Session UUID

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            # Get all fact IDs
            index_key = f"{FactManager.FACTS_INDEX_PREFIX}:{session_id}"
            fact_ids = redis_client.smembers(index_key)

            # Delete each fact
            for fact_id in fact_ids:
                fact_key = f"{FactManager.FACT_PREFIX}:{session_id}:{fact_id}"
                await cache_delete(fact_key)

            # Delete the index
            redis_client.delete(index_key)

            return True

        except Exception as e:
            print(f"[FactManager] Error clearing session facts: {str(e)}")
            return False

    @staticmethod
    def format_facts_for_context(facts: list[Fact]) -> str:
        """
        Format facts into a string for inclusion in system prompt.

        Args:
            facts: List of Fact objects

        Returns:
            Formatted string with facts or empty string if no facts
        """
        if not facts:
            return ""

        # Group facts by category
        categorized = {}
        for fact in facts:
            if fact.category not in categorized:
                categorized[fact.category] = []
            categorized[fact.category].append(fact.content)

        # Build formatted string
        lines = ["## Remembered Facts\n"]

        # Sort categories for consistent output
        for category in sorted(categorized.keys()):
            lines.append(f"**{category.title()}:**")
            for content in categorized[category]:
                lines.append(f"- {content}")
            lines.append("")

        lines.append("Use these facts to provide personalized responses.\n")

        return "\n".join(lines)
