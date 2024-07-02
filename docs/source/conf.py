# Configuration file for the Sphinx documentation builder.

import os
import sys
from dotenv import load_dotenv

# Шлях до кореневої папки проекту
sys.path.insert(0, os.path.abspath('../'))

# Завантаження змінних оточення з .env файлу
env_path = os.path.abspath('../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f".env file not found at path: {env_path}")

# Додаємо шлях до кореневої папки проекту
sys.path.insert(0, os.path.abspath('../../'))

project = 'contact_api'
copyright = '2024, Iryna S'
author = 'Iryna S'

# -- General configuration ---------------------------------------------------

autodoc_mock_imports = ["fastapi", "sqlalchemy", "aioredis", "cloudinary", "dotenv", "fastapi_limiter"]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True

# -- Napoleon settings -------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Значення за замовчуванням
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Завантажуємо значення змінної середовища
access_token_expire_minutes_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if access_token_expire_minutes_str is not None:
    try:
        # Спробуємо перетворити значення на ціле число
        ACCESS_TOKEN_EXPIRE_MINUTES = int(access_token_expire_minutes_str)
    except ValueError:
        print(f"Invalid value for ACCESS_TOKEN_EXPIRE_MINUTES in .env: {access_token_expire_minutes_str}")
        ACCESS_TOKEN_EXPIRE_MINUTES = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
else:
    # Якщо змінна середовища відсутня, використовуємо значення за замовчуванням
    print(f"ACCESS_TOKEN_EXPIRE_MINUTES not found in .env, using default: {DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES}")
    ACCESS_TOKEN_EXPIRE_MINUTES = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES

# Виводимо значення для перевірки
print(f"ACCESS_TOKEN_EXPIRE_MINUTES loaded: {ACCESS_TOKEN_EXPIRE_MINUTES}")


























