import uuid
import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from ..db import get_db, User, StudySession
from ..auth import hash_password, verify_password, create_token
from ..config import GOOGLE_CLIENT_ID

router = APIRouter(prefix="/api/auth", tags=["auth"])



class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    new_user = User(
        id=user_id,
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
        focus_streak="0 Days",
        total_hours=0.0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token(new_user.id, new_user.email)
    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "focusStreak": new_user.focus_streak,
            "totalHours": new_user.total_hours,
        },
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user.id, user.email)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "focusStreak": user.focus_streak,
            "totalHours": user.total_hours,
        },
    }


@router.get("/user/{user_id}/stats")
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {
            "id": user_id,
            "name": "Student",
            "email": "",
            "totalHours": 0.0,
            "sessions": 0,
            "avgScore": 100.0,
            "focusStreak": "0 Days",
        }

    sessions = db.query(StudySession).filter(StudySession.user_id == user_id).all()
    sessions_count = len(sessions)
    if sessions_count > 0:
        avg_score = round(sum(s.focus_score for s in sessions) / sessions_count, 1)
    else:
        avg_score = 100.0

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "totalHours": round(user.total_hours or 0.0, 1),
        "sessions": sessions_count,
        "avgScore": avg_score,
        "focusStreak": user.focus_streak or "0 Days",
    }


class GoogleAuthRequest(BaseModel):
    credential: str


@router.post("/google")
def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate or register user using Google Identity Services (GIS) ID Token."""
    if not req.credential:
        raise HTTPException(status_code=400, detail="Missing Google credential token")

    try:
        # Verify token signature and claims with Google
        idinfo = id_token.verify_oauth2_token(
            req.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )

        email = idinfo.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google token does not contain a verified email")

        name = idinfo.get("name") or email.split("@")[0]
        picture = idinfo.get("picture")

        # Check if user exists in database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user_id = f"usr_{uuid.uuid4().hex[:8]}"
            user = User(
                id=user_id,
                name=name,
                email=email,
                hashed_password=hash_password(secrets.token_hex(24)),
                focus_streak="0 Days",
                total_hours=0.0,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_token(user.id, user.email)
        return {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "focusStreak": user.focus_streak,
                "totalHours": user.total_hours,
                "picture": picture,
                "authProvider": "Google",
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google ID token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google authentication error: {str(e)}")

