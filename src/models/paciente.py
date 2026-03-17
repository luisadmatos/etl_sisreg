from sqlalchemy import Column, Integer, String, DateTime, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


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

    __table_args__ = (Index("idx_paciente_data_sexo", "data_nascimento", "sexo"),)
