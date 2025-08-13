from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FavoritoBase(BaseModel):
    usuario_id: int
    paquete_id: int

class FavoritoCreate(FavoritoBase):
    pass

class Favorito(FavoritoBase):
    id: int
    fecha_agregado: datetime
    
    class Config:
        from_attributes = True

class FavoritoResponse(Favorito):
    # Campos adicionales para la respuesta
    paquete_titulo: Optional[str] = None
    paquete_tipo: Optional[str] = None
    paquete_imagen_principal: Optional[str] = None
    paquete_precio_por_persona: Optional[float] = None
    paquete_duracion_dias: Optional[int] = None
    paquete_nivel_dificultad: Optional[str] = None
    paquete_destino: Optional[str] = None
    operador_nombre: Optional[str] = None
    operador_apellido: Optional[str] = None 