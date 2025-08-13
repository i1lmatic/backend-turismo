from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models.paqueteturistico import PaqueteTuristicoResponse, PaqueteTuristicoCreate, PaqueteTuristicoUpdate, PaqueteTuristicoFiltros
from app.models.usuario import UsuarioResponse
from app.repositories.instances import paquete_turistico_repository
from app.auth.auth_handler import auth_handler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/paquetes-turisticos", tags=["Paquetes Turísticos"])

@router.post("/", response_model=PaqueteTuristicoResponse, status_code=status.HTTP_201_CREATED)
async def create_paquete_turistico(
    paquete_data: PaqueteTuristicoCreate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Crea un nuevo paquete turístico"""
    try:
        # Verificar que el usuario sea operador turístico
        if not current_user.es_operador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los operadores turísticos pueden crear paquetes"
            )
        
        # Asignar el operador actual
        paquete_data.operador_id = current_user.id
        
        paquete = await paquete_turistico_repository.create_paquete_turistico(paquete_data)
        return paquete
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear paquete turístico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[PaqueteTuristicoResponse])
async def get_paquetes_turisticos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Optional[UsuarioResponse] = Depends(auth_handler.get_current_user)
):
    """Obtiene todos los paquetes turísticos activos"""
    try:
        user_id = str(current_user.id) if current_user else None
        paquetes = await paquete_turistico_repository.get_all_paquetes_turisticos(skip, limit, user_id)
        return paquetes
    except Exception as e:
        logger.error(f"Error al obtener paquetes turísticos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{paquete_id}", response_model=PaqueteTuristicoResponse)
async def get_paquete_turistico(
    paquete_id: str,
    current_user: Optional[UsuarioResponse] = Depends(auth_handler.get_current_user)
):
    """Obtiene un paquete turístico específico por ID"""
    try:
        user_id = str(current_user.id) if current_user else None
        paquete = await paquete_turistico_repository.get_paquete_turistico_by_id(paquete_id, user_id)
        
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete turístico no encontrado"
            )
        
        return paquete
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paquete turístico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{paquete_id}", response_model=PaqueteTuristicoResponse)
async def update_paquete_turistico(
    paquete_id: str,
    paquete_update: PaqueteTuristicoUpdate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Actualiza un paquete turístico"""
    try:
        # Verificar que el paquete pertenezca al usuario actual
        paquete = await paquete_turistico_repository.get_paquete_turistico_by_id(paquete_id)
        
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete turístico no encontrado"
            )
        
        if str(paquete.operador_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar este paquete turístico"
            )
        
        updated_paquete = await paquete_turistico_repository.update_paquete_turistico(paquete_id, paquete_update)
        return updated_paquete
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar paquete turístico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{paquete_id}")
async def delete_paquete_turistico(
    paquete_id: str,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Elimina un paquete turístico (marca como inactivo)"""
    try:
        # Verificar que el paquete pertenezca al usuario actual
        paquete = await paquete_turistico_repository.get_paquete_turistico_by_id(paquete_id)
        
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete turístico no encontrado"
            )
        
        if str(paquete.operador_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este paquete turístico"
            )
        
        success = await paquete_turistico_repository.delete_paquete_turistico(paquete_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el paquete turístico"
            )
        
        return {"message": "Paquete turístico eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paquete turístico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/operador/mis-paquetes", response_model=List[PaqueteTuristicoResponse])
async def get_my_paquetes_turisticos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Obtiene los paquetes turísticos del operador actual"""
    try:
        paquetes = await paquete_turistico_repository.get_paquetes_by_operador(str(current_user.id), skip, limit)
        return paquetes
    except Exception as e:
        logger.error(f"Error al obtener paquetes del operador: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/search", response_model=List[PaqueteTuristicoResponse])
async def search_paquetes_turisticos(
    filtros: PaqueteTuristicoFiltros,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Optional[UsuarioResponse] = Depends(auth_handler.get_current_user)
):
    """Busca paquetes turísticos con filtros avanzados"""
    try:
        user_id = str(current_user.id) if current_user else None
        paquetes = await paquete_turistico_repository.search_paquetes_turisticos(filtros, skip, limit, user_id)
        return paquetes
    except Exception as e:
        logger.error(f"Error al buscar paquetes turísticos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 