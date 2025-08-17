from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

import logging
import os

from app.config import settings
from app.database import db
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.usuarios import router as usuarios_router
from app.api.paqueteturistico import router as paquetes_turisticos_router
from app.api.reservas import router as reservas_router
from app.api.reviews import router as reviews_router
from app.api.favoritos import router as favoritos_router
from app.postman_generator import router as postman_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación Sistema de Paquetes Turísticos API...")
    
    # Verificar conexión a SQLite
    try:
        if db.health_check():
            logger.info("Conexión a SQLite establecida correctamente")
        else:
            logger.error("Error al conectar con SQLite")
    except Exception as e:
        logger.error(f"Error crítico al conectar con SQLite: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación Sistema de Paquetes Turísticos API...")
    db.close()


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Paquetes Turísticos",
    version=settings.app_version,
    description="API completa para la gestión de paquetes turísticos con autenticación JWT y base de datos SQLite. Permite a operadores turísticos crear y gestionar paquetes, y a turistas hacer reservas y valoraciones.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejar excepciones globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones globales"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Maneja excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Endpoint de salud
@app.get("/health")
async def health_check():
    """Endpoint de salud de la aplicación"""
    try:
        db_healthy = db.health_check()
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "version": settings.app_version,
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "version": settings.app_version,
            "environment": settings.environment,
            "error": str(e)
        }

# Endpoint raíz
@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido al Sistema de Paquetes Turísticos API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "postman": {
            "download": "/postman/download"
        }
    }

# Incluir routers
app.include_router(auth_router)
app.include_router(usuarios_router, prefix="/usuarios")
app.include_router(paquetes_turisticos_router)
app.include_router(reservas_router)
app.include_router(reviews_router)
app.include_router(favoritos_router, prefix="/favoritos")
app.include_router(postman_router)

# Crear directorio de uploads si no existe
os.makedirs(settings.upload_dir, exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Obtener la IP local
    def get_local_ip():
        try:
            # Conectar a un socket para obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    local_ip = get_local_ip()
    
    print("Iniciando servidor...")
    print(f"IP Local: http://{local_ip}:{settings.port}")
    print(f"Localhost: http://localhost:{settings.port}")
    print(f"Documentación: http://{local_ip}:{settings.port}/docs")
    print(f"Postman Download: http://{local_ip}:{settings.port}/postman/download")
    print(f"Modo Debug: {'Activado' if settings.debug else 'Desactivado'}")
    print(f"Entorno: {settings.environment}")
    print("-" * 70)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 