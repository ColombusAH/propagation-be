from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def schedules_root():
    return {"message": "Schedules endpoint"} 