# Contract Agent

<div align="center">

![Contract Agent Logo](https://img.shields.io/badge/Contract%20Agent-AI%20Powered-purple?style=for-the-badge)

**Enterprise-grade AI-powered contract lifecycle automation platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)](https://www.postgresql.org)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-00A67E)](https://www.pinecone.io)

</div>

---

## 🌟 Overview

Contract Agent is a modern, full-stack contract management platform that leverages AI to automate and streamline the entire contract lifecycle. Built with enterprise-grade security and scalability in mind.

### Core Features

| Feature | Description |
|---------|-------------|
| 📄 **Centralized Contract Hub** | Upload, store, and manage all contracts in one place with semantic search |
| 🤖 **AI Contract Generation** | Generate contracts from templates using AI-powered variable filling |
| ✅ **Smart Validation** | AI-powered risk analysis, clause detection, and compliance checking |
| 💬 **RAG-Powered Chat** | Ask questions about your contracts with grounded, cited responses |
| 🔐 **Role-Based Access** | Granular permissions for users, reviewers, and administrators |
| 📊 **Audit Logging** | Complete activity tracking for compliance and security |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  TypeScript • Vite • TailwindCSS • shadcn/ui • React Query      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API (FastAPI)                       │
│  Python • SQLAlchemy • Pydantic • JWT Auth • Rate Limiting      │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐    ┌───────────────────┐    ┌───────────────┐
│  PostgreSQL   │    │     Pinecone      │    │  OpenRouter   │
│   Database    │    │  Vector Search    │    │   LLM API     │
└───────────────┘    └───────────────────┘    └───────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 14+
- **Redis** (optional, for production)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create database
psql -U postgres -c "CREATE DATABASE contract_agent;"

# Run migrations
alembic upgrade head

# Create admin user
python scripts/create_admin.py

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

---

## 📁 Project Structure

```
contract-agent/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API endpoints
│   │   │   ├── admin/        # Admin endpoints
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── contracts.py  # Contract CRUD
│   │   │   ├── templates.py  # Template management
│   │   │   ├── uploads.py    # File uploads
│   │   │   ├── chat.py       # RAG chat
│   │   │   ├── validation.py # Contract validation
│   │   │   └── proposals.py  # Validation proposals
│   │   ├── core/             # Core utilities
│   │   │   ├── config.py     # Configuration
│   │   │   ├── security.py   # JWT, encryption
│   │   │   ├── logging.py    # Structured logging
│   │   │   └── rate_limit.py # Rate limiting
│   │   ├── db/               # Database layer
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   ├── crud/         # CRUD operations
│   │   │   └── session.py    # DB session
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── rag.py        # RAG service
│   │   │   ├── embedding.py  # Embeddings
│   │   │   ├── validation.py # Validation
│   │   │   └── ...
│   │   ├── workers/          # Background tasks
│   │   └── tests/            # Test suite
│   ├── alembic/              # Migrations
│   ├── data/                 # File storage
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── ui/           # shadcn/ui
│   │   │   ├── error/        # Error boundaries
│   │   │   └── loading/      # Skeletons
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── hooks/            # Custom hooks
│   │   ├── contexts/         # React contexts
│   │   ├── types/            # TypeScript types
│   │   └── lib/              # Utilities
│   ├── public/
│   └── package.json
│
└── README.md
```

---

## 🔐 User Roles

| Role | Permissions |
|------|-------------|
| **Regular** | Create contracts, upload documents, use AI chat |
| **Reviewer** | All regular permissions + approve/reject contracts |
| **Admin** | Full system access + user management + settings |

---

## 🤖 AI Features

### RAG-Powered Chat
- Upload documents and ask questions
- Grounded responses with source citations
- Confidence scoring
- Multi-document context

### Contract Validation
- Risk scoring (0-100%)
- Clause detection
- Compliance checking
- Improvement suggestions

### AI Generation
- Template-based contract creation
- Variable substitution
- AI-assisted drafting

---

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register (admin)
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user

### Contracts
- `GET /api/v1/contracts` - List contracts
- `POST /api/v1/contracts` - Create contract
- `POST /api/v1/contracts/from-template` - Generate from template
- `POST /api/v1/contracts/{id}/submit` - Submit for review
- `POST /api/v1/contracts/{id}/approve` - Approve (reviewer)
- `POST /api/v1/contracts/{id}/reject` - Reject (reviewer)

### Chat
- `POST /api/v1/chat/rag` - RAG chat

### Validation
- `POST /api/v1/validation/contracts/{id}/validate` - Validate contract

### Admin
- `GET /api/v1/admin/users` - List users
- `POST /api/v1/admin/users` - Create user
- `GET /api/v1/admin/audit` - Audit logs
- `GET /api/v1/admin/settings/health` - System health

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

---

## 🚀 Production Deployment

### Environment Variables

See `backend/.env.example` for all required environment variables.

**Critical for production:**
- Generate new `SECRET_KEY`, `JWT_SECRET_KEY`, `ENCRYPTION_KEY`
- Set `ENVIRONMENT=production`
- Set `DEBUG=false`
- Configure proper database URL
- Set production CORS origins

### Docker (Coming Soon)

```bash
docker-compose up -d
```

---

## 📝 License

Private project - All rights reserved.

---

## 👥 Authors

**Tuhin Dutta** - Initial development and architecture

---

<div align="center">

**Built with ❤️ using modern technologies**

FastAPI • React • TypeScript • PostgreSQL • Pinecone • OpenRouter

</div>
