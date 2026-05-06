from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List
from src.database import files_db, users_db, File, User
from src.auth import (
    get_current_user_from_header,
    check_file_read_permission,
    check_file_delete_permission
)

app = FastAPI(
    title="Corporate File Manager - Security",
    description="File manager with RBAC protection",
    version="2.0.0"
)

templates = Jinja2Templates(directory="templates")

@app.get("/files/{file_id}", response_model=File)
async def get_file(
    file: File = Depends(check_file_read_permission)
):

    return file

@app.delete("/files/{file_id}")
async def delete_file(
    file: File = Depends(check_file_delete_permission)
):

    file_id = file.id
    del files_db[file_id]
    
    return {
        "msg": "File deleted successfully",
        "file_id": file_id,
        "file_name": file.name
    }

@app.get("/files/my")
async def get_my_files(
    current_user: User = Depends(get_current_user_from_header)
):
    user_files = []
    for file in files_db.values():
        if file.owner_id == current_user.id:
            user_files.append({
                "id": file.id,
                "name": file.name,
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
            "name": file.name,
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


@app.get("/comments")
async def show_comments():
    return {"message": "Comments page - see task 6"}


@app.get("/")
async def root():
    return {
        "message": "Corporate File Manager",
        "endpoints": {
            "GET /files/my": "List my files",
            "GET /files/all": "List all files (admin only)",
            "GET /files/{file_id}": "Get file info",
            "DELETE /files/{file_id}": "Delete file",
            "GET /users/me": "Current user info",
            "GET /docs": "API Documentation"
        },
        "users": list(users_db.keys()),
        "files_count": len(files_db)
    }
