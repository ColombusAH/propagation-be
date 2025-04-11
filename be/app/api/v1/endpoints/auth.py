from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def auth_root():
    return {"message": "Auth endpoint"} 


@router.get('/me')
async def get_me():
    # return a mock rick user info 
    return {
        "id": 1,
        "name": "Rick",
        "email": "rick@example.com",
        "role": "admin"
    }
