import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

logger = logging.getLogger(__name__)

try:
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    SessionLocal = Session
    Base = declarative_base()
    logger.info("Conexão com banco configurada")
except Exception as e:
    logger.error(f"Erro ao configurar banco: {e}")
    raise