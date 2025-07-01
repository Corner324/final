from fastapi import APIRouter

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("/")
async def root():
    return {"message": "Meetings service is running"}
