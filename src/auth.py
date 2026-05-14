from fastapi import HTTPException, Depends, status, Header
from fastapi.security import HTTPBasic
from typing import Optional
from src.database import users_db, files_db, User, File

security = HTTPBasic()

async def get_current_user_from_header(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> User:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-User-Id header"
        )
    
    if x_user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{x_user_id}' not found"
        )
    
    return users_db[x_user_id]

async def check_file_read_permission(
    file_id: str,
    current_user: User = Depends(get_current_user_from_header)
) -> File:
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file = files_db[file_id]
    
    if current_user.role == "admin":
        return file
    
    if file.owner_id == current_user.id:
        return file
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )

async def check_file_delete_permission(
    file_id: str,
    current_user: User = Depends(get_current_user_from_header)
) -> File:
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file = files_db[file_id]
    
    if current_user.role == "admin":
        return file
    
    if file.owner_id == current_user.id:
        return file
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )