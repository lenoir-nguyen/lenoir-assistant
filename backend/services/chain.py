from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_settings

settings = get_settings()


async def build_owner_chain_response(
    llm: ChatOpenAI,
    system_prompt: str,
    messages: list[BaseMessage],
    user_message: str
) -> str:
    """
    Build and execute owner chain response (async).

    Args:
        llm: ChatOpenAI instance
        system_prompt: System prompt template
        messages: Previous messages from database
        user_message: Current user message

    Returns:
        Response text from GPT-4o
    """
    # Build message list: system + history + current
    chat_messages = [SystemMessage(content=system_prompt)]
    chat_messages.extend(messages)
    chat_messages.append(HumanMessage(content=user_message))

    # Call LLM
    response = await llm.ainvoke(chat_messages)
    return response.content


async def build_stranger_chain_response(
    llm: ChatOpenAI,
    system_prompt: str,
    messages: list[BaseMessage],
    user_message: str
) -> str:
    """
    Build and execute stranger chain response (async).

    Args:
        llm: ChatOpenAI instance
        system_prompt: System prompt template
        messages: Previous messages (ephemeral, not persisted)
        user_message: Current user message

    Returns:
        Response text from GPT-4o
    """
    # Same as owner, but messages aren't persisted to DB
    chat_messages = [SystemMessage(content=system_prompt)]
    chat_messages.extend(messages)
    chat_messages.append(HumanMessage(content=user_message))

    response = await llm.ainvoke(chat_messages)
    return response.content


def get_llm() -> ChatOpenAI:
    """Create OpenAI LLM instance."""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY
    )


def build_owner_system_prompt(language: str = "en") -> str:
    """Build system prompt for owner mode."""
    return f"""You are Lenoir's personal AI assistant. You know Lenoir well and respond in a warm, familiar, and helpful tone.
Always respond in {language}."""


def build_stranger_system_prompt(language: str = "en") -> str:
    """Build system prompt for guest/stranger mode."""
    return f"""You are a friendly AI assistant on Lenoir's personal chatbot. Be helpful and welcoming to visitors.
Always respond in {language}."""
