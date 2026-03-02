from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import os
import json
import io
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


# --- ROTA DE UPLOAD PARA O DRIVE VIA BOT ---
@app.post("/upload-drive")
async def upload_drive(file: UploadFile = File(...), folder_id: str = Form(...)):
    try:
        # Pega o JSON do bot das variáveis de ambiente do Render
        cred_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not cred_json_str:
            raise HTTPException(status_code=500, detail="Credenciais do bot não configuradas no servidor.")
            
        # Transforma a string de volta em JSON
        cred_info = json.loads(cred_json_str)
        
        # Autentica como o Bot (Service Account)
        credentials = service_account.Credentials.from_service_account_info(
            cred_info, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Conecta no Drive
        service = build('drive', 'v3', credentials=credentials)
        
        # Lê o arquivo que chegou do Streamlit
        conteudo = await file.read()
        fh = io.BytesIO(conteudo)
        
        # Prepara e envia o arquivo para a pasta especificada
        media = MediaIoBaseUpload(fh, mimetype=file.content_type, resumable=True)
        file_metadata = {'name': file.filename, 'parents': [folder_id]}
        
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return {"status": "sucesso", "file_id": uploaded_file.get('id')}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")