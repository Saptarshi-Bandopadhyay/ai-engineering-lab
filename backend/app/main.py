import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from backend.app.api.v1.endpoints import auth, conversation, documents, messages, users
from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging
from backend.app.middleware.logging import LoggingMiddleware
from backend.app.observability.metrics import metrics_response
from backend.app.observability.tracing import setup_tracing
from backend.app.schemas.health import HealthCheckResponse

setup_tracing()

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Starting {settings.project_name} v{settings.version} in {settings.environment} mode."
    )

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)

FastAPIInstrumentor.instrument_app(app)

app.add_middleware(LoggingMiddleware)

app.include_router(users.router, prefix=f"{settings.api_prefix}/users", tags=["Users"])

app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["Auth"])

app.include_router(
    conversation.router,
    prefix=f"{settings.api_prefix}/conversations",
    tags=["Conversations"],
)

app.include_router(messages.router, prefix="/api/v1/conversations", tags=["Messages"])

app.include_router(
    documents.router,
    prefix=f"{settings.api_prefix}/documents",
    tags=["Documents"],
)


@app.get(
    "/metrics",
    include_in_schema=False,
)
def metrics():
    return metrics_response()


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    logger.debug("Health check accessed by client")
    return {
        "status": "healthy",
        "project": settings.project_name,
        "environment": settings.environment,
        "version": settings.version,
    }
