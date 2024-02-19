from pydantic import BaseModel


class CredentialResponse(BaseModel):

    app_name: str
    username: str
    password: str

