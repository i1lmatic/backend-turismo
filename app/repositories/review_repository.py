from typing import Optional
from app.database import db
from app.models.review import ReviewResponse, ReviewCreate
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class ReviewRepository(object):
    def __init__(self):
        self.connection = db.get_client()
    
    def create_review(self, review_data: ReviewCreate) -> ReviewResponse:
        """Crea una nueva review para un paquete turístico"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO reviews (
                    reserva_id, autor_id, paquete_id, calificacion, comentario,
                    organizacion, comunicacion, actividades, guia, seguridad, valor,
                    fecha_review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                review_data.reserva_id, review_data.autor_id, review_data.paquete_id,
                review_data.calificacion, review_data.comentario, review_data.organizacion,
                review_data.comunicacion, review_data.actividades, review_data.guia,
                review_data.seguridad, review_data.valor
            ))
            
            self.connection.commit()
            
            # Obtener la review creada
            review_id = cursor.lastrowid
            cursor.execute(
                "SELECT * FROM reviews WHERE id = ?",
                (review_id,)
            )
            review_data = dict(cursor.fetchone())
            
            return self._enrich_review_response(review_data)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al crear review: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    def get_review_by_id(self, review_id: int) -> Optional[ReviewResponse]:
        """Obtiene una review por ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM reviews WHERE id = ?",
                (review_id,)
            )
            review = cursor.fetchone()
            if not review:
                return None
            return self._enrich_review_response(dict(review))
        except Exception as e:
            logger.error(f"Error al obtener review por ID: {e}")
            return None
    
    def get_reviews_by_paquete(self, paquete_id: int, skip: int = 0, limit: int = 100) -> list[ReviewResponse]:
        """Obtiene las reviews de un paquete turístico"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM reviews WHERE paquete_id = ?
                ORDER BY fecha_review DESC
                LIMIT ? OFFSET ?
            """, (paquete_id, limit, skip))
            reviews = []
            for review in cursor.fetchall():
                enriched_review = self._enrich_review_response(dict(review))
                reviews.append(enriched_review)
            return reviews
        except Exception as e:
            logger.error(f"Error al obtener reviews de paquete turístico: {e}")
            return []
    
    def _enrich_review_response(self, review_data: dict[str, any]) -> ReviewResponse:
        """Enriquece la respuesta de review con datos adicionales"""
        from datetime import datetime
        try:
            # Obtener datos del autor
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT nombre, apellido, avatar_url FROM usuarios WHERE id = ?",
                (review_data['autor_id'],)
            )
            autor = cursor.fetchone()
            if autor:
                autor_dict = dict(autor)
                review_data['autor_nombre'] = autor_dict['nombre']
                review_data['autor_apellido'] = autor_dict['apellido']
                review_data['autor_avatar'] = autor_dict['avatar_url']
            # Obtener datos del paquete turístico
            cursor.execute(
                "SELECT titulo, tipo_paquete FROM paquetes_turisticos WHERE id = ?",
                (review_data['paquete_id'],)
            )
            paquete = cursor.fetchone()
            if paquete:
                paquete_dict = dict(paquete)
                review_data['paquete_titulo'] = paquete_dict['titulo']
                review_data['paquete_tipo'] = paquete_dict['tipo_paquete']
            # Obtener datos de la reserva
            cursor.execute(
                "SELECT fecha_inicio, fecha_fin FROM reservas WHERE id = ?",
                (review_data['reserva_id'],)
            )
            reserva = cursor.fetchone()
            if reserva:
                reserva_dict = dict(reserva)
                for campo in ['fecha_inicio', 'fecha_fin']:
                    valor = reserva_dict.get(campo)
                    dt_val = None
                    if valor is None:
                        dt_val = None
                    elif isinstance(valor, datetime):
                        dt_val = valor
                    elif isinstance(valor, str):
                        try:
                            # Si el string es solo fecha, agrega hora por defecto
                            if len(valor) == 10 and valor.count('-') == 2:
                                dt_val = datetime.strptime(valor, "%Y-%m-%d")
                            else:
                                dt_val = datetime.fromisoformat(valor)
                        except Exception:
                            dt_val = None
                    else:
                        dt_val = None
                    review_data[f'reserva_{campo}'] = dt_val
            # Calcular calificación promedio del paquete turístico
            cursor.execute("""
                SELECT AVG(calificacion) as promedio, COUNT(*) as total
                FROM reviews WHERE paquete_id = ?
            """, (review_data['paquete_id'],))
            review_stats = cursor.fetchone()
            if review_stats:
                stats_dict = dict(review_stats)
                review_data['calificacion_promedio_paquete'] = (
                    float(stats_dict['promedio']) if stats_dict['promedio'] else None
                )
                review_data['total_reviews_paquete'] = stats_dict['total']
            return ReviewResponse(**review_data)
        except Exception as e:
            logger.error(f"Error al enriquecer respuesta de review: {e}")
            return ReviewResponse(**review_data)

# Instancia global del repository de reviews
review_repository = ReviewRepository() 