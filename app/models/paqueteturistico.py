from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class PaqueteTuristicoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    tipo_paquete: str = Field(..., pattern="^(aventura|cultural|gastronomico|playa|montaña|ciudad|ecoturismo|romantico|familiar|negocios)$")
    duracion_dias: int = Field(..., gt=0, le=30)
    capacidad_maxima: int = Field(..., gt=0, le=50)
    nivel_dificultad: str = Field(..., pattern="^(facil|moderado|dificil|extremo)$")
    precio_por_persona: Decimal = Field(..., gt=0)
    precio_niño: Decimal = Field(0, ge=0)  # Precio especial para niños
    incluye_transporte: bool = False
    incluye_alojamiento: bool = False
    incluye_comidas: bool = False
    incluye_guia: bool = False
    # Ubicación
    pais_destino: str = Field(..., min_length=1, max_length=100)
    ciudad_destino: str = Field(..., min_length=1, max_length=100)
    punto_encuentro: str = Field(..., min_length=1, max_length=500)
    latitud: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitud: Optional[Decimal] = Field(None, ge=-180, le=180)
    # Horarios y políticas
    hora_inicio: str = Field(default="09:00", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    hora_fin: str = Field(default="18:00", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    edad_minima: int = Field(0, ge=0, le=100)
    requiere_experiencia: bool = False
    permite_cancelacion: bool = True
    dias_cancelacion: int = Field(7, ge=0, le=30)  # Días antes para cancelar sin penalización
    # Servicios incluidos
    servicios_incluidos: Optional[str] = None  # JSON string

class PaqueteTuristicoCreate(PaqueteTuristicoBase):
    operador_id: int  # Cambio de anfitrion_id a operador_id
    imagenes: Optional[List[str]] = None  # Lista de imágenes en base64

class PaqueteTuristicoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    tipo_paquete: Optional[str] = Field(None, pattern="^(aventura|cultural|gastronomico|playa|montaña|ciudad|ecoturismo|romantico|familiar|negocios)$")
    duracion_dias: Optional[int] = Field(None, gt=0, le=30)
    capacidad_maxima: Optional[int] = Field(None, gt=0, le=50)
    nivel_dificultad: Optional[str] = Field(None, pattern="^(facil|moderado|dificil|extremo)$")
    precio_por_persona: Optional[Decimal] = Field(None, gt=0)
    precio_niño: Optional[Decimal] = Field(None, ge=0)
    incluye_transporte: Optional[bool] = None
    incluye_alojamiento: Optional[bool] = None
    incluye_comidas: Optional[bool] = None
    incluye_guia: Optional[bool] = None
    # Ubicación
    pais_destino: Optional[str] = Field(None, min_length=1, max_length=100)
    ciudad_destino: Optional[str] = Field(None, min_length=1, max_length=100)
    punto_encuentro: Optional[str] = Field(None, min_length=1, max_length=500)
    latitud: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitud: Optional[Decimal] = Field(None, ge=-180, le=180)
    # Estado
    esta_activo: Optional[bool] = None
    # Horarios y políticas
    hora_inicio: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    hora_fin: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    edad_minima: Optional[int] = Field(None, ge=0, le=100)
    requiere_experiencia: Optional[bool] = None
    permite_cancelacion: Optional[bool] = None
    dias_cancelacion: Optional[int] = Field(None, ge=0, le=30)
    # Servicios incluidos
    servicios_incluidos: Optional[str] = None

class PaqueteTuristico(PaqueteTuristicoBase):
    id: int
    operador_id: int  # Cambio de anfitrion_id a operador_id
    esta_activo: bool = True  # Cambio de esta_activa a esta_activo
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

class PaqueteTuristicoResponse(PaqueteTuristico):
    # Campos adicionales para la respuesta
    operador_nombre: Optional[str] = None
    operador_apellido: Optional[str] = None
    operador_avatar: Optional[str] = None
    calificacion_promedio: Optional[float] = None
    total_reviews: Optional[int] = None
    imagenes: Optional[List[str]] = None
    es_favorito: Optional[bool] = None

class PaqueteTuristicoFiltros(BaseModel):
    pais_destino: Optional[str] = None
    ciudad_destino: Optional[str] = None
    tipo_paquete: Optional[str] = None
    duracion_min: Optional[int] = None
    duracion_max: Optional[int] = None
    capacidad_minima: Optional[int] = None
    precio_min: Optional[Decimal] = None
    precio_max: Optional[Decimal] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nivel_dificultad: Optional[str] = None
    incluye_transporte: Optional[bool] = None
    incluye_alojamiento: Optional[bool] = None
    incluye_comidas: Optional[bool] = None
    incluye_guia: Optional[bool] = None
    edad_minima_max: Optional[int] = None  # Filtrar por edad máxima permitida
    servicios_incluidos: Optional[List[str]] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    radio_km: Optional[int] = None 