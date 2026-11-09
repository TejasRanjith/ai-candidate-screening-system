import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, init_db
from app.api.routes.sessions import router as sessions_router
from app.api.routes.meta import router as meta_router
from app.services.rag_engine import rag_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("screening.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite tables exist and ChromaDB collection is loaded
    logger.info("Initializing database schema...")
    init_db()
    logger.info(f"Database initialized. ChromaDB collection count: {rag_engine.collection.count()}")
    yield
    logger.info("Shutting down Candidate Screening Application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade AI-powered role-based technical screening system with RAG grounding.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing the candidate screening request.", "error": str(exc)}
    )

# Include Routers under API prefix
app.include_router(meta_router, prefix=settings.API_PREFIX)
app.include_router(sessions_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_prefix": settings.API_PREFIX
    }
