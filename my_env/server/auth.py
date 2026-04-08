import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import DBUser

SECRET_KEY = "HACKATHON_SUPER_SECRET_KEY"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Stateless JWT Extraction Middleware explicitly intercepting unauthorized Logic Requests natively.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload mapping")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Auth token explicitly expired or invalid")
        
    # Bind User Instance
    user = db.query(DBUser).filter(DBUser.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Mapped user explicit anomaly")
        
    return user
