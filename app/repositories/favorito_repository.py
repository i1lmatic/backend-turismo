from typing import Optional
from app.database import db
from app.models.favorito import FavoritoResponse, FavoritoCreate
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class FavoritoRepository(object):
    def __init__(self):
        self.connection = db.get_client()
    
    async def add_favorito(self, favorito_data: FavoritoCreate) -> FavoritoResponse:
        """Agrega un paquete turístico a favoritos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO favoritos (usuario_id, paquete_id, fecha_agregado)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (favorito_data.usuario_id, favorito_data.paquete_id))
            
            self.connection.commit()
            
            # Obtener el favorito creado
            favorito_id = cursor.lastrowid
            cursor.execute(
                "SELECT * FROM favoritos WHERE id = ?",
                (favorito_id,)
            )
            favorito_data = dict(cursor.fetchone())
            
            return await self._enrich_favorito_response(favorito_data)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al agregar favorito: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def get_favoritos_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[FavoritoResponse]:
        """Obtiene los favoritos de un usuario"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM favoritos WHERE usuario_id = ?
                ORDER BY fecha_agregado DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, skip))
            
            favoritos = []
            for favorito in cursor.fetchall():
                enriched_favorito = await self._enrich_favorito_response(dict(favorito))
                favoritos.append(enriched_favorito)
            
            return favoritos
        except Exception as e:
            logger.error(f"Error al obtener favoritos del usuario: {e}")
            return []
    
    async def remove_favorito(self, paquete_id: int, user_id: int) -> bool:
        """Elimina un paquete turístico de favoritos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM favoritos WHERE paquete_id = ? AND usuario_id = ?",
                (paquete_id, user_id)
            )
            self.connection.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar favorito: {e}")
            return False
    
    async def is_favorite(self, paquete_id: int, user_id: int) -> bool:
        """Verifica si un paquete turístico está en favoritos del usuario"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id FROM favoritos WHERE paquete_id = ? AND usuario_id = ?",
                (paquete_id, user_id)
            )
            
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error al verificar favorito: {e}")
            return False
    
    def _enrich_favorito_response(self, favorito_data: dict) -> FavoritoResponse:
        """Enriquece la respuesta de favorito con datos adicionales"""
        try:
            # Obtener datos del paquete turístico
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT titulo, precio_por_persona, destino, tipo_paquete, duracion_dias, nivel_dificultad, operador_id FROM paquetes_turisticos WHERE id = ?",
                (favorito_data['paquete_id'],)
            )
            paquete = cursor.fetchone()
            
            if paquete:
                paquete_dict = dict(paquete)
                favorito_data['paquete_titulo'] = paquete_dict['titulo']
                favorito_data['paquete_precio_por_persona'] = paquete_dict['precio_por_persona']
                favorito_data['paquete_destino'] = paquete_dict['destino']
                favorito_data['paquete_tipo'] = paquete_dict['tipo_paquete']
                favorito_data['paquete_duracion_dias'] = paquete_dict['duracion_dias']
                favorito_data['paquete_nivel_dificultad'] = paquete_dict['nivel_dificultad']
                
                # Obtener imagen principal del paquete turístico
                cursor.execute(
                    "SELECT url_imagen FROM imagenes_paquetes WHERE paquete_id = ? AND es_principal = 1 LIMIT 1",
                    (favorito_data['paquete_id'],)
                )
                imagen = cursor.fetchone()
                if imagen:
                    favorito_data['paquete_imagen_principal'] = imagen['url_imagen']
                
                # Calcular calificación promedio del paquete turístico
                cursor.execute("""
                    SELECT AVG(calificacion) as promedio
                    FROM reviews WHERE paquete_id = ?
                """, (favorito_data['paquete_id'],))
                
                review_stats = cursor.fetchone()
                if review_stats:
                    stats_dict = dict(review_stats)
                    favorito_data['paquete_calificacion_promedio'] = float(stats_dict['promedio']) if stats_dict['promedio'] else None
                
                # Obtener datos del operador
                cursor.execute(
                    "SELECT nombre, apellido FROM usuarios WHERE id = ?",
                    (paquete_dict['operador_id'],)
                )
                operador = cursor.fetchone()
                
                if operador:
                    operador_dict = dict(operador)
                    favorito_data['operador_nombre'] = operador_dict['nombre']
                    favorito_data['operador_apellido'] = operador_dict['apellido']
            
            return FavoritoResponse(**favorito_data)
        except Exception as e:
            logger.error(f"Error al enriquecer respuesta de favorito: {e}")
            return FavoritoResponse(**favorito_data)

# Instancia global del repository de favoritos
favorito_repository = FavoritoRepository() 