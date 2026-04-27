"""
Admin authorization helpers.
Supports token, JWT, or hybrid mode.
"""

from typing import Optional, Set

from fastapi import HTTPException
import jwt
from jwt import PyJWTError

from .config import settings


def _valid_tokens() -> Set[str]:
    tokens: Set[str] = {token.strip() for token in settings.ADMIN_CLEAR_TOKENS if token and token.strip()}
    legacy = settings.ADMIN_CLEAR_TOKEN.strip()
    if legacy:
        tokens.add(legacy)
    return tokens


def _validate_token(auth_token: Optional[str]) -> bool:
    tokens = _valid_tokens()
    if not tokens:
        return False
    return bool(auth_token and auth_token in tokens)


def _validate_jwt(authorization: Optional[str]) -> bool:
    secret = settings.JWT_SECRET_KEY.strip()
    if not secret:
        return False

    if not authorization:
        return False

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return False

    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except PyJWTError:
        return False

    role = str(payload.get("role", "")).strip()
    allowed = {value.strip() for value in settings.ADMIN_JWT_ALLOWED_ROLES if value and value.strip()}
    if not allowed:
        return False
    return role in allowed


def require_admin_access(x_admin_token: Optional[str], authorization: Optional[str]) -> None:
    """
    Validate admin access for protected endpoints.
    """
    mode = settings.ADMIN_AUTH_MODE.strip().lower()

    if mode not in {"token", "jwt", "hybrid"}:
        raise HTTPException(status_code=500, detail="Invalid ADMIN_AUTH_MODE configuration")

    token_ok = _validate_token(x_admin_token)
    jwt_ok = _validate_jwt(authorization)

    if mode == "token":
        if not _valid_tokens():
            raise HTTPException(
                status_code=503,
                detail="Admin token auth is disabled. Configure ADMIN_CLEAR_TOKEN or ADMIN_CLEAR_TOKENS.",
            )
        if not token_ok:
            raise HTTPException(status_code=401, detail="Invalid admin token")
        return

    if mode == "jwt":
        if not settings.JWT_SECRET_KEY.strip():
            raise HTTPException(
                status_code=503,
                detail="JWT auth is disabled. Configure JWT_SECRET_KEY.",
            )
        if not jwt_ok:
            raise HTTPException(status_code=401, detail="Invalid or unauthorized JWT")
        return

    # hybrid mode
    if not _valid_tokens() and not settings.JWT_SECRET_KEY.strip():
        raise HTTPException(
            status_code=503,
            detail="Hybrid auth is disabled. Configure token and/or JWT settings.",
        )
    if not (token_ok or jwt_ok):
        raise HTTPException(status_code=401, detail="Admin authorization failed")
