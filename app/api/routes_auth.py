from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserId, AuthUseCaseDep, OAuth2PasswordRequestFormDep
from app.core.errors import EmailAlreadyRegisteredError, NotFoundError, UnauthorizedError
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic

router = APIRouter()


@router.post("/register", response_model=UserPublic)
async def register(request: RegisterRequest, auth_usecase: AuthUseCaseDep):
    try:
        return await auth_usecase.register(request.email, request.password)
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestFormDep, auth_usecase: AuthUseCaseDep):
    try:
        return TokenResponse(access_token=await auth_usecase.login(form_data.username, form_data.password))
    except UnauthorizedError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})


@router.get("/me")
async def get_me(user_id: CurrentUserId, auth_usecase: AuthUseCaseDep):
    try:
        return await auth_usecase.get_profile(user_id=user_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
