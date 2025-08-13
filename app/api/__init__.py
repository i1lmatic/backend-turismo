from .auth import router as auth_router
from .usuarios import router as usuarios_router
from .paqueteturistico import router as paquetes_turisticos_router
from .reservas import router as reservas_router
from .reviews import router as reviews_router
from .favoritos import router as favoritos_router

__all__ = [
    "auth_router",
    "usuarios_router", 
    "paquetes_turisticos_router",
    "reservas_router",
    "reviews_router",
    "favoritos_router"
] 