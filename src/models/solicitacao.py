from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    codigo_solicitacao = Column(String, unique=True, nullable=False)

    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    cid = Column(String, ForeignKey("cid.codigo"), nullable=False)

    classificacao_risco = Column(String, nullable=True)
    laudo = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    data_solicitacao = Column(DateTime, nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    paciente = relationship("Paciente", back_populates="solicitacoes")
    unidade = relationship("Unidade", back_populates="solicitacoes")
