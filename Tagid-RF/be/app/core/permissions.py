"""Role-based access control (RBAC) utilities."""

from functools import wraps
from typing import Callable, List

from app.api.dependencies.auth import get_current_user
from fastapi import Depends, HTTPException, status
from prisma.models import User


def requires_role(*allowed_roles: str):
    """
    Decorator to restrict endpoint access to specific roles.

    Usage:
        @router.get("/admin-only")
        @requires_role("SUPER_ADMIN", "NETWORK_MANAGER")
        async def admin_endpoint(current_user: User = Depends(get_current_user)):
            ...

    Args:
        *allowed_roles: Variable number of role strings that are allowed to access the endpoint.

    Raises:
        HTTPException: 403 if user's role is not in allowed_roles.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args, current_user: User = Depends(get_current_user), **kwargs
        ):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                )
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


def requires_any_role(allowed_roles: List[str]):
    """
    Dependency function to check if user has any of the allowed roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(get_current_user),
            _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"]))
        ):
            ...

    Args:
        allowed_roles: List of role strings that are allowed.

    Returns:
        Dependency function that validates user role.

    Raises:
        HTTPException: 403 if user's role is not in allowed_roles.
    """

    async def check_role(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return check_role


def is_admin(user: User) -> bool:
    """Check if user has admin privileges."""
    return user.role in ["SUPER_ADMIN", "NETWORK_MANAGER"]


def is_manager(user: User) -> bool:
    """Check if user has manager privileges."""
    return user.role in ["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"]


def can_create_role(user: User, target_role: str) -> bool:
    """
    Check if user can create another user with the target role.

    Args:
        user: The user attempting to create another user.
        target_role: The role of the user being created.

    Returns:
        True if user can create target_role, False otherwise.
    """
    role_hierarchy = {
        "SUPER_ADMIN": [
            "SUPER_ADMIN",
            "NETWORK_MANAGER",
            "STORE_MANAGER",
            "EMPLOYEE",
            "CUSTOMER",
        ],
        "NETWORK_MANAGER": ["STORE_MANAGER", "EMPLOYEE", "CUSTOMER"],
        "STORE_MANAGER": ["EMPLOYEE", "CUSTOMER"],
    }

    allowed_roles = role_hierarchy.get(user.role, [])
    return target_role in allowed_roles
