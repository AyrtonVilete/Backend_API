from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types # <--- Importante para configurar a IA
import os
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env
load_dotenv()
CHAVE_API = os.getenv("GEMINI_API_KEY")

if not CHAVE_API:
    raise ValueError("Chave da API do Gemini não encontrada no arquivo .env!")

# 2. Configura o Cliente
client = genai.Client(api_key=CHAVE_API)

# 3. Inicia a API
app = FastAPI(title="API - SQL Smart Migrator AI", version="1.1")

# 4. Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Define o formato do JSON que a API vai receber
class RequisicaoChat(BaseModel):
    mensagem_usuario: str

# 6. O Prompt de Sistema (Agora isolado e muito mais forte)
PROMPT_SISTEMA = """
Você é um Arquiteto de Dados Sênior e Assistente Virtual do sistema 'SQL Smart Migrator'.
Seu objetivo é ajudar o usuário a escrever queries, otimizar migrações de dados e resolver erros de banco de dados.

Regras estritas:
1. O sistema suporta SQL Server, MySQL e PostgreSQL. Sempre que der um exemplo de código, especifique para qual banco é.
2. Seja direto e técnico. Não use saudações longas.
3. Foque em performance de migração (ETL), tipos de dados e tratamento de chaves primárias/estrangeiras.
4. Se o usuário perguntar algo que não seja sobre banco de dados, programação ou migração, diga educadamente que você só pode ajudar com o SQL Smart Migrator.
"""

# 7. A Rota principal da API (Agora 100% Assíncrona e Otimizada)
@app.post("/chat")
async def conversar_com_ia(requisicao: RequisicaoChat):
    try:
        # --- Configuração de Comportamento da IA ---
        configuracao_ia = types.GenerateContentConfig(
            system_instruction=PROMPT_SISTEMA,
            temperature=0.2, # Deixa a IA mais precisa, lógica e menos "inventiva" (ideal para código/SQL)
        )
        
        # Faz a chamada usando o cliente Assíncrono (.aio)
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=requisicao.mensagem_usuario,
            config=configuracao_ia
        )
        
        return {"resposta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")

# Rota de teste simples
@app.get("/")
def home():
    return {"status": "API da IA do Migrador está Online e Otimizada! 🚀"}