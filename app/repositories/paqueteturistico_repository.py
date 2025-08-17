from typing import Optional, List
from app.database import db
from app.models.paqueteturistico import PaqueteTuristicoResponse, PaqueteTuristicoCreate, PaqueteTuristicoUpdate, PaqueteTuristicoFiltros
from fastapi import HTTPException, status
import logging
import json
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

router = APIRouter()

logger = logging.getLogger(__name__)

class PaqueteTuristicoRepository(object):
    def __init__(self):
        self.connection = db.get_client()
    
    async def create_paquete_turistico(self, paquete_data: PaqueteTuristicoCreate) -> PaqueteTuristicoResponse:
        """Crea un nuevo paquete turístico"""
        try:
            # Validar campos obligatorios y loguear datos recibidos
            logger.info(f"Datos recibidos para crear paquete: {paquete_data}")
            if not paquete_data.titulo or not paquete_data.tipo_paquete or not paquete_data.duracion_dias or not paquete_data.capacidad_maxima or not paquete_data.nivel_dificultad or not paquete_data.precio_por_persona or not paquete_data.pais_destino or not paquete_data.ciudad_destino or not paquete_data.punto_encuentro:
                logger.error("Faltan campos obligatorios para crear el paquete turístico")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan campos obligatorios para crear el paquete turístico")
            logger.info(f"Imágenes recibidas: {paquete_data.imagenes}")
            cursor = self.connection.cursor()
            cursor.execute("""
    INSERT INTO paquetes_turisticos (
        operador_id, titulo, tipo_paquete, duracion_dias, capacidad_maxima, nivel_dificultad,
        precio_por_persona, pais_destino, ciudad_destino, punto_encuentro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    paquete_data.operador_id,
    paquete_data.titulo,
    paquete_data.tipo_paquete,
    paquete_data.duracion_dias,
    paquete_data.capacidad_maxima,
    paquete_data.nivel_dificultad,
    float(paquete_data.precio_por_persona),
    paquete_data.pais_destino,
    paquete_data.ciudad_destino,
    paquete_data.punto_encuentro
))
            self.connection.commit()

            # Obtener el paquete creado
            paquete_id = cursor.lastrowid
            cursor.execute(
                "SELECT * FROM paquetes_turisticos WHERE id = ?",
                (paquete_id,)
            )
            paquete_row = dict(cursor.fetchone())

            # Guardar imágenes en la tabla imagenes_paquetes
            if paquete_data.imagenes:
                for idx, img_base64 in enumerate(paquete_data.imagenes):
                    cursor.execute(
                        """
                        INSERT INTO imagenes_paquetes (paquete_id, url_imagen, es_principal, orden)
                        VALUES (?, ?, ?, ?)
                        """,
                        (paquete_id, img_base64, 1 if idx == 0 else 0, idx)
                    )
                self.connection.commit()

            return await self._enrich_paquete_response(paquete_row)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al crear paquete turístico: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def get_paquete_by_id(self, paquete_id: int, user_id: Optional[int] = None) -> Optional[PaqueteTuristicoResponse]:
        """Obtiene un paquete turístico por ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM paquetes_turisticos WHERE id = ?",
                (paquete_id,)
            )
            paquete = cursor.fetchone()
            
            if not paquete:
                return None
            
            return await self._enrich_paquete_response(
                dict(paquete), user_id
            )
        except Exception as e:
            logger.error(f"Error al obtener paquete por ID: {e}")
            return None
    
    async def get_all_paquetes(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[PaqueteTuristicoResponse]:
        """Obtiene todos los paquetes turísticos activos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM paquetes_turisticos WHERE esta_activo = 1
                ORDER BY fecha_creacion DESC
                LIMIT ? OFFSET ?
            """, (limit, skip))
            
            paquetes = []
            for paquete in cursor.fetchall():
                enriched_paquete = await self._enrich_paquete_response(
                    dict(paquete), user_id
                )
                paquetes.append(enriched_paquete)
            
            return paquetes
        except Exception as e:
            logger.error(f"Error al obtener paquetes: {e}")
            return []
    
    async def get_paquetes_by_operador(self, operador_id: int, skip: int = 0, limit: int = 100) -> List[PaqueteTuristicoResponse]:
        """Obtiene los paquetes de un operador turístico"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM paquetes_turisticos WHERE operador_id = ? AND esta_activo = 1
                ORDER BY fecha_creacion DESC
                LIMIT ? OFFSET ?
            """, (operador_id, limit, skip))
            paquetes = []
            for paquete in cursor.fetchall():
                enriched_paquete = await self._enrich_paquete_response(
                    dict(paquete)
                )
                paquetes.append(enriched_paquete)
            return paquetes
        except Exception as e:
            logger.error(f"Error al obtener paquetes del operador: {e}")
            return []
    
    async def get_paquete_turistico_by_id(self, paquete_id: int, user_id: Optional[int] = None) -> Optional[PaqueteTuristicoResponse]:
        """Alias para obtener paquete turístico por ID"""
        return await self.get_paquete_by_id(paquete_id, user_id)

    async def update_paquete(self, paquete_id: int, paquete_update: PaqueteTuristicoUpdate) -> Optional[PaqueteTuristicoResponse]:
        """Actualiza un paquete turístico"""
        try:
            # Filtrar campos None
            update_data = {k: v for k, v in paquete_update.dict().items() if v is not None}
            
            if not update_data:
                return await self.get_paquete_by_id(paquete_id)
            
            # Convertir Decimal a float para campos de precio
            if 'precio_por_persona' in update_data:
                update_data['precio_por_persona'] = float(update_data['precio_por_persona'])
            if 'precio_grupal' in update_data:
                update_data['precio_grupal'] = float(update_data['precio_grupal'])
            
            # Construir query de actualización
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [paquete_id]
            
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE paquetes_turisticos SET {set_clause}, "
                f"fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?",
                values
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Paquete turístico no encontrado"
                )
            
            self.connection.commit()
            return await self.get_paquete_by_id(paquete_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al actualizar paquete turístico: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def delete_paquete(self, paquete_id: int) -> bool:
        """Elimina un paquete turístico (marca como inactivo)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE paquetes_turisticos SET esta_activo = 0 WHERE id = ?",
                (paquete_id,)
            )
            self.connection.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar paquete turístico: {e}")
            return False
    
    async def search_paquetes(self, filtros: PaqueteTuristicoFiltros, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[PaqueteTuristicoResponse]:
        """Busca paquetes turísticos según filtros"""
        try:
            # Construir query dinámicamente
            query = "SELECT * FROM paquetes_turisticos WHERE esta_activo = 1"
            params = []
            
            if filtros.pais_origen:
                query += " AND pais_origen LIKE ?"
                params.append(f"%{filtros.pais_origen}%")
            
            if filtros.ciudad_origen:
                query += " AND ciudad_origen LIKE ?"
                params.append(f"%{filtros.ciudad_origen}%")
            
            if filtros.destinos:
                query += " AND destinos LIKE ?"
                params.append(f"%{filtros.destinos}%")
            
            if filtros.tipo_paquete:
                query += " AND tipo_paquete = ?"
                params.append(filtros.tipo_paquete)
            
            if filtros.duracion_min:
                query += " AND duracion_dias >= ?"
                params.append(filtros.duracion_min)
            
            if filtros.duracion_max:
                query += " AND duracion_dias <= ?"
                params.append(filtros.duracion_max)
            
            if filtros.capacidad_minima:
                query += " AND capacidad_maxima >= ?"
                params.append(filtros.capacidad_minima)
            
            if filtros.precio_min:
                query += " AND precio_por_persona >= ?"
                params.append(float(filtros.precio_min))
            
            if filtros.precio_max:
                query += " AND precio_por_persona <= ?"
                params.append(float(filtros.precio_max))
            
            if filtros.incluye_transporte is not None:
                query += " AND incluye_transporte = ?"
                params.append(filtros.incluye_transporte)
            
            if filtros.incluye_alojamiento is not None:
                query += " AND incluye_alojamiento = ?"
                params.append(filtros.incluye_alojamiento)
            
            if filtros.incluye_comidas is not None:
                query += " AND incluye_comidas = ?"
                params.append(filtros.incluye_comidas)
            
            if filtros.incluye_guia is not None:
                query += " AND incluye_guia = ?"
                params.append(filtros.incluye_guia)
            
            if filtros.dificultad:
                query += " AND dificultad = ?"
                params.append(filtros.dificultad)
            
            if filtros.edad_minima:
                query += " AND (edad_minima IS NULL OR edad_minima <= ?)"
                params.append(filtros.edad_minima)
            
            if filtros.edad_maxima:
                query += " AND (edad_maxima IS NULL OR edad_maxima >= ?)"
                params.append(filtros.edad_maxima)
            
            query += " ORDER BY fecha_creacion DESC LIMIT ? OFFSET ?"
            params.extend([limit, skip])
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            paquetes = []
            for paquete in cursor.fetchall():
                enriched_paquete = await self._enrich_paquete_response(
                    dict(paquete), user_id
                )
                paquetes.append(enriched_paquete)
            
            return paquetes
        except Exception as e:
            logger.error(f"Error al buscar paquetes turísticos: {e}")
            return []
    
    async def search_paquetes_turisticos(self, filtros: PaqueteTuristicoFiltros, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[PaqueteTuristicoResponse]:
        """Busca paquetes turísticos según filtros avanzados"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM paquetes_turisticos WHERE 1=1"
            params = []

            if filtros.tipo_paquete:
                query += " AND tipo_paquete = ?"
                params.append(filtros.tipo_paquete)
            if filtros.pais_destino:
                query += " AND pais_destino = ?"
                params.append(filtros.pais_destino)
            if filtros.ciudad_destino:
                query += " AND ciudad_destino = ?"
                params.append(filtros.ciudad_destino)
            if filtros.nivel_dificultad:
                query += " AND nivel_dificultad = ?"
                params.append(filtros.nivel_dificultad)
            if filtros.precio_min is not None:
                query += " AND precio_por_persona >= ?"
                params.append(float(filtros.precio_min))
            if filtros.precio_max is not None:
                query += " AND precio_por_persona <= ?"
                params.append(float(filtros.precio_max))
            if filtros.duracion_min is not None:
                query += " AND duracion_dias >= ?"
                params.append(filtros.duracion_min)
            if filtros.duracion_max is not None:
                query += " AND duracion_dias <= ?"
                params.append(filtros.duracion_max)

            query += " LIMIT ? OFFSET ?"
            params.extend([limit, skip])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            paquetes = []
            for row in rows:
                paquete_row = dict(row)
                paquete = await self._enrich_paquete_response(paquete_row)
                paquetes.append(paquete)
            return paquetes
        except Exception as e:
            logger.error(f"Error en búsqueda de paquetes turísticos: {e}")
            raise HTTPException(status_code=500, detail="Error interno en búsqueda de paquetes turísticos")
    
    async def _enrich_paquete_response(self, paquete_data: dict, user_id: Optional[int] = None) -> PaqueteTuristicoResponse:
        """Enriquece la respuesta de paquete turístico con datos adicionales"""
        try:
            # Obtener datos del operador turístico
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT nombre, apellido, avatar_url FROM usuarios WHERE id = ?",
                (paquete_data['operador_id'],)
            )
            operador = cursor.fetchone()
            
            if operador:
                operador_dict = dict(operador)
                paquete_data['operador_nombre'] = operador_dict['nombre']
                paquete_data['operador_apellido'] = operador_dict['apellido']
                paquete_data['operador_avatar'] = operador_dict['avatar_url']
            
            # Obtener calificación promedio y total de reviews
            # Nota: Necesitaremos actualizar las reviews para que trabajen con paquetes
            cursor.execute("""
                SELECT AVG(calificacion) as promedio, COUNT(*) as total
                FROM reviews WHERE paquete_id = ?
            """, (paquete_data['id'],))
            
            review_stats = cursor.fetchone()
            if review_stats:
                review_dict = dict(review_stats)
                paquete_data['calificacion_promedio'] = (
                    float(review_dict['promedio']) if review_dict['promedio'] else None
                )
                paquete_data['total_reviews'] = review_dict['total']
            
            # Obtener imágenes del paquete
            cursor.execute(
                "SELECT url_imagen FROM imagenes_paquetes WHERE paquete_id = ? "
                "ORDER BY orden, es_principal DESC",
                (paquete_data['id'],)
            )
            
            imagenes_result = cursor.fetchall()
            imagenes = [dict(row)['url_imagen'] for row in imagenes_result]
            paquete_data['imagenes'] = imagenes
            
            # Verificar si es favorito del usuario
            if user_id:
                cursor.execute(
                    "SELECT id FROM favoritos WHERE usuario_id = ? AND paquete_id = ?",
                    (user_id, paquete_data['id'])
                )
                favorito = cursor.fetchone()
                paquete_data['es_favorito'] = favorito is not None
            

            
            return PaqueteTuristicoResponse(**paquete_data)
        except Exception as e:
            logger.error(f"Error al enriquecer respuesta de paquete turístico: {e}")
            return PaqueteTuristicoResponse(**paquete_data)
    

        # Alias para compatibilidad con el API
        get_all_paquetes_turisticos = get_all_paquetes

# Instancia global del repository de paquetes turísticos
paquete_turistico_repository = PaqueteTuristicoRepository()

# Alias para compatibilidad con código existente
propiedad_repository = paquete_turistico_repository
PropiedadRepository = PaqueteTuristicoRepository