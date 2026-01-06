from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def shifts_root():
    return {"message": "Shifts endpoint"}
