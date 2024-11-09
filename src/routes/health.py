from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
