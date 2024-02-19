import os
from datetime import timedelta, datetime

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from src.config.db_connection import session, engine
from src.entity.credential import Credential, Base
from src.dto.credential_response import CredentialResponse
from src.entity.token import TokenBlacklist
from src.entity.user import User
from src.dto.user_response import UserResponse

Base.metadata.create_all(bind=engine)


class PasswordRepository:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    authenticated_user = None

    secret_key = os.getenv("SECRET_KEY")
    algorithm_type = os.getenv("ALGORITHM")

    def create_password(self, password_data: CredentialResponse, user_id):
        data = Credential(
            app_name=password_data.app_name,
            username=password_data.username,
            password=password_data.password,
            user_id=user_id)
        session.add(data)
        session.commit()
        return {"Message": "Data Saved"}

    def retrieve_credential_list(self, page_no, page_size, user_id: int):

        offset = (page_no - 1) * page_size
        limit = page_size

        total_records = session.query(func.count()).filter(Credential.user_id == user_id).scalar()

        password_list = session.query(Credential).filter(Credential.user_id == user_id).offset(offset).limit(
            page_size).all()

        total_pages = (total_records + page_size - 1) // page_size

        return {"document": password_list, "total": total_records, "totalPages": total_pages, "status": "success"}

    def credential_by_app_name(self, app_name: str):
        credential_list = session.query(Credential)
        credential_item = credential_list.filter_by(app_name=app_name)
        return credential_item.all()

    def update_credential(self, credential_id: int, new_credential_data: CredentialResponse):
        try:
            credential = session.query(Credential).filter_by(id=credential_id).one()
            if credential:
                credential.app_name = new_credential_data.app_name
                credential.username = new_credential_data.username
                credential.password = new_credential_data.password
                session.commit()
                return {"Message": "Credential updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="Credential not found")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Credential not found")

    def update_user(self, new_user_data: UserResponse, user_id: int, ):
        try:
            user = session.query(User).filter_by(id=user_id).one()
            if user:
                user.username = new_user_data.username
                user.email = new_user_data.email
                if new_user_data.password:
                    user.password = self.get_password_hash(new_user_data.password)
                session.commit()
                return {"Message": "User updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Email already exists")

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def sign_up(self, new_user: UserResponse):
        user = User(username=new_user.username,
                    email=new_user.email,
                    password=self.get_password_hash(new_user.password))
        try:
            session.add(user)
            session.commit()
            return {"Message": "New Account Created"}
        except HTTPException:
            raise HTTPException(status_code=400, detail="something went wrong")

    def create_access_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now() + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm_type)

        # db_token_exp = TokenExpiration(token=encoded_jwt, expire_at=expire)
        # session.add(db_token_exp)
        # session.commit()

        return encoded_jwt

    def revoke_token(self, token: str):
        # Store revoked token in the database
        db_token_blacklist = TokenBlacklist(token=token)
        session.add(db_token_blacklist)
        session.commit()

    # def is_token_expired(self, token: str) -> bool:
    #     # Check if token is expired
    #     token_exp = session.query(TokenExpiration).filter_by(token=token).first()
    #     return token_exp.expire_at < datetime.now() if token_exp else True

    def is_token_revoked(self, token: str) -> bool:
        # Check if token is revoked
        return session.query(TokenBlacklist).filter_by(token=token).first() is not None

    def retrieve_user_id(self):
        if self.authenticated_user is None:
            raise HTTPException(status_code=400, detail="User not authenticated")
        return self.authenticated_user.id

    def authenticate_user(self, username, password):
        try:
            user = session.query(User).filter_by(username=username).one()
            if not user:
                raise HTTPException(status_code=400, detail="User not found")
            if not self.pwd_context.verify(password, user.password):
                raise HTTPException(status_code=400, detail="Password incorrect")
            self.authenticated_user = user
            return self.token_access(user)
        except NoResultFound:
            raise HTTPException(status_code=400, detail="User not found")
        finally:
            session.close()

    def token_access(self, user):
        access_token = self.create_access_token(data={"sub": user.username, "user_id": user.id},
                                                expires_delta=timedelta(minutes=30))
        return {"user_id": user.id, "access_token": access_token, "token_type": "bearer"}
