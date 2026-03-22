# AgendM

Sistema web multi-tenant em Django para gestao de fila por guiche, importacao incremental de planilhas e fluxo inteligente de atendimento.

## Stack
- Python 3.12+
- Django 4.2
- SQLite por padrao
- Pronto para migracao futura para PostgreSQL via variaveis de ambiente

## Como rodar localmente
1. Instale as dependencias: `pip install -r requirements.txt`
2. Gere/aplique migrations: `python manage.py makemigrations && python manage.py migrate`
3. Opcionalmente force o bootstrap do master: `python manage.py bootstrap_master`
4. Rode o servidor: `python manage.py runserver`
5. Acesse: `http://127.0.0.1:8000/accounts/login/`

## Usuario master inicial
- usuario: `demasantosdev`
- senha: `Dem@2026`

## Migracao futura para PostgreSQL
Defina:
- `DB_ENGINE=postgres`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

A modelagem ja usa recursos portaveis do Django ORM e nao depende de SQLite.
