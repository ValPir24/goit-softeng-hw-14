import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, database
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    """
    Generate hashed password.

    Args:
        password (str): Plain password.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify hashed password.

    Args:
        plain_password (str): Plain password.
        hashed_password (str): Hashed password.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data (dict): Data to encode into token.
        expires_delta (Optional[timedelta], optional): Expiry duration. Defaults to None.

    Returns:
        str: JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session, token: str) -> models.User:
    """
    Get current user from JWT token.

    Args:
        db (Session): Database session.
        token (str): JWT token.

    Raises:
        HTTPException: Raised if credentials cannot be validated.

    Returns:
        models.User: User object.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def send_verification_email(email: str, background_tasks: BackgroundTasks):
    """
    Send email verification link.

    Args:
        email (str): Email address.
        background_tasks (BackgroundTasks): Background tasks manager.
    """
    token = create_access_token(data={"sub": email})
    verification_link = f"{os.getenv('EMAIL_VERIFICATION_URL')}?token={token}"
    
    subject = "Verify your email"
    body = f"Please verify your email by clicking on the following link: {verification_link}"
    message = MIMEMultipart()
    message["From"] = os.getenv("SMTP_USER")
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    server = smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"))
    server.starttls()
    server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
    text = message.as_string()
    server.sendmail(os.getenv("SMTP_USER"), email, text)
    server.quit()

def verify_email_token(token: str) -> Optional[str]:
    """
    Verify JWT email verification token.

    Args:
        token (str): JWT token.

    Returns:
        Optional[str]: Email address if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None



