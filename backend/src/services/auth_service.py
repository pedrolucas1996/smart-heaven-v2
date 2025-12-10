"""Authentication service for user management and JWT tokens."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.config import settings
from src.models.user import User
from src.schemas.user import UserCreate, TokenData


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"
)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def _truncate_password(password: str) -> str:
        """Truncate password to 72 bytes for bcrypt compatibility."""
        password_bytes = password.encode('utf-8')
        if len(password_bytes) <= 72:
            return password
        # Truncate at byte level, then decode back to string
        truncated = password_bytes[:72]
        # Handle potential cut-off in middle of multi-byte character
        try:
            return truncated.decode('utf-8')
        except UnicodeDecodeError:
            # If we cut in middle of char, try 71, 70, etc
            for i in range(71, 0, -1):
                try:
                    return password_bytes[:i].decode('utf-8')
                except UnicodeDecodeError:
                    continue
            return password[:50]  # Fallback
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        plain_password = AuthService._truncate_password(plain_password)
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        password = AuthService._truncate_password(password)
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        # Truncate password before verification (bcrypt limit is 72 bytes)
        truncated_password = password[:72]
        if not self.verify_password(truncated_password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if username exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email exists
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Create new user
        # Truncate password before hashing (bcrypt limit is 72 bytes)
        truncated_password = user_data.password[:72]
        hashed_password = self.get_password_hash(truncated_password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            is_active=False,  # Requer aprovação manual de um admin
            created_at=datetime.utcnow(),
            id_house=user_data.id_house
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
