from fastapi import FastAPI
from routers import chat

app = FastAPI(title="Lenoir Chatbot API", version="1.0.0")

app.include_router(chat.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
