from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class DisponibilidadBase(BaseModel):
    paquete_id: int
    fecha: date
    disponible: bool = True
    precio_especial: Optional[Decimal] = Field(None, description="Precio especial para esta fecha específica")
    cupos_disponibles: Optional[int] = Field(None, ge=0, description="Número de cupos disponibles para esta fecha")
    
class DisponibilidadCreate(DisponibilidadBase):
    pass

class DisponibilidadUpdate(BaseModel):
    disponible: Optional[bool] = None
    precio_especial: Optional[Decimal] = Field(None, ge=0)
    cupos_disponibles: Optional[int] = Field(None, ge=0)

class Disponibilidad(DisponibilidadBase):
    id: int
    
    class Config:
        from_attributes = True

class DisponibilidadResponse(Disponibilidad):
    # Campos adicionales para la respuesta enriquecida
    paquete_titulo: Optional[str] = None
    paquete_tipo: Optional[str] = None
    precio_base_por_persona: Optional[Decimal] = None
    capacidad_maxima_paquete: Optional[int] = None
    operador_nombre: Optional[str] = None

class DisponibilidadFiltros(BaseModel):
    paquete_id: Optional[int] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    disponible: Optional[bool] = None
    tipo_paquete: Optional[str] = Field(None, description="Filtrar por tipo de paquete turístico")
    precio_max: Optional[Decimal] = Field(None, ge=0, description="Precio máximo por persona")
    cupos_minimos: Optional[int] = Field(None, ge=1, description="Mínimo de cupos disponibles requeridos")

class DisponibilidadMasiva(BaseModel):
    """Modelo para crear disponibilidad en múltiples fechas"""
    paquete_id: int
    fecha_inicio: date
    fecha_fin: date
    disponible: bool = True
    precio_especial: Optional[Decimal] = None
    cupos_disponibles: Optional[int] = None
    excluir_fechas: Optional[list[date]] = Field(default_factory=list, description="Fechas a excluir del rango")
    solo_fines_semana: Optional[bool] = Field(False, description="Solo crear disponibilidad para fines de semana")
    solo_dias_laborales: Optional[bool] = Field(False, description="Solo crear disponibilidad para días laborales") 