from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


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
    content_type: str = "text/plain"

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
    
    files_db["file1"] = File(
        id="file1",
        name="report_alice.txt",
        size=1024,
        owner_id="alice",
        owner_name="alice",
        created_at=datetime.now().isoformat(),
        content_type="text/plain"
    )
    
    files_db["file2"] = File(
        id="file2",
        name="presentation_alice.pdf",
        size=2048,
        owner_id="alice",
        owner_name="alice",
        created_at=datetime.now().isoformat(),
        content_type="application/pdf"
    )
    
    files_db["file3"] = File(
        id="file3",
        name="data_bob.xlsx",
        size=3072,
        owner_id="bob",
        owner_name="bob",
        created_at=datetime.now().isoformat(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    files_db["file4"] = File(
        id="file4",
        name="system_config.conf",
        size=512,
        owner_id="admin",
        owner_name="admin",
        created_at=datetime.now().isoformat(),
        content_type="text/plain"
    )
    
    files_db["file5"] = File(
        id="file5",
        name="notes_alice.md",
        size=768,
        owner_id="alice",
        owner_name="alice",
        created_at=datetime.now().isoformat(),
        content_type="text/markdown"
    )


init_database()