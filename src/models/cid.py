from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base


class CID(Base):
    __tablename__ = "cid"

    codigo = Column(String, primary_key=True)
    descricao = Column(String, nullable=True)
    cronico = Column(Boolean, nullable=True)
    data_criacao = Column(DateTime, server_default=func.now())
