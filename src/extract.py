import requests
import logging
from .config import BASE_URL, UF, MUNICIPIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def _create_session_with_retries(retries=3):
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_data_paginated(page_size=100, max_pages=None, retries=3):

    base_url = BASE_URL.format(UF=UF, MUNICIPIO=MUNICIPIO)
    page = 0
    total_fetched = 0
    
    session = _create_session_with_retries(retries)
    
    try:
        while True:
            # Verificar limite de páginas
            if max_pages and page >= max_pages:
                logger.info(f"Limite de {max_pages} páginas atingido")
                break
            
            # Montar URL com paginação
            url = f"{base_url}?page={page}&size={page_size}"
            logger.info(f"Fetching página {page + 1}... ({url})")
            
            try:
                response = session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Se não há dados, parar
                if not data or not data.get("hits", {}).get("hits"):
                    logger.info(f"Fim dos dados. Total: {total_fetched} registros")
                    break
                
                hits = data.get("hits", {}).get("hits", [])
                total_fetched += len(hits)
                
                logger.info(f"Página {page + 1}: {len(hits)} registros (Total: {total_fetched})")
                
                # Retornar página (yield para processar pouco em pouco)
                yield data
                
                page += 1
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout na página {page + 1}")
                raise
            except requests.exceptions.HTTPError as e:
                logger.error(f"Erro HTTP {e.response.status_code} na página {page + 1}")
                raise
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados: {e}")
        raise


def fetch_data(retries=3):
    
    url = BASE_URL.format(UF=UF, MUNICIPIO=MUNICIPIO)
    logger.info(f"Fazendo requisição para: {url}")
    
    session = _create_session_with_retries(retries)
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        logger.info("Dados extraídos com sucesso")
        return response.json()
        
    except requests.exceptions.Timeout:
        logger.error("Timeout na requisição")
        return None
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP: {e.response.status_code}")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        return None
        return None
