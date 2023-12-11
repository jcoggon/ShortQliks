from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app import SessionLocal
import secrets
import string
from pydantic import BaseModel
from typing import Optional
import httpx

class UserBase(BaseModel):
    email: str
    firstName: str
    lastName: str

router = APIRouter()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

@router.post('/onboard')
async def onboard(user: UserBase, local_kw: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        app_name = 'ShortQliks'
        
        budibase_api_key = 'budibase'  # Consider moving this to a config file or environment variable
        headers = {
            'x-budibase-api-key': budibase_api_key,
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f'http://web:5000/api/app_search/{app_name}')
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to find app.")
            
            response_data = response.json()
            app_id = response_data.get('_id')
            # print(app_id)
            password = generate_password()
            data = {
                "email": user.email,
                "password": password,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "roles": {app_id: "BASIC"},
                "forceResetPassword": False,
                "builder": {
                    "global": False
                },
                "admin": {
                    "global": False
                }
            }
            response = await client.post("http://bbproxy:10000/api/global/users", headers=headers, json=data)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Onboarding failed.")

            response_data = response.json()
            # print(response_data)  # Add this line
            user_data = response_data
            user_data['password'] = password
            # print(user_data)

            if not user_data:
                return {"onboarding": "Failed"}, 404

            user = await create_user_onboarding(user_data, db)

            return {"user_id": user.id, "password": password}, 200
    finally:
        await db.close()

async def create_user_onboarding(data, db: Session):
    try:
        user = User(
            user_id=data.get('_id'),
            email=data.get('email'),
            password=data.get('password')
        )
        # print(user)
        db.add(user)
        await db.flush()  # Ensure that the INSERT has been executed
        await db.commit()
        return user
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def generate_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
