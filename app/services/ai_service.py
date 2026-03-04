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
app = FastAPI(title="API - SQL Smart Migrator AI", version="1.2")

# 4. Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Define os formatos de JSON que a API vai receber
class RequisicaoChat(BaseModel):
    mensagem_usuario: str

class RequisicaoSQL(BaseModel):
    mensagem_usuario: str
    schema_banco: str

# 6. O Prompt de Sistema para o Chat (Geral)
PROMPT_SISTEMA = """
Você é um Arquiteto de Dados Sênior e Assistente Virtual do sistema 'SQL Smart Migrator'.
Seu objetivo é ajudar o usuário a escrever queries, otimizar migrações de dados e resolver erros de banco de dados.

Regras estritas:
1. O sistema suporta SQL Server, MySQL e PostgreSQL. Sempre que der um exemplo de código, especifique para qual banco é.
2. Seja direto e técnico. Não use saudações longas.
3. Foque em performance de migração (ETL), tipos de dados e tratamento de chaves primárias/estrangeiras.
4. Se o usuário perguntar algo que não seja sobre banco de dados, programação ou migração, diga educadamente que você só pode ajudar com o SQL Smart Migrator.
"""

# ==========================================
# 🤖 ROTA 1: CHAT GERAL DE IA
# ==========================================
@app.post("/chat")
async def conversar_com_ia(requisicao: RequisicaoChat):
    try:
        configuracao_ia = types.GenerateContentConfig(
            system_instruction=PROMPT_SISTEMA,
            temperature=0.2, 
        )
        
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=requisicao.mensagem_usuario,
            config=configuracao_ia
        )
        
        return {"resposta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")


# ==========================================
# ⚡ ROTA 2: GERADOR DE SQL AUTOMÁTICO (TEXT-TO-SQL)
# ==========================================
@app.post("/gerar-sql")
async def gerar_sql_ia(requisicao: RequisicaoSQL):
    try:
        # A "camisa de força" para garantir que a IA retorne apenas código
        instrucao_sistema_sql = (
            "Você é um Engenheiro de Dados Sênior especialista em SQL. "
            "Sua única função é gerar queries SQL válidas baseadas EXCLUSIVAMENTE no schema de tabelas fornecido. "
            "REGRA DE OURO: Retorne APENAS o código SQL puro. Não escreva 'Aqui está', não dê explicações "
            "e NÃO use formatação markdown (como ```sql). Retorne apenas a string da query pronta para execução no banco."
        )
        
        # Temperatura 0.1 para ser extremamente técnico e previsível
        configuracao_ia_sql = types.GenerateContentConfig(
            system_instruction=instrucao_sistema_sql,
            temperature=0.1,
        )
        
        # Junta o mapa do banco com o pedido do usuário
        prompt_completo = f"--- SCHEMA DO BANCO DE DADOS ---\n{requisicao.schema_banco}\n\n--- PEDIDO DO USUÁRIO ---\n{requisicao.mensagem_usuario}"
        
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_completo,
            config=configuracao_ia_sql
        )
        
        # Limpa resquícios de markdown caso a IA desobedeça
        sql_limpo = response.text.replace("```sql", "").replace("```", "").strip()
        
        return {"sql": sql_limpo}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA ao gerar SQL: {str(e)}")


# Rota de teste simples
@app.get("/")
def home():
    return {"status": "API da IA do Migrador está Online e Otimizada (v1.2)! 🚀"}