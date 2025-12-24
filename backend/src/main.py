"""
PCG Arena Backend - Main Entry Point
Protocol: arena/v0

This module initializes the application:
1. Loads configuration
2. Initializes database connection
3. Runs pending migrations
4. Starts the API server
"""

import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import load_config
from db import init_connection, run_migrations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

# Create FastAPI app
app = FastAPI(
    title="PCG Arena",
    description="Pairwise rating platform for Mario PCG generators",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and run migrations on startup."""
    logger.info("Starting PCG Arena backend...")
    logger.info(f"Protocol: arena/v0")
    
    try:
        # Initialize database connection
        init_connection(config.db_path)
        
        # Run migrations
        applied = run_migrations(config.migrations_path)
        logger.info(f"Database ready (applied {applied} new migrations)")
        
        # Check for seed data
        seed_path = Path(config.seed_path)
        generators_file = seed_path / "generators.json"
        if generators_file.exists():
            logger.info(f"Found generators.json at {generators_file}")
        else:
            logger.warning(f"generators.json not found at {generators_file}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns server status and protocol version.
    """
    from datetime import datetime, timezone
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "status": "ok",
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "build": {
            "backend_version": "0.1.0"
        }
    })


def main():
    """Run the server."""
    logger.info(f"Starting server on {config.host}:{config.port}")
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

