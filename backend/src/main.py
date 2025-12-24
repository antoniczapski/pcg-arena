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

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse

from config import load_config
from db import init_connection, get_connection, run_migrations, import_generators, init_generator_ratings, import_levels, log_db_status

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
        
        # Import seed data: generators
        gen_count = import_generators(config.seed_path)
        logger.info(f"Generators ready ({gen_count} imported/updated)")
        
        # Import seed data: levels
        level_count = import_levels(config.seed_path)
        logger.info(f"Levels ready ({level_count} imported/updated)")
        
        # Initialize ratings for new generators
        ratings_init = init_generator_ratings(config.initial_rating)
        if ratings_init > 0:
            logger.info(f"Initialized ratings for {ratings_init} new generator(s)")
        
        # Log DB status summary
        log_db_status(config.db_path)
        
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


@app.get("/v1/leaderboard")
async def get_leaderboard():
    """
    Get the current generator leaderboard.
    
    Returns generators sorted by rating (descending), with stats.
    """
    from datetime import datetime, timezone
    
    conn = get_connection()
    
    # Join generators and ratings, sort by rating DESC, then generator_id
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id,
            g.name,
            g.version,
            g.documentation_url,
            r.rating_value,
            r.games_played,
            r.wins,
            r.losses,
            r.ties,
            r.skips,
            r.updated_at_utc
        FROM generators g
        JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.is_active = 1
        ORDER BY r.rating_value DESC, g.generator_id ASC
        """
    )
    
    generators = []
    for rank, row in enumerate(cursor.fetchall(), start=1):
        generators.append({
            "rank": rank,
            "generator_id": row["generator_id"],
            "name": row["name"],
            "version": row["version"],
            "documentation_url": row["documentation_url"],
            "rating": row["rating_value"],
            "games_played": row["games_played"],
            "wins": row["wins"],
            "losses": row["losses"],
            "ties": row["ties"],
            "skips": row["skips"],
        })
    
    # Get the most recent update time
    if generators:
        cursor = conn.execute(
            "SELECT MAX(updated_at_utc) as last_update FROM ratings"
        )
        last_update = cursor.fetchone()["last_update"]
    else:
        last_update = datetime.now(timezone.utc).isoformat()
    
    return JSONResponse({
        "protocol_version": "arena/v0",
        "updated_at_utc": last_update,
        "rating_system": {
            "name": "ELO",
            "initial_rating": config.initial_rating,
            "k_factor": config.k_factor,
        },
        "generators": generators,
    })


@app.get("/", response_class=HTMLResponse)
async def leaderboard_page():
    """
    Render a simple HTML leaderboard page.
    
    Provides a human-readable view of generator rankings.
    """
    from datetime import datetime, timezone
    
    conn = get_connection()
    
    # Get leaderboard data
    cursor = conn.execute(
        """
        SELECT 
            g.generator_id,
            g.name,
            g.version,
            g.documentation_url,
            r.rating_value,
            r.games_played,
            r.wins,
            r.losses,
            r.ties,
            r.skips
        FROM generators g
        JOIN ratings r ON g.generator_id = r.generator_id
        WHERE g.is_active = 1
        ORDER BY r.rating_value DESC, g.generator_id ASC
        """
    )
    rows = cursor.fetchall()
    
    # Build table rows
    table_rows = ""
    for rank, row in enumerate(rows, start=1):
        doc_link = f'<a href="{row["documentation_url"]}">{row["name"]}</a>' if row["documentation_url"] else row["name"]
        table_rows += f"""
        <tr>
            <td>{rank}</td>
            <td>{doc_link}</td>
            <td><code>{row["generator_id"]}</code></td>
            <td>{row["version"]}</td>
            <td><strong>{row["rating_value"]:.1f}</strong></td>
            <td>{row["games_played"]}</td>
            <td>{row["wins"]}</td>
            <td>{row["losses"]}</td>
            <td>{row["ties"]}</td>
            <td>{row["skips"]}</td>
        </tr>
        """
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PCG Arena - Leaderboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 2rem;
                background: #0d1117;
                color: #c9d1d9;
            }}
            h1 {{
                color: #58a6ff;
                border-bottom: 1px solid #30363d;
                padding-bottom: 0.5rem;
            }}
            .meta {{
                color: #8b949e;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: #161b22;
                border-radius: 6px;
                overflow: hidden;
            }}
            th, td {{
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid #30363d;
            }}
            th {{
                background: #21262d;
                color: #58a6ff;
                font-weight: 600;
            }}
            tr:hover {{
                background: #1f2428;
            }}
            code {{
                background: #30363d;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                font-size: 0.85rem;
            }}
            a {{
                color: #58a6ff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .rating {{
                font-weight: bold;
                color: #3fb950;
            }}
            .footer {{
                margin-top: 2rem;
                color: #8b949e;
                font-size: 0.8rem;
            }}
        </style>
    </head>
    <body>
        <h1>🎮 PCG Arena Leaderboard</h1>
        <div class="meta">
            Protocol: arena/v0 | Rating: ELO (K={config.k_factor}) | Updated: {now}
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Generator</th>
                    <th>ID</th>
                    <th>Version</th>
                    <th>Rating</th>
                    <th>Games</th>
                    <th>W</th>
                    <th>L</th>
                    <th>T</th>
                    <th>Skip</th>
                </tr>
            </thead>
            <tbody>
                {table_rows if table_rows else '<tr><td colspan="10" style="text-align:center;color:#8b949e;">No generators yet</td></tr>'}
            </tbody>
        </table>
        <div class="footer">
            <a href="/v1/leaderboard">JSON API</a> | 
            <a href="/health">Health Check</a> |
            <a href="/docs">API Docs</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


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

