"""
Aplicación FastAPI de SIGNA.
"""

from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title = "SIGNA API",
    description = "Sistema inteligente de triaje de incidencias de telecomunicaciones.",
    version = "1.0.0", 
)

app.include_router(router)