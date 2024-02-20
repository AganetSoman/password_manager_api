from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.di.auth_repository import auth_repository

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthController:

    @staticmethod
    @auth_router.post("/token")
    def login(form_data: OAuth2PasswordRequestForm = Depends()):
        username = form_data.username
        password = form_data.password
        return auth_repository.authenticate_user(username, password)

    @staticmethod
    @auth_router.get("/home")
    def home(token: str = Depends(oauth2_scheme)):
        return token

    @staticmethod
    @auth_router.post("/logout")
    def logout(token: str = Depends(oauth2_scheme)):
        # Check if token is already revoked
        if auth_repository.is_token_revoked(token):
            raise HTTPException(status_code=400, detail="Token already revoked")

        # Revoke the token
        auth_repository.revoke_token(token)

        return {"message": "Logout successful"}
