# Backend Mock Local — Agente Consultivo MARH

Backend HTTP local que simula as dependências externas (ma-hr-orch, Bedrock, RAG)
para teste de integração com o frontend da POC.

## Requisitos

- Python 3.12+

## Setup

```powershell
cd C:\proj\discover_alelo\poc_marh_agent\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Executar o backend

```powershell
python -m uvicorn marh_agent.api.local_api:app --reload --port 8000
```

## Executar o frontend (em outro terminal)

```powershell
cd C:\proj\discover_alelo\poc_marh_agent\frontend
python -m http.server 8080
```

Abrir: http://localhost:8080/chat-alelo.html

## Executar testes

```powershell
pytest
```

## Endpoints

- `GET /health` — Health check
- `POST /chat` — Endpoint principal de chat

## Classificação: SYNTHETIC_TEST_DATA

Todos os dados são sintéticos. Nenhum dado real é utilizado.
