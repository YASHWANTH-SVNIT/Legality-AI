import os
import sys
import uvicorn
import subprocess
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# --- RUNTIME VECTOR DB BUILD ---
# This ensures we build the DB with access to runtime secrets, not during Docker build
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db_gold")

if not os.path.exists(DB_PATH):
    print("⚠️ Vector DB not found. Building now...")
    try:
        # Run build_vector_db.py as a subprocess
        # Assumes backend/ is current working directory or in path
        build_script = os.path.join(BASE_DIR, "build_pipeline", "build_vector_db.py")
        subprocess.run(["python", build_script], check=True)
        print("✅ Vector DB built successfully!")
    except Exception as e:
        print(f"❌ Failed to build Vector DB: {e}")
        # We don't exit, as the app might still run partially or for other reasons

from src.api.routes import analysis, feedback, health, admin

# Create a new app for Hugging Face deployment
app = FastAPI(
    title="Legality AI (HF Space)",
    docs_url="/api/docs",
    redoc_url=None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for HF Spaces as domain is dynamic
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount API Routes
app.include_router(analysis.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
# Health check at /api/health AND /health (for HF)
app.include_router(health.router, prefix="/api", tags=["Health"]) 

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 2. Serve Frontend Static Files
# The Dockerfile copies frontend/build to /app/backend/static
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    # Mount static assets (JS/CSS/Images)
    app.mount("/static", StaticFiles(directory=os.path.join(static_dir, "static")), name="static")
    
    # Serve other root files (favicon, manifest, etc.)
    # We can't mount root directly as it overrides API, so we serve specific files or catch-all
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Pass API requests through (though routes above should handle them first)
        if full_path.startswith("api") or full_path.startswith("health"):
            return {"error": "API route not found"}
        
        # Check if file exists in static root (e.g. favicon.ico)
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Fallback to index.html for React Router (Single Page App)
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
            
        return {"error": "Frontend not found"}
else:
    print(f"WARNING: Static directory not found at {static_dir}")

if __name__ == "__main__":
    # Hugging Face Spaces expects port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
