from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.config.db_connection import Base
from src.entity.base_mixin import BaseMixin


class User(Base, BaseMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # credentials = relationship("Credential", back_populates="user")
