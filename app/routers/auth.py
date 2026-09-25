import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.responder import Responder
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from passlib.context import CryptContext

router = APIRouter(prefix="", tags=["Authentication"])
# PBKDF2 avoids native bcrypt compatibility issues on current Python runtimes.
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@router.post("/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
    user = User(
        id=user_id,
        name=user_in.name,
        email=user_in.email,
        password_hash=password_context.hash(user_in.password),
        role=user_in.role,
        phone=user_in.phone
    )
    db.add(user)

    # If registering as a responder, also create Responder profile
    if user_in.role == "RESPONDER":
        resp = Responder(
            id=f"R-{uuid.uuid4().hex[:4].upper()}",
            user_id=user.id,
            name=user.name,
            status="AVAILABLE",
            latitude=12.9721,
            longitude=77.5952,
            location_permission=True
        )
        db.add(resp)

    db.commit()
    db.refresh(user)
    return user

@router.post("/auth/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not password_context.verify(login_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = f"aeris_jwt_{user.id}_{int(datetime.now(timezone.utc).timestamp())}"
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/users/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db)):
    # Returns default operator or primary user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
