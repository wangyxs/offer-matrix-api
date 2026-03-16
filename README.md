# offer-matrix-api

FastAPI backend for an AI mock interview and interview training platform.

This service powers role management, resume and material workflows, AI interview chat, question generation, interview record storage, favorites, and interview analysis. It is built for products that want to combine interview preparation, role-specific practice, and AI feedback into one backend.

## What It Does

- User registration, login, and JWT-based authentication
- Role and user-role management
- Resume and learning material association for each target role
- AI interview chat APIs for mock interview sessions
- Interview record storage and analysis
- AI-generated question sets for role-based training
- Favorite questions and learning workflows
- Text-to-speech support for interview interaction

## Product Positioning

This repository is the backend layer of the Offer Matrix project. The product is centered on:

- AI mock interview infrastructure
- role-based interview preparation
- resume-aware interview scenarios
- interview analysis and improvement loops

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite for local development
- PostgreSQL-ready data model for production evolution
- JWT authentication
- LLM integration for question generation and interview analysis
- Edge TTS integration

## Core API Areas

- `/api/auth`
  Authentication and token issuance
- `/api/users`
  User profile and account data
- `/api/roles`
  Role definitions, role assignment, resumes, and materials
- `/api/question-sets`
  AI-generated interview question sets
- `/api/interview`
  Interview chat, TTS, favorites, records, and analysis
- `/api/interviews`
  Interview record CRUD endpoints

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a local `.env` file:

```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
DATABASE_URL=sqlite:///./offer_matrix.db
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ZHIPUAI_API_KEY=
ALIYUN_ACCESS_KEY=
ALIYUN_SECRET_KEY=
ALIYUN_APP_ID=
ALIYUN_APP_KEY=
```

### 3. Initialize the database

```bash
python scripts/init_db.py
```

### 4. Start the API

```bash
python run.py
```

The service runs locally at `http://localhost:8000`.

## API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Detailed API examples are available in [API文档.md](./API文档.md).

## Project Structure

```text
app/
├── core/        # Config, database, security, middleware
├── models/      # SQLAlchemy models
├── routers/     # FastAPI route modules
├── schemas/     # Request and response schemas
└── services/    # AI interview, question generation, analysis, TTS, auth
scripts/         # Local setup and migration helpers
```

## Related Repository

- Android client: [offer-matrix-android](https://github.com/wangyxs/offer-matrix-android)

## Keywords

AI interview API, mock interview backend, FastAPI interview platform, interview analysis, question generation, resume-based interview, career prep backend
