"""
/api/health — used by Docker, monitoring systems, and humans
verifying that the backend is alive.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}
