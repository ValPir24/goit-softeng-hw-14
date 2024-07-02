from sqlalchemy.orm import Session
from app import models, schemas, utils

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by email.

    Args:
        db (Session): Database session.
        email (str): User's email address.

    Returns:
        models.User: User object if found, None otherwise.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user.

    Args:
        db (Session): Database session.
        user (schemas.UserCreate): User creation data.

    Returns:
        models.User: The created user.
    """
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user.

    Args:
        db (Session): Database session.
        email (str): User's email address.
        password (str): User's password.

    Returns:
        models.User: Authenticated user if credentials are correct, None otherwise.
    """
    user = get_user_by_email(db, email)
    if not user or not utils.verify_password(password, user.hashed_password):
        return None
    return user

def verify_user_email(db: Session, email: str):
    """
    Verify a user's email.

    Args:
        db (Session): Database session.
        email (str): User's email address.

    Returns:
        models.User: User object with verified email if found, None otherwise.
    """
    user = get_user_by_email(db, email)
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)
    return user

def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    """
    Update a user's avatar URL.

    Args:
        db (Session): Database session.
        user_id (int): User's ID.
        avatar_url (str): URL of the new avatar.

    Returns:
        models.User: User object with updated avatar URL if found, None otherwise.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
    return user

def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    """
    Create a new contact.

    Args:
        db (Session): Database session.
        contact (schemas.ContactCreate): Contact creation data.
        user_id (int): ID of the owner user.

    Returns:
        models.Contact: The created contact.
    """
    db_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, skip: int = 0, limit: int = 10, search: str = None, user_id: int = None):
    """
    Retrieve a list of contacts.

    Args:
        db (Session): Database session.
        skip (int): Number of contacts to skip.
        limit (int): Maximum number of contacts to return.
        search (str): Search query for contacts.
        user_id (int): ID of the owner user.

    Returns:
        List[models.Contact]: List of contacts.
    """
    query = db.query(models.Contact).filter(models.Contact.owner_id == user_id)
    if search:
        query = query.filter(models.Contact.name.ilike(f"%{search}%") | models.Contact.email.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Retrieve a contact by ID.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact.
        user_id (int): ID of the owner user.

    Returns:
        models.Contact: The retrieved contact.
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int):
    """
    Update a contact by ID.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact.
        contact (schemas.ContactUpdate): Updated contact data.
        user_id (int): ID of the owner user.

    Returns:
        models.Contact: The updated contact.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact by ID.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact.
        user_id (int): ID of the owner user.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact



