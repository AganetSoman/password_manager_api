import os
import shutil

from fastapi import HTTPException, UploadFile, File
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from starlette.responses import FileResponse

from src.config.db_connection import session, engine
from src.di.auth_repository import auth_repository
from src.entity.credential import Credential, Base
from src.dto.credential_response import CredentialResponse
from src.entity.user import User
from src.dto.user_response import UserResponse

Base.metadata.create_all(bind=engine)


class PasswordRepository:

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
                    user.password = auth_repository.get_password_hash(new_user_data.password)
                session.commit()
                return {"Message": "User updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Email already exists")

    def upload_file(self, file: UploadFile = File(...)):
        destination_folder = os.getenv("DESTINATION_FOLDER")

        # Move the uploaded file to the destination folder
        file_path = destination_folder + "/" + file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "destination_folder": destination_folder}

    def read_data(self):
        file_path = os.getenv("FILE_PATH")
        response = FileResponse(file_path, media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=example.csv"
        return response

    def sign_up(self, new_user: UserResponse):
        user = User(username=new_user.username,
                    email=new_user.email,
                    password=auth_repository.get_password_hash(new_user.password))
        try:
            session.add(user)
            session.commit()
            return {"Message": "New Account Created"}
        except HTTPException:
            raise HTTPException(status_code=400, detail="something went wrong")
