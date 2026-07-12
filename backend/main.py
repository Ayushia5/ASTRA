"""FastAPI application entry point."""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import upload, signals, graph
from db.neo4j_client import verify_connection

load_dotenv()

app = FastAPI(title="ASTRA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(graph.router, prefix="/graph-data", tags=["graph"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    verify_connection()
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
