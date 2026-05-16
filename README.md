# Lenoir Chatbot v1

A simple AI chat assistant with multilingual support.

## Quick Start

1. **Backend** (in `backend/` folder):
```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend** (in `frontend/` folder):
```bash
cp .env.local.example .env.local
npm install
npm run dev
```

3. Open **http://localhost:3000**

## Features
- ✅ Text chat with GPT-4o
- ✅ Language selection (English, French, Vietnamese)
- ✅ Clean, simple UI

## Documentation
See `/docs` folder for detailed guides.
