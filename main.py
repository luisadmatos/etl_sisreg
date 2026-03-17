import sys
import logging
from src.extract import fetch_data_paginated
from src.transform import transform
from src.load import load_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(paginated: bool = True, page_size: int = 100, max_pages: int = None):
    mode = "PAGINADO" if paginated else "SIMPLES"
    print("=" * 50)
    print(f"PIPELINE ETL SISREG ({mode})")
    print("=" * 50)
    
    try:
        total_inserted = 0
        total_skipped = 0
        page_count = 0
        
        print("\nEXTRACT + TRANSFORM + LOAD...\n")
        
        for page_data in fetch_data_paginated(page_size=page_size, max_pages=max_pages):
            page_count += 1
            
            # Transformar dados
            registros = transform(page_data)
            
            if not registros:
                print(f"Página {page_count}: nenhum registro válido")
                continue
            
            # Carregar dados
            resultado = load_data(registros)
            
            total_inserted += resultado['inserted']
            total_skipped += resultado['skipped']
            
            print(f"   Página {page_count}: {resultado['inserted']} inseridas, {resultado['skipped']} puladas")
        
        print("\n" + "=" * 50)
        print(f"Pipeline concluído com sucesso!")
        print(f"   Páginas processadas: {page_count}")
        print(f"   Total inseridas: {total_inserted}")
        print(f"   Total puladas: {total_skipped}")
        print("=" * 50)

    except Exception as e:
        logger.error(f"Erro fatal no pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main(
        paginated=True,      
        page_size=100,       
        max_pages=None      
    )