import uvicorn
import os
import logging

if __name__ == "__main__":
    is_production = os.getenv("ENVIRONMENT") == "production"

    log_level = "warning" if is_production else "info"

    logging.basicConfig(
        level=logging.WARNING if is_production else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logging.getLogger("legality-ai").info(
        "Starting server in %s mode",
        "production" if is_production else "development"
    )

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=not is_production,
        log_level=log_level
    )
