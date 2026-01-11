import uvicorn
import os

if __name__ == "__main__":
    is_production = os.getenv("ENVIRONMENT") == "production"
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=not is_production,  # No reload in prod
        log_level="warning" if is_production else "info"
    )