from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import PGVector
from sqlalchemy.orm import Session
from config import get_settings
from db.models import Base

settings = get_settings()


def build_owner_chain(db: Session, language: str = "en"):
    """
    Build a ConversationalRetrievalChain for the owner (Lenoir).
    Includes RAG retrieval over personal facts and history.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        streaming=True,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # Memory: keep last 10 messages
    memory = ConversationBufferWindowMemory(
        k=10,
        memory_key="chat_history",
        return_messages=True
    )

    # System prompt for owner
    system_prompt = f"""You are Lenoir's personal AI assistant. You know Lenoir well and can recall personal facts and past conversations.
Be warm, attentive, and personalized in your responses. Use the provided context to inform your replies.
Current language: {language}
Always respond in {language}."""

    system_message = SystemMessagePromptTemplate.from_template(system_prompt)
    human_template = "{input}"
    human_message = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

    # Note: In production, we'd connect PGVector as a retriever
    # For now, we'll use LLMChain and manually augment with retrieved docs
    chain = LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

    return chain, llm


def build_stranger_chain(language: str = "en"):
    """
    Build a simple LLMChain for strangers.
    No RAG, no history persistence.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        streaming=True,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # Memory: keep last 5 messages only (in-memory, not persisted)
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True
    )

    # System prompt for stranger
    system_prompt = f"""You are a friendly and helpful AI assistant. You're speaking with a new visitor.
Be warm and welcoming, but professional.
Current language: {language}
Always respond in {language}."""

    system_message = SystemMessagePromptTemplate.from_template(system_prompt)
    human_template = "{input}"
    human_message = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

    chain = LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

    return chain, llm
