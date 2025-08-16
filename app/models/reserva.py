from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class ReservaBase(BaseModel):
    paquete_id: int
    turista_id: Optional[int] = None
    fecha_inicio: date
    fecha_fin: date
    numero_personas: int = Field(..., gt=0, le=50)
    numero_adultos: int = Field(..., gt=0, le=50)
    numero_niños: int = Field(0, ge=0, le=20)
    precio_total: Decimal = Field(..., gt=0)
    precio_por_persona: Decimal = Field(..., gt=0)
    precio_niños: Decimal = Field(0, ge=0)
    # Información adicional
    necesidades_especiales: Optional[str] = None
    nivel_experiencia: Optional[str] = Field(None, pattern="^(principiante|intermedio|avanzado)$")
    notas_adicionales: Optional[str] = None
    # Estado de la reserva
    estado: Optional[str] = Field(None, pattern="^(pendiente|confirmada|cancelada|completada)$")
    # Información de pago
    metodo_pago: Optional[str] = None
    pagado: bool = False
    fecha_pago: Optional[datetime] = None

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    numero_personas: Optional[int] = Field(None, gt=0, le=50)
    numero_adultos: Optional[int] = Field(None, gt=0, le=50)
    numero_niños: Optional[int] = Field(None, ge=0, le=20)
    precio_total: Optional[Decimal] = Field(None, gt=0)
    precio_por_persona: Optional[Decimal] = Field(None, gt=0)
    precio_niños: Optional[Decimal] = Field(None, ge=0)
    # Información adicional
    necesidades_especiales: Optional[str] = None
    nivel_experiencia: Optional[str] = Field(None, pattern="^(principiante|intermedio|avanzado)$")
    notas_adicionales: Optional[str] = None
    # Estado de la reserva
    estado: Optional[str] = Field(None, pattern="^(pendiente|confirmada|cancelada|completada)$")
    # Información de pago
    metodo_pago: Optional[str] = None
    pagado: Optional[bool] = None
    fecha_pago: Optional[datetime] = None

class Reserva(ReservaBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

class ReservaResponse(Reserva):
    # Campos adicionales para la respuesta
    paquete_titulo: Optional[str] = None
    paquete_tipo: Optional[str] = None
    paquete_imagen_principal: Optional[str] = None
    paquete_duracion_dias: Optional[int] = None
    operador_nombre: Optional[str] = None
    operador_apellido: Optional[str] = None
    turista_nombre: Optional[str] = None
    turista_apellido: Optional[str] = None
    dias_totales: Optional[int] = None

class ReservaFiltros(BaseModel):
    paquete_id: Optional[int] = None
    turista_id: Optional[int] = None
    operador_id: Optional[int] = None
    estado: Optional[str] = None
    tipo_paquete: Optional[str] = None
    fecha_inicio_desde: Optional[date] = None
    fecha_inicio_hasta: Optional[date] = None
    fecha_fin_desde: Optional[date] = None
    fecha_fin_hasta: Optional[date] = None
    pagado: Optional[bool] = None
    metodo_pago: Optional[str] = None
    nivel_experiencia: Optional[str] = None 