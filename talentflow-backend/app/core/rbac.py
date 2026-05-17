from typing import List, Callable
from fastapi import Depends, HTTPException
from app.core.auth import get_current_user, ClerkUser

def require_role(allowed_roles: List[str]) -> Callable:
    def role_checker(current_user: ClerkUser = Depends(get_current_user)) -> ClerkUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Operation not permitted for role: {current_user.role}"
            )
        return current_user
    return role_checker

# Pre-defined checkers
require_admin = require_role(["admin"])
require_recruiter = require_role(["admin", "recruiter"])
require_manager = require_role(["admin", "recruiter", "hiring_manager"])
require_any = require_role(["admin", "recruiter", "hiring_manager", "viewer"])
