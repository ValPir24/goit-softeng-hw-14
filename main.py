import aioredis
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app import models, schemas, database, crud, utils
from typing import List, Optional
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Завантаження змінних середовища з файлу .env
load_dotenv()

app = FastAPI()

# Дозволити CORS для всіх доменів
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функція для отримання сесії бази даних
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ініціалізація Redis
async def startup():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis = await aioredis.from_url(redis_url, encoding="utf-8")
    await FastAPILimiter.init(redis)
    app.state.redis = redis
    database.Base.metadata.create_all(bind=database.engine)

# Закриття пулу з'єднань Redis при завершенні роботи додатка
async def shutdown():
    if hasattr(app.state, "redis") and app.state.redis:
        app.state.redis.close()
        await app.state.redis.wait_closed()

# Реєстрація функцій startup та shutdown
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data for user authentication.
        db (Session): Database session.

    Returns:
        dict: Access token and token type.
    """
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user (schemas.UserCreate): User creation data.
        background_tasks (BackgroundTasks): Background tasks manager.
        db (Session): Database session.

    Returns:
        schemas.User: The created user.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = crud.create_user(db=db, user=user)
    utils.send_verification_email(new_user.email, background_tasks)
    return new_user

@app.get("/")
def read_root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message.
    """
    return {"message": "Welcome to the Contact API"}

@app.post("/contacts/", response_model=schemas.Contact, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
def create_contact(contact: schemas.ContactCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Create a new contact.

    Args:
        contact (schemas.ContactCreate): Contact creation data.
        token (str): User's access token.
        db (Session): Database session.

    Returns:
        schemas.Contact: The created contact.
    """
    user = utils.get_current_user(db, token)
    return crud.create_contact(db=db, contact=contact, user_id=user.id)

@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, search: Optional[str] = None, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieve a list of contacts.

    Args:
        skip (int): Number of contacts to skip.
        limit (int): Maximum number of contacts to return.
        search (Optional[str]): Search query for contacts.
        token (str): User's access token.
        db (Session): Database session.

    Returns:
        List[schemas.Contact]: List of contacts.
    """
    user = utils.get_current_user(db, token)
    return crud.get_contacts(db=db, skip=skip, limit=limit, search=search, user_id=user.id)

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieve a contact by ID.

    Args:
        contact_id (int): ID of the contact.
        token (str): User's access token.
        db (Session): Database session.

    Returns:
        schemas.Contact: The retrieved contact.
    """
    user = utils.get_current_user(db, token)
    contact = crud.get_contact(db=db, contact_id=contact_id, user_id=user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Update a contact by ID.

    Args:
        contact_id (int): ID of the contact.
        contact (schemas.ContactUpdate): Updated contact data.
        token (str): User's access token.
        db (Session): Database session.

    Returns:
        schemas.Contact: The updated contact.
    """
    user = utils.get_current_user(db, token)
    db_contact = crud.get_contact(db=db, contact_id=contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=user.id)

@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Delete a contact by ID.

    Args:
        contact_id (int): ID of the contact.
        token (str): User's access token.
        db (Session): Database session.

    Returns:
        dict: Success message.
    """
    user = utils.get_current_user(db, token)
    db_contact = crud.get_contact(db=db, contact_id=contact_id, user_id=user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    crud.delete_contact(db=db, contact_id=contact_id, user_id=user.id)
    return {"message": "Contact deleted successfully"}

@app.post("/users/avatar")
def update_avatar(file: UploadFile, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Update the user's avatar.

    Args:
        file (UploadFile): Uploaded avatar file.
        token (str): User's access token.
        db (Session): Database session.

    Returns:
        dict: URL of the uploaded avatar.
    """
    user = utils.get_current_user(db, token)
    result = cloudinary.uploader.upload(file.file)
    avatar_url = result["secure_url"]
    crud.update_user_avatar(db, user_id=user.id, avatar_url=avatar_url)
    return {"avatar_url": avatar_url}

@app.get("/verify_email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user's email address.

    Args:
        token (str): Email verification token.
        db (Session): Database session.

    Returns:
        dict: Success message.
    """
    email = utils.verify_email_token(token)
    if email is None:
        raise HTTPException











