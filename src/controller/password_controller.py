from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.responses import FileResponse

from src.di.auth_repository import auth_repository
from src.di.password_repository import password_repository
from src.dto.credential_response import CredentialResponse
from src.dto.user_response import UserResponse
from src.controller.auth_controller import oauth2_scheme

router = APIRouter()


class PasswordController:

    @staticmethod
    @router.post("/sign_up", tags=["SignUp"])
    def sign_up(new_user: UserResponse):
        return password_repository.sign_up(new_user)

    @staticmethod
    @router.post("/create_password")
    async def create_password(password_data: CredentialResponse,
                              user_id: int = Depends(auth_repository.retrieve_user_id),
                              token: str = Depends(oauth2_scheme)):
        if auth_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.create_password(password_data, user_id)

    @staticmethod
    @router.get("/credential_list/{limit}/{skip}")
    def credential_list(page_no: int, page_size: int, user_id: int = Depends(auth_repository.retrieve_user_id),
                        token: str = Depends(oauth2_scheme)):
        if auth_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.retrieve_credential_list(page_no, page_size, user_id)

    @staticmethod
    @router.get("/credential_by_app_name/{app_name}")
    def credential_by_app_name(app_name: str, token: str = Depends(oauth2_scheme)):
        if auth_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.credential_by_app_name(app_name)

    @staticmethod
    @router.post("update/credential_details")
    def update_credential(credential_id: int, new_credential_data: CredentialResponse,
                          token: str = Depends(oauth2_scheme)):
        if auth_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked. Password creation not allowed.")
        return password_repository.update_credential(credential_id, new_credential_data)

    @staticmethod
    @router.post("/update_user")
    def change_password(new_user_data: UserResponse, user_id: int = Depends(auth_repository.retrieve_user_id)):

        return password_repository.update_user(new_user_data, user_id)

    @staticmethod
    @router.post("/upload")
    def upload_file(file: UploadFile = File(...)):
        return password_repository.upload_file(file)

    @staticmethod
    @router.get("/retreive/file", response_class=FileResponse)
    def read_data():
        return password_repository.read_data()
