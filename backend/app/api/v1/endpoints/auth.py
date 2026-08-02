from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import InvalidCredentialsError
from backend.app.dependencies.database import get_db
from backend.app.schemas.token import Token
from backend.app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post("/login", response_model=Token, summary="Login")
async def login_access_token(
    session: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """OAuth2 compatible token login. Get an access token for future requests."""
    try:
        token = await auth_service.authenticate_user(
            session=session, email=form_data.username, password=form_data.password
        )
        return token
    except InvalidCredentialsError:
        # Translation happens here
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
