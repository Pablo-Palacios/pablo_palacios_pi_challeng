from fastapi import FastAPI
from routers.router import router
from fastapi.middleware.cors import CORSMiddleware
from models.views import generate_embeddings_all
from models.config import redis_client,collection
from models.model import convertir_embeddigns


app = FastAPI()

app.include_router(router, prefix="/api", tags=["Endpoints"])

@app.on_event("startup")
async def on_data():
    print("Iniciando API - Activando embeddings...")
    try:
        generate_embeddings_all(redis_client, convertir_embeddigns, collection)
    except Exception as e:
        raise SystemError(f"Error al cargar embeddings: {e}")
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)