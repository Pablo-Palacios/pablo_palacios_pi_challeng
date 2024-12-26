from fastapi import FastAPI
from routers.router import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(router, prefix="/api", tags=["Endpoints"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)