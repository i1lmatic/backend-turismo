from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models.usuario import UsuarioResponse, UsuarioUpdate
from app.repositories.instances import usuario_repository
from app.auth.auth_handler import auth_handler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Usuarios - Sistema de Turismo"])

@router.get("/me", response_model=UsuarioResponse)
async def get_me(current_user: UsuarioResponse = Depends(auth_handler.get_current_user)):
    """Obtiene la información completa del usuario actual (turista u operador turístico)"""
    return current_user

@router.put("/me", response_model=UsuarioResponse)
async def update_current_user(
    user_update: UsuarioUpdate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Actualiza la información del usuario actual (perfil de turista u operador turístico)"""
    try:
        updated_user = await usuario_repository.update_user(str(current_user.id), user_update)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{user_id}", response_model=UsuarioResponse)
async def get_user_by_id(user_id: str):
    """Obtiene un usuario por ID"""
    try:
        user = await usuario_repository.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[UsuarioResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtiene todos los usuarios (solo para administradores del sistema)"""
    try:
        users = await usuario_repository.get_all_users(skip, limit)
        return users
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/operadores", response_model=List[UsuarioResponse])
async def get_operadores_turisticos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Obtiene lista de operadores turísticos verificados"""
    try:
        # Aquí podrías agregar lógica específica para obtener solo operadores
        # Por ahora usamos el método general y filtramos
        users = await usuario_repository.get_all_users(skip, limit * 3)  # Obtenemos más para filtrar
        operadores = [user for user in users if user.es_operador and user.es_verificado]
        return operadores[:limit]
    except Exception as e:
        logger.error(f"Error al obtener operadores turísticos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me/stats")
async def get_my_stats(current_user: UsuarioResponse = Depends(auth_handler.get_current_user)):
    """Obtiene estadísticas del usuario actual (paquetes creados, reservas, etc.)"""
    try:
        if current_user.es_operador:
            # Estadísticas para operadores turísticos
            from app.repositories.instances import paquete_turistico_repository, reserva_repository
            
            # Contar paquetes creados por el operador
            # Por simplicidad, retornamos estructura básica
            stats = {
                "tipo_usuario": "operador_turistico",
                "es_verificado": current_user.es_verificado,
                "paquetes_activos": 0,  # Se podría implementar conteo real
                "reservas_recibidas": 0,  # Se podría implementar conteo real
                "perfil_completo": bool(current_user.descripcion_perfil and current_user.telefono)
            }
        else:
            # Estadísticas para turistas
            stats = {
                "tipo_usuario": "turista",
                "es_verificado": current_user.es_verificado,
                "reservas_realizadas": 0,  # Se podría implementar conteo real
                "favoritos_guardados": 0,  # Se podría implementar conteo real
                "reviews_escritas": 0,  # Se podría implementar conteo real
                "perfil_completo": bool(current_user.telefono and current_user.pais and current_user.ciudad)
            }
            
        return stats
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/me/convert-to-operator")
async def convert_to_operator(current_user: UsuarioResponse = Depends(auth_handler.get_current_user)):
    """Convierte un turista en operador turístico (requiere aprobación)"""
    try:
        if current_user.es_operador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya es un operador turístico"
            )
        
        # Validar que el perfil esté completo
        if not (current_user.telefono and current_user.pais and current_user.ciudad):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe completar su perfil (teléfono, país, ciudad) antes de convertirse en operador"
            )
        
        # Crear solicitud de conversión (por ahora lo hacemos directamente)
        from app.models.usuario import UsuarioUpdate
        update_data = UsuarioUpdate(es_operador=True)
        updated_user = await usuario_repository.update_user(str(current_user.id), update_data)
        
        return {
            "message": "Solicitud de conversión a operador turístico procesada",
            "status": "pendiente_verificacion",
            "note": "Su cuenta será revisada por nuestro equipo antes de activar las funciones de operador"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al convertir usuario a operador: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/me")
async def delete_current_user(current_user: UsuarioResponse = Depends(auth_handler.get_current_user)):
    """Elimina la cuenta del usuario actual (turista u operador turístico)"""
    try:
        # Verificar si es operador con paquetes activos
        if current_user.es_operador:
            # Aquí podrías agregar validación de paquetes activos
            # Por ahora solo notificamos
            pass
        
        success = await usuario_repository.delete_user(str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar usuario"
            )
        
        message = "Cuenta de operador turístico eliminada exitosamente" if current_user.es_operador else "Cuenta de turista eliminada exitosamente"
        return {"message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 