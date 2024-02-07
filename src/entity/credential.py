from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Credential(Base):
    __tablename__ = "credentials"

    credential_id = Column(Integer, primary_key=True,autoincrement=True)
    app_name = Column(String)
    username = Column(String)
    password = Column(String)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    user = relationship("User", back_populates="credentials")
