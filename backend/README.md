# Contract Agent - Backend

Enterprise-grade FastAPI backend for Contract Agent with AI-powered contract management, validation, and RAG chat.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (Memurai for Windows)

### Setup

1. **Create Virtual Environment**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

2. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

3. **Setup PostgreSQL**
```powershell
# Using psql
psql -U postgres
CREATE DATABASE contract_agent;
GRANT ALL PRIVILEGES ON DATABASE contract_agent TO postgres;
\q
```

4. **Configure Environment**

Copy `.env.example` to `.env` and update values. The .env file has been pre-configured with:
- ✅ Generated secure keys for JWT and encryption
- ✅ Pinecone API key from your account
- ✅ OpenRouter API key from your account
- ✅ PostgreSQL connection (default: postgres@localhost)
- ✅ Redis connection (default: localhost:6379)

**IMPORTANT:** The API keys in `.env` are from your message and should be rotated before production.

5. **Run Database Migrations**
```powershell
alembic upgrade head
```

6. **Start API Server**
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Verify Health**
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "environment": "development"
}
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/v1/              # API endpoints
│   ├── core/                # Config, security
│   ├── db/                  # Database models & CRUD
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── workers/             # Background jobs
│   └── tests/               # Test suite
├── alembic/                 # Database migrations
├── data/                    # File storage (local)
└── scripts/                 # Utility scripts
```

---

## 🔐 Security

### API Keys

**Status:** ⚠️ API keys in `.env` are from this chat session and are now exposed.

**Action Required Before Production:**
1. Rotate Pinecone API key at https://app.pinecone.io/
2. Rotate OpenRouter API key at https://openrouter.ai/keys
3. Update `.env` with new keys
4. Never commit `.env` to version control

### Generated Secrets

The following secrets have been automatically generated for local development:
- `SECRET_KEY`: For general application security
- `JWT_SECRET_KEY`: For JWT token signing
- `ENCRYPTION_KEY`: For encrypting API keys in database (32 bytes)

**Production:** Regenerate all secrets using:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📡 API Endpoints

### Health & Status
- `GET /health` - Health check

### Authentication (Phase 1 - In Progress)
- `POST /api/v1/auth/register` - Register user (admin only)
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Coming in Future Phases
- Contracts, Templates, Uploads, Validation, Chat, Admin

Full API documentation: http://localhost:8000/api/v1/docs

---

## 🧪 Testing

```powershell
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest app/tests/test_auth.py
```

---

## 🔄 Database Migrations

```powershell
# Create new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 📊 Development Status

**Current Phase:** Phase 1 - Core Foundation  
**Completed:**
- ✅ Project structure
- ✅ Environment configuration
- ✅ FastAPI application
- ✅ CORS middleware
- ✅ Health check endpoint
- ⏳ Database models (in progress)
- ⏳ JWT authentication (in progress)

**Next Steps:**
- Database models (User, Contract, etc.)
- Security utilities (JWT, password hashing)
- Auth endpoints
- CRUD operations

---

## 🚀 Production Deployment

### Environment Variables
Update `.env` for production:
- Set `ENVIRONMENT=production`
- Set `DEBUG=false`
- Use production database URL
- Use production Redis URL
- Enable HTTPS
- Restrict CORS origins

### Run in Production
```powershell
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📝 Notes

- **Local Development:** All features run on localhost (no cloud required)
- **Future Deployment:** Architecture supports AWS/GCP/Azure deployment
- **File Storage:** Currently uses local filesystem (`./data/uploads`)
- **Future Migration:** Easy switch to S3/Cloud Storage via storage abstraction

---

## 🆘 Troubleshooting

### PostgreSQL Connection Error
- Verify PostgreSQL is running: `net start postgresql-x64-14`
- Check database exists: `psql -U postgres -l`
- Verify DATABASE_URL in `.env`

### Redis Connection Error
- Verify Memurai is running: `net start memurai`
- Check REDIS_URL in `.env`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### API Key Errors
- Verify keys are correct in `.env`
- Test Pinecone connection
- Test OpenRouter connection

---

## 📞 Support

For issues or questions, refer to:
- Implementation Plan: `implementation_plan.md`
- Frontend Compatibility: `backend_frontend_compatibility_tests.md`
- FastAPI Docs: http://localhost:8000/api/v1/docs
