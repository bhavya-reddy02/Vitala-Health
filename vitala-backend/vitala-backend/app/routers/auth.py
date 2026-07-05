"""/auth — signup, login, logout."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..redis_client import update_leaderboard
from ..security import (
    hash_password, verify_password, create_session_token, revoke_session, bearer,
)
from .. import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.TokenOut)
def signup(body: schemas.SignupIn, db: Session = Depends(get_db)):
    uname = body.username.strip().lower()
    if db.query(models.User).filter(models.User.username == uname).first():
        raise HTTPException(status_code=409, detail="That username is taken")

    user = models.User(username=uname, email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.flush()  # assign user.id

    # Every account starts with a progress row so reads never hit a null.
    db.add(models.UserProgress(
        user_id=user.id, joined_date=date.today(), cat_counts={}, perfect_dates=[],
    ))
    db.commit()

    update_leaderboard(uname, 0)  # appear on the board immediately
    token = create_session_token(uname)
    return schemas.TokenOut(access_token=token, username=uname, has_profile=False)


@router.post("/login", response_model=schemas.TokenOut)
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):
    uname = body.username.strip().lower()
    user = db.query(models.User).filter(models.User.username == uname).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username or password doesn't match")

    token = create_session_token(uname)
    return schemas.TokenOut(access_token=token, username=uname, has_profile=user.profile is not None)


@router.post("/logout")
def logout(cred: HTTPAuthorizationCredentials = Depends(bearer)):
    revoke_session(cred.credentials)
    return {"ok": True}
