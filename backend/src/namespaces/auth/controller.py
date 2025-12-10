"""Authentication routes."""
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.dependencies import get_db, get_current_active_user
from src.services.auth_service import AuthService
from src.services.notification_service import notification_service
from src.schemas.user import UserCreate, UserResponse, Token
from src.models.user import User


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-debug")
async def register_debug(request: Request):
    """Debug endpoint to see raw request body."""
    body = await request.body()
    logger.info(f"Raw body: {body}")
    try:
        json_body = await request.json()
        logger.info(f"JSON body: {json_body}")
        return {"received": json_body}
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return {"error": str(e), "raw": body.decode()}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user. Account will be inactive until approved by an admin."""
    logger.info(f"Register request received: {user_data.model_dump()}")
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.create_user(user_data)
        logger.info(f"New user registered (pending approval): {user.username}")
        
        # Send WhatsApp notification asynchronously (don't block registration)
        logger.info(f"[REGISTER] Calling notification service for user: {user.username}")
        try:
            await notification_service.notify_new_user_registration(
                username=user.username,
                email=user.email
            )
            logger.info(f"[REGISTER] Notification service call completed")
        except Exception as notif_error:
            # Log but don't fail registration if notification fails
            logger.error(f"[REGISTER] Failed to send registration notification: {notif_error}", exc_info=True)
        
        return user
    except ValueError as e:
        logger.warning(f"Validation error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return JWT token."""
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        # Verificar se é usuário inativo ou credenciais incorretas
        existing_user = await auth_service.get_user_by_username(form_data.username)
        if existing_user and not existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta aguardando aprovação. Entre em contato com um administrador.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user
