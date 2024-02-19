from sqlalchemy import Column, String, Integer, ForeignKey

from src.config.db_connection import Base
from src.entity.base_mixin import BaseMixin


class Credential(Base, BaseMixin):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    # user = relationship("User", back_populates="credentials")
