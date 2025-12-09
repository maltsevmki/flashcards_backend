# 📚 Flashcards AI Backend — Architecture Overview

## 1. System Overview

Flashcards AI is an asynchronous REST API backend for a mobile flashcard app, empowering users to create, manage, and study custom flashcards.  
The API uses FastAPI for speedy, scalable development, PostgreSQL for relational data, and integrates with AI language APIs to automatically generate flashcards from highlighted book text or manual input.

**High-level flow:**
- Users register, log in, and access their personal flashcard decks.
- The mobile app or future web clients communicate with the backend via REST endpoints.
- When a user highlights text (e.g., in an e-book), the backend sends the highlight to an AI service, receives suggested questions/answers, and stores them as flashcards for the user’s study deck.

---

## 2. Main Technologies Used

Layer	Technology
- API Framework	FastAPI (async, Python 3.10+)
- Database	PostgreSQL (managed cloud)
- ORM	SQLModel (SQLAlchemy ORM/async)
- Testing	pytest, httpx, FastAPI TestClient
- Auth	OAuth2, JWT (python-jose, passlib)
- AI Integration	OpenAI, HuggingFace API, httpx
- Deployment	Railway/Heroku/Web
- Code Formatting	flake8
- Docs	Markdown, FastAPI OpenAPI docs