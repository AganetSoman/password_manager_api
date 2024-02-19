from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.di.repository import password_repository
from src.dto.credential_response import CredentialResponse
from src.dto.user_response import UserResponse

router = APIRouter()


class PasswordController:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @staticmethod
    @router.post("/sign_up", tags=["SignUp"])
    def sign_up(new_user: UserResponse):
        return password_repository.sign_up(new_user)

    @router.post("/token")
    def login(form_data: OAuth2PasswordRequestForm = Depends()):
        username = form_data.username
        password = form_data.password
        return password_repository.authenticate_user(username, password)

    @router.get("/home")
    def home(token: str = Depends(oauth2_scheme)):
        return token

    @staticmethod
    @router.post("/create_password")
    async def create_password(password_data: CredentialResponse,
                              user_id: int = Depends(password_repository.retrieve_user_id),
                              token: str = Depends(oauth2_scheme)):
        if password_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.create_password(password_data, user_id)

    @staticmethod
    @router.get("/credential_list/{limit}/{skip}")
    def credential_list(page_no: int, page_size: int, user_id: int = Depends(password_repository.retrieve_user_id),
                        token: str = Depends(oauth2_scheme)):
        if password_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.retrieve_credential_list(page_no, page_size, user_id)

    @staticmethod
    @router.get("/credential_by_app_name/{app_name}")
    def credential_by_app_name(app_name: str, token: str = Depends(oauth2_scheme)):
        if password_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.credential_by_app_name(app_name)

    @staticmethod
    @router.post("update/credential_details")
    def update_credential(credential_id: int, new_credential_data: CredentialResponse,
                          token: str = Depends(oauth2_scheme)):
        if password_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.update_credential(credential_id, new_credential_data)

    @staticmethod
    @router.post("/update_user")
    def update_user(new_user_data: UserResponse, user_id: int = Depends(password_repository.retrieve_user_id),
                    token: str = Depends(oauth2_scheme)):
        if password_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.update_user(new_user_data, user_id)

    @staticmethod
    @router.post("/logout")
    def logout(token: str = Depends(oauth2_scheme)):
        # Check if token is already revoked
        if password_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked")

        # Revoke the token
        password_repository.revoke_token(token)

        return {"message": "Logout successful"}
