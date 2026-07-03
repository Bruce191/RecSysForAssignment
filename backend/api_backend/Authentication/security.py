from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 25

#Sets up password hashing using the bcrypt algorithm.
#deprecated="auto" ensures old hashes are still supported but marked for upgrade.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    """
    Verifies if the provided plain password matches the hashed password stored in the database.
    """
    return pwd_context.verify(plain_password, hashed_password)  # Compare the plain password with the hashed password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt