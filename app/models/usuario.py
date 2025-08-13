from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    genero: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_operador: bool = False
    es_verificado: bool = False
    avatar_url: Optional[str] = None
    descripcion_perfil: Optional[str] = None
    idiomas: Optional[str] = None  # JSON string
    respuesta_tiempo_horas: Optional[int] = None

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=100)

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    genero: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_operador: Optional[bool] = None
    avatar_url: Optional[str] = None
    descripcion_perfil: Optional[str] = None
    idiomas: Optional[str] = None
    respuesta_tiempo_horas: Optional[int] = None

class Usuario(UsuarioBase):
    id: int
    fecha_registro: datetime
    ultimo_acceso: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UsuarioResponse(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    genero: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_operador: bool
    es_verificado: bool
    avatar_url: Optional[str] = None
    descripcion_perfil: Optional[str] = None
    idiomas: Optional[str] = None
    respuesta_tiempo_horas: Optional[int] = None
    fecha_registro: datetime
    ultimo_acceso: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None 