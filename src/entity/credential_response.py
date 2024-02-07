from pydantic import BaseModel


class CredentialResponse(BaseModel):
    credential_id: int
    app_name: str
    username: str
    password: str
    user_id: int
