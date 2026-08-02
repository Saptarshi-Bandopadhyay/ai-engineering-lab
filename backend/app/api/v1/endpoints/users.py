from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import DuplicateResourceError
from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse
from backend.app.services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_in: UserCreate, session: AsyncSession = Depends(get_db)):
    """
    Create a new user. The response explicitly filters out the password
    by enforcing the UserResponse schema.
    """
    try:
        new_user = await user_service.register_user(session, user_in)
        return new_user
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the details of the currently logged-in user.
    Requires a valid Bearer token.
    """
    return current_user
