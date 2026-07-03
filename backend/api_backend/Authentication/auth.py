from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from backend.api_backend.Database import models
from backend.api_backend.Authentication import security
from backend.api_backend.Database.db import get_db

#original
# def get_user(db: Session, name: str):
#     return db.query(models.user_map).filter(models.user_map.name == name).first()

def get_user(db: Session, name: str):
    return db.query(models.user_map).filter(models.user_map.name == name).first()
    # O(log n) with indexed row (name)


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 1. Get JWT token from cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token not found")

    # 2. Decode JWT token safely
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        #print("username: ", username)
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError as e:
        # You can check for expiration or other issues
        if "Signature has expired" in str(e):
            raise HTTPException(status_code=401, detail="Token expired")
        raise HTTPException(status_code=401, detail="Invalid token")

    # 3. Find user based on JWT username
    user = db.query(models.user_map).filter(models.user_map.name == username).first()
    #print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user