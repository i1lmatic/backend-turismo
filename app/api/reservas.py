
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models.reserva import ReservaResponse, ReservaCreate, ReservaUpdate, ReservaFiltros
from app.models.usuario import UsuarioResponse
from app.repositories.instances import reserva_repository
from app.auth.auth_handler import auth_handler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.get("/operador", response_model=List[ReservaResponse])
async def get_reservas_by_operador(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    if not current_user.es_operador:
        raise HTTPException(status_code=403, detail="Solo operadores pueden ver sus reservas")
    reservas = await reserva_repository.get_reservas_by_operador(str(current_user.id), skip, limit)
    return reservas  # No lances error si reservas es []

@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def create_reserva(
    reserva_data: ReservaCreate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Crea una nueva reserva de paquete turístico"""
    try:
        # Asignar el turista actual
        reserva_data.turista_id = current_user.id
        
        reserva = await reserva_repository.create_reserva(reserva_data)
        return reserva
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear reserva: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{reserva_id}", response_model=ReservaResponse)
async def get_reserva(
    reserva_id: str,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Obtiene una reserva específica"""
    try:
        reserva = await reserva_repository.get_reserva_by_id(reserva_id, str(current_user.id))
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        return reserva
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener reserva: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{reserva_id}", response_model=ReservaResponse)
async def update_reserva(
    reserva_id: str,
    reserva_update: ReservaUpdate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Actualiza una reserva"""
    try:
        # Verificar que la reserva pertenezca al usuario actual
        reserva = await reserva_repository.get_reserva_by_id(reserva_id, str(current_user.id))
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        updated_reserva = await reserva_repository.update_reserva(reserva_id, reserva_update, str(current_user.id))
        return updated_reserva
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar reserva: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[ReservaResponse])
async def get_my_reservas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Obtiene las reservas de paquetes turísticos del usuario actual"""
    try:
        reservas = await reserva_repository.get_reservas_by_user(str(current_user.id), skip, limit)
        return reservas
    except Exception as e:
        logger.error(f"Error al obtener reservas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/cancel/{reserva_id}")
async def cancel_reserva(
    reserva_id: str,
    motivo: str = None,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Cancela una reserva de paquete turístico"""
    try:
        success = await reserva_repository.cancel_reserva(reserva_id, str(current_user.id), motivo)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo cancelar la reserva del paquete turístico"
            )
        
        return {"message": "Reserva de paquete turístico cancelada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar reserva: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )