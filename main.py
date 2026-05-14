import os
import uuid
import filetype
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import List
from src.database import files_db, users_db, File, User
from src.auth import (
    get_current_user_from_header,
    check_file_read_permission,
    check_file_delete_permission
)

app = FastAPI(
    title="Corporate File Manager - Security",
    description="File manager with RBAC protection and secure file upload",
    version="2.0.0"
)

templates = Jinja2Templates(directory="templates")

STORAGE_DIR = "storage"
MAX_FILE_SIZE = 2 * 1024 * 1024
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]

os.makedirs(STORAGE_DIR, exist_ok=True)

def validate_file_size(file_data: bytes) -> None:
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )

def validate_file_type(file_data: bytes) -> str:
    kind = filetype.guess(file_data)
    
    if kind is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot determine file type or file is corrupted"
        )
    
    mime_type = kind.mime
    
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {mime_type} not allowed. Only JPEG and PNG images are allowed"
        )
    
    return mime_type

def save_file_to_disk(file_data: bytes, file_id: str) -> str:
    file_extension = None
    
    kind = filetype.guess(file_data)
    if kind:
        file_extension = kind.extension
    
    if not file_extension:
        file_extension = "bin"
    
    filename = f"{file_id}.{file_extension}"
    file_path = os.path.join(STORAGE_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    return file_path

def delete_file_from_disk(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)

@app.get("/")
async def root():
    return {
        "message": "Corporate File Manager",
        "users": list(users_db.keys()),
        "files_count": len(files_db)
    }

@app.get("/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user_from_header)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@app.post("/files/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user_from_header)
):
    file_data = await file.read()
    
    validate_file_size(file_data)
    
    mime_type = validate_file_type(file_data)
    
    file_id = str(uuid.uuid4())
    
    storage_path = save_file_to_disk(file_data, file_id)
    
    new_file = File(
        id=file_id,
        name=file.filename,
        size=len(file_data),
        owner_id=current_user.id,
        owner_name=current_user.username,
        created_at=datetime.now().isoformat(),
        content_type=mime_type,
        storage_path=storage_path,
        original_name=file.filename
    )
    
    files_db[file_id] = new_file
    
    return {
        "msg": "File uploaded successfully",
        "file_id": file_id,
        "file_name": file.filename,
        "size": len(file_data),
        "storage_path": storage_path
    }

@app.get("/files/{file_id}/download")
async def download_file(
    file: File = Depends(check_file_read_permission)
):
    if not os.path.exists(file.storage_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        path=file.storage_path,
        filename=file.original_name,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=\"{file.original_name}\""
        }
    )

@app.get("/files/my")
async def get_my_files(
    current_user: User = Depends(get_current_user_from_header)
):
    user_files = []
    for file in files_db.values():
        if file.owner_id == current_user.id:
            user_files.append({
                "id": file.id,
                "name": file.original_name,
                "size": file.size,
                "owner_id": file.owner_id,
                "owner_name": file.owner_name,
                "created_at": file.created_at,
                "content_type": file.content_type
            })
    
    return {
        "user": current_user.username,
        "role": current_user.role,
        "files": user_files,
        "count": len(user_files)
    }

@app.get("/files/all")
async def get_all_files(
    current_user: User = Depends(get_current_user_from_header)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    all_files = []
    for file in files_db.values():
        all_files.append({
            "id": file.id,
            "name": file.original_name,
            "size": file.size,
            "owner_id": file.owner_id,
            "owner_name": file.owner_name,
            "created_at": file.created_at,
            "content_type": file.content_type
        })
    
    return {
        "admin": current_user.username,
        "files": all_files,
        "count": len(files_db)
    }

@app.get("/files/{file_id}")
async def get_file_info(
    file: File = Depends(check_file_read_permission)
):
    return {
        "id": file.id,
        "name": file.original_name,
        "size": file.size,
        "owner_id": file.owner_id,
        "owner_name": file.owner_name,
        "created_at": file.created_at,
        "content_type": file.content_type
    }

@app.delete("/files/{file_id}")
async def delete_file(
    file: File = Depends(check_file_delete_permission)
):
    file_id = file.id
    
    delete_file_from_disk(file.storage_path)
    
    del files_db[file_id]
    
    return {
        "msg": "File deleted successfully",
        "file_id": file_id,
        "file_name": file.original_name
    }

@app.get("/comments")
async def show_comments():
    return {"message": "Comments page - see task 6"}