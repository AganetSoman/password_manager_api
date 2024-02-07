import os
from datetime import timedelta, datetime

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm.exc import NoResultFound

from src.config.db_connection import session, engine
from src.entity.credential import Credential, Base
from src.entity.credential_response import CredentialResponse
from src.entity.user import User
from src.entity.user_response import UserResponse

Base.metadata.create_all(bind=engine)


class PasswordRepository:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    secret_key = os.getenv("SECRET_KEY")
    algorithm_type = os.getenv("ALGORITHM")

    @staticmethod
    def create_password(password_data: CredentialResponse):
        data = Credential(credential_id=password_data.credential_id,
                          app_name=password_data.app_name,
                          username=password_data.username,
                          password=password_data.password,
                          user_id=password_data.user_id)
        session.add(data)
        session.commit()
        return {"Message": "Data Saved"}

    @staticmethod
    def retrieve_credential_list(user_id: int):
        credential_list = session.query(Credential).filter_by(user_id=user_id)
        return credential_list.all()

    @staticmethod
    def credential_by_app_name(app_name: str):
        credential_list = session.query(Credential)
        credential_item = credential_list.filter_by(app_name=app_name)
        return credential_item.all()

    @staticmethod
    def get_password_hash(password):
        return PasswordRepository.pwd_context.hash(password)

    @staticmethod
    def sign_up(new_user: UserResponse):
        user = User(user_id=new_user.user_id,
                    username=new_user.username,
                    password=PasswordRepository.get_password_hash(new_user.password))
        session.add(user)
        session.commit()
        return {"Message": "New Account Created"}

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now() + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, PasswordRepository.secret_key, algorithm=PasswordRepository.algorithm_type)
        return encoded_jwt

    @staticmethod
    def authenticate_user(user_name, password):

        try:
            user = session.query(User).filter_by(username=user_name).one()
            password_check = PasswordRepository.pwd_context.verify(password, user.password)
            return password_check
        except NoResultFound:
            return False
        finally:
            session.close()

    @staticmethod
    def token_access(form_data: OAuth2PasswordRequestForm = Depends()):
        username = form_data.username
        password = form_data.password

        if PasswordRepository.authenticate_user(username, password):
            access_token = PasswordRepository.create_access_token(data={"sub": username},
                                                                  expires_delta=timedelta(minutes=30))

            return {"access_token": access_token, "token_type": "bearer"}

        else:

            raise HTTPException(status_code=400, detail="incorrect credentials")
