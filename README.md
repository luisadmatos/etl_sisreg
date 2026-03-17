# ETL SISREG

Pipeline de **Extract, Transform e Load (ETL)** que consome dados da API pública do **SISREG** (Sistema de Regulação do SUS), trata os registros e grava em um banco **PostgreSQL** rodando em **Docker**.

---

## O que este projeto faz

- **Extract:** Busca dados paginados da API do SISREG (solicitações ambulatoriais por UF e município).
- **Transform:** Valida e normaliza os dados (datas, CID, campos obrigatórios) e monta registros de pacientes, unidades, CID e solicitações.
- **Load:** Insere os dados no PostgreSQL, criando ou reutilizando pacientes, unidades e CIDs e evitando duplicar solicitações pelo `codigo_solicitacao`.

O banco é usado **somente via Docker**; a aplicação Python roda na sua máquina e se conecta ao container.

---

## Pré-requisitos

Antes de clonar e rodar, tenha instalado:

| Ferramenta | Versão sugerida | Onde baixar |
|------------|-----------------|-------------|
| **Python** | 3.11 ou 3.12 | [python.org](https://www.python.org/downloads/) |
| **Docker Desktop** | Última estável | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |

- **Python 3.14** pode dar problema em alguns pacotes; prefira 3.11 ou 3.12.
- **Docker Desktop** deve estar **aberto e em execução** (ícone na bandeja do sistema) antes de subir o banco.

---

## Estrutura do projeto

```
.
├── main.py              # Ponto de entrada do pipeline ETL
├── requirements.txt     # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente (copiar para .env)
├── docker-compose.yml    # Serviço PostgreSQL em Docker
├── src/
│   ├── config.py         # Configurações (DATABASE_URL, API SISREG)
│   ├── database.py       # Conexão SQLAlchemy com o banco
│   ├── extract.py        # Extração da API SISREG (paginação)
│   ├── transform.py      # Transformação e validação dos dados
│   ├── load.py           # Carga no PostgreSQL (pacientes, unidades, CID, solicitações)
│   └── models/           # Modelos SQLAlchemy (Paciente, Unidade, CID, Solicitacao)
└── scripts/
    └── init_db.py        # Cria as tabelas no banco (rodar uma vez)
```

---

## Como rodar na sua máquina (passo a passo)

Siga a ordem abaixo. Qualquer passo pulado pode gerar erro na primeira execução.

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd etl_sisreg
```

Substitua `<url-do-repositorio>` pela URL real do repositório (SSH ou HTTPS).

---

### 2. Criar e ativar o ambiente virtual (venv)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

O prompt deve mostrar `(venv)` indicando que o ambiente está ativo.

---

### 3. Instalar as dependências Python

Com o venv ativado, na raiz do projeto:

```bash
pip install -r requirements.txt
```

Se der erro com `psycopg` em Python 3.14, use Python 3.11 ou 3.12 no venv.

---

### 4. Configurar a variável de ambiente do banco

O projeto **não** usa configuração de banco fixa no código. A URL do banco vem da variável de ambiente **`DATABASE_URL`**. A forma mais simples é usar um arquivo **`.env`** na raiz do projeto.

**Criar o arquivo `.env` a partir do exemplo:**

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Windows (CMD):**

```cmd
copy .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

O `.env.example` já traz a URL correta para o Postgres do Docker (usuário `postgres`, senha `password`, banco `sisreg`, host `localhost`, porta `5432`). Só altere o `.env` se você mudar usuário/senha no `docker-compose.yml`.

---

### 5. Subir o PostgreSQL com Docker

Na raiz do projeto:

```bash
docker-compose up -d
```

Isso sobe o container **sisreg-postgres** na porta **5432** e cria o banco **sisreg**. Os dados ficam persistidos em um volume Docker.

**Conferir se o container está rodando:**

```bash
docker ps
```

Deve aparecer um container com a imagem `postgres:16` e a porta `0.0.0.0:5432->5432/tcp`.

---

### 6. Criar as tabelas no banco (primeira vez)

As tabelas não são criadas automaticamente. Rode **uma vez** o script de inicialização:

```bash
python scripts/init_db.py
```

Saída esperada: `Tabelas criadas com sucesso!`

Se aparecer erro de conexão (por exemplo `password authentication failed`), confira:

- O container está de pé (`docker ps`).
- O `.env` existe na raiz e contém `DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/sisreg` (senha igual à do `docker-compose.yml`: `password`).

---

### 7. Rodar o pipeline ETL

Com o banco no ar e as tabelas criadas:

```bash
python main.py
```

O script vai:

1. Buscar dados da API do SISREG (UF e município configurados em `src/config.py`: MS, 500830).
2. Transformar e validar os registros.
3. Inserir no PostgreSQL (evitando duplicar solicitações já existentes).

Para **testar com poucas páginas** (recomendado na primeira vez):

```bash
python -c "from main import main; main(paginated=True, page_size=10, max_pages=1)"
```

Isso processa apenas 1 página com até 10 registros.

---

## Resumo rápido dos comandos (ordem)

```bash
git clone <url>
cd etl_sisreg
python -m venv venv
# Ativar o venv (comando depende do OS; veja passo 2)
pip install -r requirements.txt
cp .env.example .env          # ou Copy-Item no PowerShell
docker-compose up -d
python scripts/init_db.py
python main.py
```

---

## Configurações opcionais

- **UF e município:** Em `src/config.py` estão `UF = "MS"` e `MUNICIPIO = "500830"`. Altere se quiser outro estado/município na API do SISREG.
- **Paginação:** Em `main.py`, no `if __name__ == "__main__"`, você pode mudar `page_size` e `max_pages` (ou `None` para processar todas as páginas).

---

## Problemas comuns

| Erro | Causa provável | O que fazer |
|------|----------------|-------------|
| `RuntimeError: Defina a variável de ambiente DATABASE_URL` | Arquivo `.env` não existe ou não está na raiz do projeto. | Criar `.env` a partir de `.env.example` (passo 4). |
| `password authentication failed for user "postgres"` | Senha no `.env` diferente da do container. | Usar no `.env` a mesma senha do `docker-compose.yml` (`password`) ou ajustar o `POSTGRES_PASSWORD` no compose para bater com o `.env`. |
| `connection refused` / `could not connect to server` | Postgres não está rodando ou porta errada. | Rodar `docker-compose up -d` e conferir `docker ps`. Verificar se a porta no `.env` é `5432`. |
| Porta 5432 já em uso | Outro PostgreSQL (ou serviço) usando 5432. | Parar o outro serviço ou alterar no `docker-compose.yml` a porta externa (ex.: `"5433:5432"`) e no `.env` usar `localhost:5433`. |
| `ModuleNotFoundError: sqlalchemy` (ou outro) | Dependências não instaladas ou venv inativo. | Ativar o venv e rodar `pip install -r requirements.txt` (passo 3). |

---

## Parar o banco e remover dados (opcional)

Parar os containers:

```bash
docker-compose down
```

Parar e **apagar o volume** (apaga todos os dados do banco):

```bash
docker-compose down -v
```

---

## Licença e uso

Projeto para uso no contexto do PET Digital / SISREG. Ajuste UF/município e credenciais conforme o ambiente de uso.
