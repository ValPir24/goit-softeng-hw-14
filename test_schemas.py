from pydantic import ValidationError
from datetime import date
from app.schemas import UserCreate, ContactCreate

def test_user_create_schema():
    # Перевірка схеми для створення користувача
    valid_user_data = {
        "email": "test@example.com",
        "password": "securepassword"
    }
    try:
        user = UserCreate(**valid_user_data)
        assert user.email == valid_user_data["email"]
        assert user.password == valid_user_data["password"]
    except ValidationError as e:
        assert False, f"Validation error: {e}"

def test_contact_create_schema():
    # Перевірка схеми для створення контакту
    valid_contact_data = {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "birthday": date(1990, 1, 1),
        "additional_info": "Some additional info"
    }
    try:
        contact = ContactCreate(**valid_contact_data)
        assert contact.name == valid_contact_data["name"]
        assert contact.surname == valid_contact_data["surname"]
        assert contact.email == valid_contact_data["email"]
        assert contact.phone == valid_contact_data["phone"]
        assert contact.birthday == valid_contact_data["birthday"]
        assert contact.additional_info == valid_contact_data["additional_info"]
    except ValidationError as e:
        assert False, f"Validation error: {e}"
