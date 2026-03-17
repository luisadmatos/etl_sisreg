import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError) as e:
        logger.warning(f"Erro ao parsear data '{date_str}': {e}")
        return None


def normalize_cid(cid):
    if not cid:
        return None
    normalized = cid.strip().upper()
    if len(normalized) < 3:
        logger.warning(f"CID inválido (muito curto): {cid}")
        return None
    return normalized


def transform(data): 
    if not data:
        logger.warning("Dados vazios recebidos")
        return []
    
    registros = []
    erros = 0
    
    hits = data.get("hits", {}).get("hits", [])
    
    if not hits:
        logger.warning("Nenhum hit encontrado na resposta")
        return []

    for item in hits:
        try:
            r = item.get("_source", {})

            if not r.get("codigo_solicitacao"):
                logger.warning("Registro sem codigo_solicitacao")
                erros += 1
                continue

            if not r.get("data_solicitacao"):
                logger.warning(f"Registro {r.get('codigo_solicitacao')} sem data_solicitacao")
                erros += 1
                continue

            # CID é crítico - validar aqui antes de prosseguir
            cid = normalize_cid(r.get("codigo_cid_solicitado"))
            if not cid:
                logger.warning(f"Registro {r.get('codigo_solicitacao')} com CID inválido")
                erros += 1
                continue

            registro = {
                "codigo_solicitacao": r.get("codigo_solicitacao"),
                "sexo": r.get("sexo_usuario"),
                "data_nascimento": parse_date(r.get("dt_nascimento_usuario")),
                "endereco": r.get("endereco_paciente_residencia"),
                "bairro": r.get("bairro_paciente_residencia"),
                "codigo_central": r.get("codigo_central_solicitante"),
                "nome_unidade": r.get("nome_unidade_solicitante"),
                "cid": cid,
                "classificacao_risco": r.get("codigo_classificacao_risco"),
                "laudo": r.get("laudo"),
                "status": r.get("status_solicitacao"),
                "data_solicitacao": parse_date(r.get("data_solicitacao")),
            }

            registros.append(registro)

        except Exception as e:
            logger.error(f"Erro ao transformar registro: {e}")
            erros += 1
            continue

    logger.info(f"Transform: {len(registros)} registros processados, {erros} erros")
    return registros