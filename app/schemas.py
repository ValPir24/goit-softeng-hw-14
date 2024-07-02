from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

class UserBase(BaseModel):
    """
    Base user model schema.
    """
    email: EmailStr

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str

class User(UserBase):
    """
    User model schema with additional fields.
    """
    id: int
    is_verified: bool
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True  # Замість orm_mode

class ContactBase(BaseModel):
    """
    Base contact model schema.
    """
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact.
    """
    pass

class Contact(ContactBase):
    """
    Contact model schema with additional fields.
    """
    id: int
    owner_id: int

    class Config:
        from_attributes = True  # Замість orm_mode

class Token(BaseModel):
    """
    Token model schema.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Token data model schema.
    """
    email: Optional[str] = None










