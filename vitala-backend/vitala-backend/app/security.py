"""Auth: bcrypt password hashing + JWT access tokens whose validity is also
tracked in Redis (so logout/revocation is instant)."""
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .redis_client import redis_client
from . import models

bearer = HTTPBearer(auto_error=True)


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_session_token(username: str) -> str:
    """Issue a JWT and register a matching session key in Redis."""
    jti = uuid.uuid4().hex
    ttl_seconds = settings.jwt_expire_minutes * 60
    exp = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    token = jwt.encode(
        {"sub": username, "jti": jti, "exp": exp},
        settings.jwt_secret,
        algorithm="HS256",
    )
    redis_client.set(f"session:{jti}", username, ex=ttl_seconds)
    return token


def revoke_session(token: str) -> None:
    """Delete the Redis session so the token can no longer authenticate."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        redis_client.delete(f"session:{payload['jti']}")
    except jwt.PyJWTError:
        pass


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> models.User:
    token = cred.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired, please log in again")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    jti = payload.get("jti")
    username = payload.get("sub")
    # The token must also have a live session in Redis (logout deletes it).
    if not jti or not redis_client.exists(f"session:{jti}"):
        raise HTTPException(status_code=401, detail="Session expired, please log in again")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return user
