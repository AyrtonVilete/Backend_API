from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 200


class GenerateResponse(BaseModel):
    result: str
