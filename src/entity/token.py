from sqlalchemy import Column, Integer, String

from src.config.db_connection import Base
from src.entity.base_mixin import BaseMixin


class TokenBlacklist(Base, BaseMixin):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False)
