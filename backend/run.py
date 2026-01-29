import uvicorn
import os
import logging
import sys
import traceback

# Ensure backend root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    is_production = os.getenv("ENVIRONMENT") == "production"
    log_level = "warning" if is_production else "info"

    logging.basicConfig(
        level=logging.WARNING if is_production else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    
    logger = logging.getLogger("legality-ai")
    logger.info("Starting server in %s mode", "production" if is_production else "development")

    try:
        # Import app directly
        print("DEBUG: Importing app...", flush=True)
        from src.api.main import app
        print("DEBUG: App imported successfully", flush=True)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            reload=False, 
            log_level=log_level
        )
    except Exception as e:
        print("\n--- FATAL ERROR DURING STARTUP ---", flush=True)
        traceback.print_exc()
        if hasattr(e, '__cause__') and e.__cause__:
             print(f"\nROOT CAUSE: {e.__cause__}", flush=True)
             traceback.print_exception(type(e.__cause__), e.__cause__, e.__cause__.__traceback__)
        
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)
