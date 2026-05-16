from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from config import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    history: list[Message] = []

class ChatResponse(BaseModel):
    content: str
    language: str

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    try:
        system_prompt = f"""You are a friendly and helpful AI assistant.
Always respond in {request.language}."""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        content = response.choices[0].message.content
        return ChatResponse(content=content, language=request.language)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
