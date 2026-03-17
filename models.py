from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    cpf = Column(String(11), unique=True, nullable=True)
    sexo = Column(String(1), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    endereco = Column(String, nullable=True)
    bairro = Column(String, nullable=True)
    data_criacao = Column(DateTime, server_default=func.now())

    solicitacoes = relationship("Solicitacao", back_populates="paciente")
    
    # Índice composto para queries frequentes
    __table_args__ = (Index('idx_paciente_data_sexo', 'data_nascimento', 'sexo'),)

class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    nome = Column(String, nullable=False)
    codigo_central = Column(String, unique=True, nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())

    solicitacoes = relationship("Solicitacao", back_populates="unidade")

class CID(Base):
    __tablename__ = "cid"

    codigo = Column(String, primary_key=True)
    descricao = Column(String, nullable=True)
    cronico = Column(Boolean, nullable=True)
    data_criacao = Column(DateTime, server_default=func.now())

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
