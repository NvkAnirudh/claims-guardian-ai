from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import claims, chat, stats

app = FastAPI(
    title="Claims Guardian AI - Medical Claims Validator",
    description="AI-powered medical claims validation using multi-agent workflows",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims.router)
app.include_router(chat.router)
app.include_router(stats.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "claims-guardian-ai",
        "environment": settings.environment
    }


@app.get("/")
async def root():
    return {
        "message": "Claims Guardian AI - Medical Claims Validator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "claims": {
                "validate": "POST /api/claims/validate",
                "batch_validate": "POST /api/claims/batch-validate",
                "get_claim": "GET /api/claims/{claim_id}",
                "list_claims": "GET /api/claims/"
            },
            "chat": {
                "ask_question": "POST /api/chat/ask"
            },
            "stats": {
                "summary": "GET /api/stats/summary",
                "agents": "GET /api/stats/agents",
                "trends": "GET /api/stats/trends"
            }
        }
    }
