from typing import List, Optional
from app.database import db
from app.models.usuario import UsuarioResponse, UsuarioUpdate
from app.auth.jwt_handler import jwt_handler
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class UsuarioRepository(object):
    def __init__(self):
        self.connection = db.get_client()
    
    async def get_user_by_id(self, user_id: str) -> Optional[UsuarioResponse]:
        """Obtiene un usuario por ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM usuarios WHERE id = ?",
                (user_id,)
            )
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
            
            return UsuarioResponse(**dict(user_data))
        except Exception as e:
            logger.error(f"Error al obtener usuario por ID: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UsuarioResponse]:
        """Obtiene un usuario por email"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = ?",
                (email,)
            )
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
            
            return UsuarioResponse(**dict(user_data))
        except Exception as e:
            logger.error(f"Error al obtener usuario por email: {e}")
            return None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UsuarioResponse]:
        """Obtiene todos los usuarios con paginación"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM usuarios LIMIT ? OFFSET ?",
                (limit, skip)
            )
            users_data = cursor.fetchall()
            
            return [UsuarioResponse(**dict(user)) for user in users_data]
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}")
            return []
    
    async def update_user(self, user_id: str, user_update: UsuarioUpdate) -> Optional[UsuarioResponse]:
        """Actualiza un usuario"""
        try:
            # Filtrar campos None
            update_data = {k: v for k, v in user_update.dict().items() if v is not None}
            
            if not update_data:
                return await self.get_user_by_id(user_id)
            
            # Construir query de actualización
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [user_id]
            
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE usuarios SET {set_clause} WHERE id = ?",
                values
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            self.connection.commit()
            return await self.get_user_by_id(user_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al actualizar usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM usuarios WHERE id = ?",
                (user_id,)
            )
            self.connection.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar usuario: {e}")
            return False
    
    async def verify_user(self, user_id: str) -> Optional[UsuarioResponse]:
        """Verifica un usuario (marca como verificado)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE usuarios SET es_verificado = 1 WHERE id = ?",
                (user_id,)
            )
            self.connection.commit()
            
            if cursor.rowcount == 0:
                return None
            
            return await self.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error al verificar usuario: {e}")
            return None
    
    async def update_user_avatar(self, user_id: str, avatar_url: str) -> Optional[UsuarioResponse]:
        """Actualiza el avatar de un usuario"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE usuarios SET avatar_url = ? WHERE id = ?",
                (avatar_url, user_id)
            )
            self.connection.commit()
            
            if cursor.rowcount == 0:
                return None
            
            return await self.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error al actualizar avatar: {e}")
            return None
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> list[UsuarioResponse]:
        """Busca usuarios por nombre o email"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM usuarios 
                WHERE nombre LIKE ? OR apellido LIKE ? OR email LIKE ?
                LIMIT ? OFFSET ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit, skip))
            
            users_data = cursor.fetchall()
            return [UsuarioResponse(**dict(user)) for user in users_data]
        except Exception as e:
            logger.error(f"Error al buscar usuarios: {e}")
            return []

# Instancia global del repository de usuarios
usuario_repository = UsuarioRepository() 