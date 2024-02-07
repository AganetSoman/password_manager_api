from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.di.repository import password_repository
from src.entity.credential_response import CredentialResponse
from src.entity.user_response import UserResponse
from src.repository.password_repository import PasswordRepository

router = APIRouter()


class PasswordController:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @staticmethod
    @router.post("/sign_up")
    def sign_up(new_user: UserResponse):
        return PasswordRepository.sign_up(new_user)

    @staticmethod
    @router.post("/token")
    def token_access(form_data: OAuth2PasswordRequestForm = Depends()):
        return PasswordRepository.token_access(form_data)

    @staticmethod
    @router.get("/home")
    def home(token: str = Depends(oauth2_scheme)):
        return token

    @staticmethod
    @router.post("/create_password")
    async def create_password(password_data: CredentialResponse, ):
        return password_repository.create_password(password_data)

    @staticmethod
    @router.get("/credential_list")
    def credential_list(user_id: int):
        return password_repository.retrieve_credential_list(user_id)

    @staticmethod
    @router.get("/credential_by_app_name/{app_name}")
    def credential_by_app_name(app_name: str):
        return password_repository.credential_by_app_name(app_name)
