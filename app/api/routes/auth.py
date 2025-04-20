from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.auth import UserCreate, Token, UserLogin
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.utils import constants as msg 
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    """
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == user_data.email).first()
        if user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "status_code": 400,
                    "message": msg.EMAIL_ALREADY_REGISTERED,
                    "data": None
                }
            )

        # Hash the password and create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(email=user_data.email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT token
        token = create_access_token(data={"sub": str(new_user.id)})

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "status_code": 201,
                "message": msg.USER_REGISTERED_SUCCESSFULLY,
                "data": {
                    "access_token": token,
                    "token_type": "bearer"
                }
            }
        )
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT token.
    """
    try:
        # Check if both email and password are provided
        if not user_data.email or not user_data.password:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "status_code": 400,
                    "message": msg.EMAIL_PASSWORD_REQUIRED,
                    "data": None
                }
            )

        # Retrieve user
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "status_code": 404,
                    "message": msg.USER_NOT_FOUND,
                    "data": None
                }
            )

        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "status_code": 401,
                    "message": msg.INVALID_PASSWORD,
                    "data": None
                }
            )

        # Create token
        access_token = create_access_token(data={"sub": str(user.id)})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "status_code": 200,
                "message": msg.LOGIN_SUCCESS,
                "data": {
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            }
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )
