import sys

sys.path.insert(0, ".")

from src.database import engine, Base
from src.models import Paciente, Unidade, CID, Solicitacao

def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Tabelas criadas com sucesso!")