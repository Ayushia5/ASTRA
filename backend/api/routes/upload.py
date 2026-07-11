"""Upload route placeholder."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def placeholder():
    """Placeholder route."""
    return {"status": "not implemented"}
