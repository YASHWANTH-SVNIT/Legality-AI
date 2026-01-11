from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from src.api.routes import analysis, feedback, health

load_dotenv()

is_production = os.getenv("ENVIRONMENT") == "production"

app = FastAPI(
    title="Legality AI API",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
if os.path.exists("./uploads"):
    app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# Include routers - THIS IS CRITICAL
app.include_router(analysis.router, prefix="/analyze", tags=["Analysis"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(health.router, tags=["Health"])

@app.get("/")
def root():
    return {
        "name": "Legality AI API",
        "version": "1.0.0",
        "status": "operational"
    }