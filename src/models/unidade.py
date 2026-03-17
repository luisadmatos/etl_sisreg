from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nome = Column(String, nullable=False)
    codigo_central = Column(String, unique=True, nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())

    solicitacoes = relationship("Solicitacao", back_populates="unidade")
