from fastapi import FastAPI
from .api.routes import router as api_router
from .config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "version": settings.APP_VERSION}
