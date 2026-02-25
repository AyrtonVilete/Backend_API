# API para IA (FastAPI)

Projeto inicial com FastAPI para expor endpoints de geração de texto via um serviço de IA.

Instalação (venv recomendado):

```bash
python -m venv .venv
\.\.venv\\Scripts\\activate
pip install -r requirements.txt
```

Rodar localmente:

```bash
uvicorn app.services.ai_service:app --reload --port 8000
```

Exemplo de uso (curl):

```bash
curl -X POST http://localhost:8000/api/generate -H "Content-Type: application/json" -d '{"prompt":"Olá mundo"}'
```

Configuração: copie `.env.example` para `.env` e defina `OPENAI_API_KEY` se desejar usar OpenAI.
