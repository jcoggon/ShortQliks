
from fastapi import APIRouter

router = APIRouter(prefix="/v1")

@router.get("/users/")
async def read_users():
    return [{"username": "user1"}, {"username": "user2"}]

@router.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"username": f"user{user_id}"}
