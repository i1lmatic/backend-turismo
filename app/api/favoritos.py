from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models.favorito import FavoritoResponse, FavoritoCreate
from app.models.usuario import UsuarioResponse
from app.repositories.instances import favorito_repository
from app.auth.auth_handler import auth_handler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])

@router.post("/", response_model=FavoritoResponse, status_code=status.HTTP_201_CREATED)
async def add_favorito(
    favorito_data: FavoritoCreate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Agrega un paquete turístico a favoritos"""
    try:
        # Asignar el usuario actual
        favorito_data.usuario_id = current_user.id
        
        favorito = await favorito_repository.add_favorito(favorito_data)
        return favorito
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al agregar paquete a favoritos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[FavoritoResponse])
async def get_my_favoritos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Obtiene los paquetes turísticos favoritos del usuario actual"""
    try:
        favoritos = await favorito_repository.get_favoritos_by_user(str(current_user.id), skip, limit)
        return favoritos
    except Exception as e:
        logger.error(f"Error al obtener paquetes favoritos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{paquete_id}")
async def remove_favorito(
    paquete_id: str,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Elimina un paquete turístico de favoritos"""
    try:
        success = await favorito_repository.remove_favorito(paquete_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorito no encontrado"
            )
        
        return {"message": "Paquete turístico eliminado de favoritos exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar favorito: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/check/{paquete_id}")
async def check_favorito(
    paquete_id: str,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Verifica si un paquete turístico está en favoritos del usuario"""
    try:
        is_favorite = await favorito_repository.is_favorite(paquete_id, str(current_user.id))
        return {"is_favorite": is_favorite}
    except Exception as e:
        logger.error(f"Error al verificar favorito: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 