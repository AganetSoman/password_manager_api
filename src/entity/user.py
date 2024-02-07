from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.entity.credential import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)

    credentials = relationship("Credential", back_populates="user")
