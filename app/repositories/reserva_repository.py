from typing import List, Optional
from app.database import db
from app.models.reserva import ReservaResponse, ReservaCreate, ReservaUpdate
from fastapi import HTTPException, status
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReservaRepository(object):
    def __init__(self):
        self.connection = db.get_client()
    
    async def create_reserva(self, reserva_data: ReservaCreate) -> ReservaResponse:
        """Crea una nueva reserva"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
INSERT INTO reservas (
    paquete_id, turista_id, fecha_inicio, fecha_fin,
    numero_personas, numero_adultos, precio_total, precio_por_persona, 
    estado, metodo_pago, pagado, fecha_creacion
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    reserva_data.paquete_id,
                    reserva_data.turista_id,
                    reserva_data.fecha_inicio,
                    reserva_data.fecha_fin,
                    reserva_data.numero_personas,
                    reserva_data.numero_adultos,
                    float(reserva_data.precio_total) if reserva_data.precio_total is not None else None,
                    float(reserva_data.precio_por_persona) if reserva_data.precio_por_persona is not None else None,
                    reserva_data.estado or 'pendiente',
                    reserva_data.metodo_pago,
                    reserva_data.pagado or False
                )
            )
            
            self.connection.commit()
            
            # Obtener la reserva creada
            reserva_id = cursor.lastrowid
            cursor.execute(
                "SELECT * FROM reservas WHERE id = ?",
                (reserva_id,)
            )
            reserva_data = dict(cursor.fetchone())
            
            return self._enrich_reserva_response(reserva_data)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al crear reserva: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def get_reserva_by_id(self, reserva_id: str, user_id: str) -> Optional[ReservaResponse]:
        """Obtiene una reserva por ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM reservas WHERE id = ?",
                (reserva_id,)
            )
            reserva = cursor.fetchone()
            
            if not reserva:
                return None
            
            reserva_dict = dict(reserva)
            
            # Verificar que el usuario tenga acceso a esta reserva
            # (Solo lógica de operador si es necesario, huesped eliminado)
            
            return self._enrich_reserva_response(reserva_dict)
        except Exception as e:
            logger.error(f"Error al obtener reserva por ID: {e}")
            return None
    
    async def get_reservas_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> list[ReservaResponse]:
        """Obtiene las reservas de un usuario"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM reservas WHERE turista_id = ?
                ORDER BY fecha_creacion DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, skip))
            
            reservas = []
            for reserva in cursor.fetchall():
                enriched_reserva = self._enrich_reserva_response(dict(reserva))
                reservas.append(enriched_reserva)
            
            return reservas
        except Exception as e:
            logger.error(f"Error al obtener reservas del usuario: {e}")
            return []
    
    async def update_reserva(self, reserva_id: str, reserva_update: ReservaUpdate, user_id: str) -> Optional[ReservaResponse]:
        """Actualiza una reserva"""
        try:
            # Verificar que la reserva pertenezca al usuario
            reserva = await self.get_reserva_by_id(reserva_id, user_id)
            
            if not reserva:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reserva no encontrada"
                )
            
            # Filtrar campos None
            update_data = {k: v for k, v in reserva_update.dict().items() if v is not None}
            
            if not update_data:
                return reserva
            
            # Construir query de actualización
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [reserva_id]
            
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE reservas SET {set_clause} WHERE id = ?",
                values
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reserva no encontrada"
                )
            
            self.connection.commit()
            return await self.get_reserva_by_id(reserva_id, user_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al actualizar reserva: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def cancel_reserva(self, reserva_id: str, user_id: str, motivo: str = None) -> bool:
        """Cancela una reserva"""
        try:
            # Verificar que la reserva pertenezca al usuario
            reserva = await self.get_reserva_by_id(reserva_id, user_id)
            
            if not reserva:
                return False
            
            update_data = {
                'estado': 'cancelada',
                'fecha_cancelacion': 'CURRENT_TIMESTAMP'
            }
            
            if motivo:
                update_data['motivo_cancelacion'] = motivo
            
            # Construir query de actualización
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [reserva_id]
            
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE reservas SET {set_clause} WHERE id = ?",
                values
            )
            
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al cancelar reserva: {e}")
            return False
    
    def _enrich_reserva_response(self, reserva_data: dict) -> ReservaResponse:
        """Enriquece la respuesta de reserva con datos adicionales"""
        try:
            # Obtener datos de la propiedad
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT titulo FROM paquetes_turisticos WHERE id = ?",
                (reserva_data['paquete_id'],)
            )
            propiedad = cursor.fetchone()
            
            if propiedad:
                propiedad_dict = dict(propiedad)
                reserva_data['propiedad_titulo'] = propiedad_dict['titulo']
            
            # Obtener datos del anfitrión
            if propiedad:
                cursor.execute(
                    "SELECT nombre, apellido FROM usuarios WHERE id = ?",
                    (propiedad_dict['operador_id'],)
                )
                operador = cursor.fetchone()
                
                if operador:
                    operador_dict = dict(operador)
                    reserva_data['operador_nombre'] = operador_dict['nombre']
                    reserva_data['operador_apellido'] = operador_dict['apellido']
            
            # (Lógica de huésped eliminada)
            
            # Calcular días de estancia
            check_in = datetime.fromisoformat(reserva_data['fecha_inicio'].replace('Z', '+00:00'))
            check_out = datetime.fromisoformat(reserva_data['fecha_fin'].replace('Z', '+00:00'))
            dias = (check_out - check_in).days
            reserva_data['dias_estancia'] = dias
            
            return ReservaResponse(**reserva_data)
        except Exception as e:
            logger.error(f"Error al enriquecer respuesta de reserva: {e}")
            return ReservaResponse(**reserva_data)

# Instancia global del repository de reservas
reserva_repository = ReservaRepository() 