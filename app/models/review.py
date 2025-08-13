from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    reserva_id: int
    autor_id: int
    paquete_id: int
    calificacion: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None
    # Categorías específicas para paquetes turísticos (coinciden con base de datos)
    organizacion: Optional[int] = Field(None, ge=1, le=5)
    comunicacion: Optional[int] = Field(None, ge=1, le=5)
    actividades: Optional[int] = Field(None, ge=1, le=5)
    guia: Optional[int] = Field(None, ge=1, le=5)
    seguridad: Optional[int] = Field(None, ge=1, le=5)
    valor: Optional[int] = Field(None, ge=1, le=5)

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    calificacion: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = None
    organizacion: Optional[int] = Field(None, ge=1, le=5)
    comunicacion: Optional[int] = Field(None, ge=1, le=5)
    actividades: Optional[int] = Field(None, ge=1, le=5)
    guia: Optional[int] = Field(None, ge=1, le=5)
    seguridad: Optional[int] = Field(None, ge=1, le=5)
    valor: Optional[int] = Field(None, ge=1, le=5)

class Review(ReviewBase):
    id: int
    fecha_review: datetime
    
    class Config:
        from_attributes = True

class ReviewResponse(Review):
    # Campos adicionales para la respuesta
    autor_nombre: Optional[str] = None
    autor_apellido: Optional[str] = None
    autor_avatar: Optional[str] = None
    paquete_titulo: Optional[str] = None
    paquete_tipo: Optional[str] = None
    reserva_fecha_inicio: Optional[datetime] = None
    reserva_fecha_fin: Optional[datetime] = None

class ReviewFiltros(BaseModel):
    paquete_id: Optional[int] = None
    autor_id: Optional[int] = None
    reserva_id: Optional[int] = None
    calificacion_min: Optional[int] = Field(None, ge=1, le=5)
    calificacion_max: Optional[int] = Field(None, ge=1, le=5)
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None 