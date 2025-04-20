from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Validates the JWT access token, retrieves the corresponding user from the database,
    and returns the authenticated user object.
    """
    # Define a standard unauthorized error to be raised if validation fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT token to extract payload
    payload = decode_access_token(token)

    # If payload is invalid or 'sub' (subject i.e. user ID) is missing, raise exception
    if not payload or "sub" not in payload:
        raise credentials_exception

    # Fetch the user from the database using the ID from token's payload
    user = db.query(User).filter(User.id == payload["sub"]).first()

    if not user:
        raise credentials_exception

    return user
