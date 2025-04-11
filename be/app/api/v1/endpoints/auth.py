from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def auth_root():
    return {"message": "Auth endpoint"} 


@router.get('/me')
async def get_me():
    logger.info("Getting me")
    # return a mock rick user info 
    return {
        "id": 1,
        "name": "Rick",
        "email": "rick@example.com",
        "role": "admin"
    }
