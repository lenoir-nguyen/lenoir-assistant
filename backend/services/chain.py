from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import PGVector
from sqlalchemy.orm import Session
from config import get_settings
from db.models import Base

settings = get_settings()


def build_owner_chain(db: Session, language: str = "en"):
    """
    Build an LLMChain for owner (Lenoir) with RAG capabilities.

    The owner chain:
    - Uses gpt-4o model for high-quality personalized responses
    - Maintains a conversation buffer of last 10 messages for context
    - Receives augmented prompts containing retrieved facts from pgvector (RAG)
    - Responds in the specified language (en/fr/vi)
    - Stores all messages in database for persistent history

    Args:
        db: SQLAlchemy database session (for potential retriever integration)
        language: Response language code (en=English, fr=French, vi=Vietnamese)

    Returns:
        tuple: (LLMChain, ChatOpenAI LLM) for response generation
    """
    # Initialize OpenAI GPT-4o with streaming enabled
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,  # Balanced creativity (0.7) and consistency
        streaming=True,   # Enable token-by-token streaming for real-time response
        openai_api_key=settings.OPENAI_API_KEY
    )

    # Memory manager: maintains conversation context from last 10 messages
    # This helps LLM understand conversation flow and maintain consistency
    memory = ConversationBufferWindowMemory(
        k=10,
        memory_key="chat_history",
        return_messages=True
    )

    # System prompt tailored for owner mode
    # Instructs LLM to be personal, use context, and respond in user's language
    system_prompt = f"""You are Lenoir's personal AI assistant. You know Lenoir well and can recall personal facts and past conversations.
Be warm, attentive, and personalized in your responses. Use the provided context to inform your replies.
Current language: {language}
Always respond in {language}."""

    system_message = SystemMessagePromptTemplate.from_template(system_prompt)
    human_template = "{input}"
    human_message = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

    # LLMChain: orchestrates LLM invocations with memory and prompt templates
    # RAG context is injected by chat router before calling apredict() to augment LLM's knowledge
    chain = LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

    return chain, llm


def build_stranger_chain(language: str = "en"):
    """
    Build an LLMChain for stranger sessions (no personal data, no persistence).

    The stranger chain:
    - Uses gpt-4o model for friendly, helpful responses
    - Maintains only 5-message in-memory buffer (not persisted to database)
    - No access to personal facts or history (RAG disabled)
    - Responds in specified language
    - All context lost on page reload (privacy-by-design)

    Args:
        language: Response language code (en/fr/vi)

    Returns:
        tuple: (LLMChain, ChatOpenAI LLM) for response generation
    """
    # Initialize GPT-4o with streaming
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        streaming=True,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # Minimal memory: 5-message window, in-memory only, never persisted to database
    # This ensures strangers cannot infer anything about owner from stored history
    # Memory is cleared on page reload for strong privacy guarantees
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True
    )

    # System prompt for stranger mode: friendly but generic, no personal context
    system_prompt = f"""You are a friendly and helpful AI assistant. You're speaking with a new visitor.
Be warm and welcoming, but professional.
Current language: {language}
Always respond in {language}."""

    system_message = SystemMessagePromptTemplate.from_template(system_prompt)
    human_template = "{input}"
    human_message = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

    # LLMChain for stateless conversations: context not stored anywhere
    chain = LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

    return chain, llm
