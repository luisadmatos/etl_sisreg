import logging
from database import SessionLocal
from models import Paciente, Unidade, Solicitacao, CID
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def get_or_create_cid(session, cid_codigo):
    if not cid_codigo:
        logger.warning("CID vazio fornecido")
        return None
    
    cid = session.query(CID).filter_by(codigo=cid_codigo).first()
    
    if not cid:
        cid = CID(codigo=cid_codigo)
        session.add(cid)
        session.flush()
    
    return cid


def get_or_create_paciente(session, r):
    if not r["data_nascimento"] or not r["sexo"]:
        logger.error(f"Paciente incompleto: data_nascimento={r['data_nascimento']}, sexo={r['sexo']}")
        return None

    paciente = session.query(Paciente).filter_by(
        data_nascimento=r["data_nascimento"],
        sexo=r["sexo"]
    ).first()

    if not paciente:
        paciente = Paciente(
            sexo=r["sexo"],
            data_nascimento=r["data_nascimento"],
            endereco=r["endereco"],
            bairro=r["bairro"]
        )
        session.add(paciente)
        session.flush()

    return paciente


def get_or_create_unidade(session, r):
    if not r["codigo_central"] or not r["nome_unidade"]:
        logger.error(f"Unidade incompleta: codigo={r['codigo_central']}, nome={r['nome_unidade']}")
        return None

    unidade = session.query(Unidade).filter_by(
        codigo_central=r["codigo_central"]
    ).first()

    if not unidade:
        unidade = Unidade(
            codigo_central=r["codigo_central"],
            nome=r["nome_unidade"]
        )
        session.add(unidade)
        session.flush()
    return unidade


def load_data(registros):
    if not registros:
        logger.warning("Nenhum registro para carregar")
        return {"inserted": 0, "skipped": 0}

    session = SessionLocal()
    insertados = 0
    pulados = 0

    try:
        for r in registros:
            exists = session.query(Solicitacao).filter_by(
                codigo_solicitacao=r["codigo_solicitacao"]
            ).first()

            if exists:
                pulados += 1
                continue

            # Criar/obter relacionados
            cid = get_or_create_cid(session, r["cid"])
            if not cid:
                pulados += 1
                continue

            paciente = get_or_create_paciente(session, r)
            if not paciente:
                pulados += 1
                continue

            unidade = get_or_create_unidade(session, r)
            if not unidade:
                pulados += 1
                continue

            # Criar solicitação
            solicitacao = Solicitacao(
                codigo_solicitacao=r["codigo_solicitacao"],
                paciente_id=paciente.id,
                unidade_id=unidade.id,
                cid=r["cid"],
                classificacao_risco=r["classificacao_risco"],
                laudo=r["laudo"],
                status=r["status"],
                data_solicitacao=r["data_solicitacao"]
            )

            session.add(solicitacao)
            insertados += 1

        session.commit()
        logger.info(f"Lote carregado: {insertados} inseridas, {pulados} puladas")

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Erro ao carregar dados: {e}")
        raise

    finally:
        session.close()
    
    return {"inserted": insertados, "skipped": pulados}