from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    email: str
    password: str
    role: str

class File(BaseModel):
    id: str
    name: str
    size: int
    owner_id: str
    owner_name: str
    created_at: str
    content_type: str
    storage_path: str
    original_name: str

users_db: Dict[str, User] = {}
files_db: Dict[str, File] = {}

def init_database():
    users_db["alice"] = User(
        id="alice",
        username="alice",
        email="alice@example.com",
        password="Alice123!",
        role="user"
    )
    
    users_db["bob"] = User(
        id="bob",
        username="bob",
        email="bob@example.com",
        password="Bob123!",
        role="user"
    )
    
    users_db["admin"] = User(
        id="admin",
        username="admin",
        email="admin@example.com",
        password="Admin123!",
        role="admin"
    )

init_database()