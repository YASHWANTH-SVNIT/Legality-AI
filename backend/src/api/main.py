from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv

from src.api.routes import analysis, feedback, health, admin

load_dotenv()
is_production = os.getenv("ENVIRONMENT") == "production"

logging.basicConfig(
    level=logging.WARNING if is_production else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("legality-ai")

app = FastAPI(
    title="Legality AI API",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("./uploads"):
    app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")
    logger.info("Uploads directory mounted")

app.include_router(analysis.router, prefix="/analyze", tags=["Analysis"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(health.router, tags=["Health"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error on {request.method} {request.url.path}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Legality AI API started")
    logger.info(f"Environment: {'production' if is_production else 'development'}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Legality AI API shutting down")

# ---------------- ROOT ----------------
@app.get("/")
def root():
    logger.info("Health check hit on /")
    return {
        "name": "Legality AI API",
        "version": "1.0.0",
        "status": "operational"
    }
