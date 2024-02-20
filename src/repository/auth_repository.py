import os
from datetime import timedelta, datetime

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound

from src.config.db_connection import session
from src.entity.token import TokenBlacklist
from src.entity.user import User


class AuthRepository:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    authenticated_user = None

    secret_key = os.getenv("SECRET_KEY")
    algorithm_type = os.getenv("ALGORITHM")

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now() + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm_type)

        return encoded_jwt

    def revoke_token(self, token: str):
        # Store revoked token in the database
        db_token_blacklist = TokenBlacklist(token=token)
        session.add(db_token_blacklist)
        session.commit()

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
