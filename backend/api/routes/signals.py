"""GET /signals endpoint."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from db import neo4j_client

router = APIRouter()

def serialize_signal(signal: dict) -> dict:
    """Convert Neo4j DateTime objects to ISO strings for JSON serialization."""
    result = {}
    for key, value in signal.items():
        if hasattr(value, 'iso_format'):
            result[key] = value.iso_format()
        elif hasattr(value, '__str__') and 'DateTime' in type(value).__name__:
            result[key] = str(value)
        else:
            result[key] = value
    return result

@router.get("/signals")
async def get_signals(exam_name: str = None, limit: int = 20):
    """Return all signals, optionally filtered by exam name."""
    # TODO: server-side filtering requires graph traversal query
    # For now returning all signals unfiltered
    signals = neo4j_client.get_all_signals(limit=limit)
    serialized = [serialize_signal(s) for s in signals]
    return JSONResponse({"signals": serialized, "total": len(serialized)})