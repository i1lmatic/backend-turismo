import json
import os
import aiofiles
from typing import Any
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import FileResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/postman", tags=["Postman"])

class PostmanGenerator(object):
    def __init__(self):
        self.collection_name = "Airbnb Clone API"
        self.collection_description = "API completa para sistema tipo Airbnb"
        self.version = "1.0.0"
    
    def generate_collection(self, request: Request) -> dict[str, Any]:
        """Genera una colección de Postman completa"""
        try:
            # Obtener la URL base dinámicamente
            base_url = str(request.base_url).rstrip('/')
            
            collection = {
                "info": {
                    "name": self.collection_name,
                    "description": self.collection_description,
                    "version": self.version,
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "variable": [
                    {
                        "key": "base_url",
                        "value": base_url,
                        "type": "string"
                    },
                    {
                        "key": "access_token",
                        "value": "",
                        "type": "string"
                    },
                    {
                        "key": "refresh_token",
                        "value": "",
                        "type": "string"
                    }
                ],
                "item": [
                    self._generate_auth_folder(),
                    self._generate_usuarios_folder(),
                    self._generate_paquetes_turisticos_folder(),
                    self._generate_reservas_folder(),
                    self._generate_reviews_folder(),
                    self._generate_favoritos_folder()
                ]
            }
            
            return collection
        except Exception as e:
            logger.error(f"Error generando colección Postman: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generando colección Postman"
            )
    
    @staticmethod
    def _generate_auth_folder() -> dict[str, Any]:
        """Genera la carpeta de autenticación"""
        return {
            "name": "🔐 Autenticación",
            "description": "Endpoints para registro, login y gestión de tokens",
            "item": [
                PostmanGenerator._create_register_request(),
                PostmanGenerator._create_login_request(),
                PostmanGenerator._create_me_request(),
                PostmanGenerator._create_refresh_request()
            ]
        }
    
    @staticmethod
    def _create_register_request() -> dict[str, Any]:
        """Crea la request de registro"""
        return {
            "name": "Registrar Usuario",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "email": "usuario@ejemplo.com",
                        "password": "contraseña123",
                        "nombre": "Juan",
                        "apellido": "Pérez",
                        "telefono": "+1234567890",
                        "es_operador": False
                    }, indent=2)
                },
                "url": {
                    "raw": "{{base_url}}/auth/register",
                    "host": ["{{base_url}}"],
                    "path": ["auth", "register"]
                }
            }
        }
    
    @staticmethod
    def _create_login_request() -> dict[str, Any]:
        """Crea la request de login con script automático"""
        return {
            "name": "Iniciar Sesión",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "email": "usuario@ejemplo.com",
                        "password": "contraseña123"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{base_url}}/auth/login",
                    "host": ["{{base_url}}"],
                    "path": ["auth", "login"]
                },
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "if (pm.response.code === 200) {",
                            "    const response = pm.response.json();",
                            "    pm.collectionVariables.set('access_token', response.access_token);",
                            "    pm.collectionVariables.set('refresh_token', response.refresh_token);",
                            "    console.log('Tokens guardados automáticamente');",
                            "}"
                        ]
                    }
                }]
            }
        }
    
    @staticmethod
    def _create_me_request() -> dict[str, Any]:
        """Crea la request para obtener usuario actual"""
        return {
            "name": "Obtener Usuario Actual",
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                "url": {
                    "raw": "{{base_url}}/auth/me",
                    "host": ["{{base_url}}"],
                    "path": ["auth", "me"]
                }
            }
        }
    
    @staticmethod
    def _create_refresh_request() -> dict[str, Any]:
        """Crea la request para refrescar token"""
        return {
            "name": "Refrescar Token",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({"refresh_token": "{{refresh_token}}"}, indent=2)
                },
                "url": {
                    "raw": "{{base_url}}/auth/refresh",
                    "host": ["{{base_url}}"],
                    "path": ["auth", "refresh"]
                }
            }
        }
    
    @staticmethod
    def _generate_usuarios_folder() -> dict[str, Any]:
        """Genera la carpeta de usuarios"""
        return {
            "name": "👥 Usuarios",
            "description": "Gestión de perfiles de usuario",
            "item": [
                {
                    "name": "Obtener Perfil Actual",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/usuarios/me",
                            "host": ["{{base_url}}"],
                            "path": ["usuarios", "me"]
                        }
                    }
                },
                {
                    "name": "Actualizar Perfil",
                    "request": {
                        "method": "PUT",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "nombre": "Juan Actualizado",
                                "apellido": "Pérez Actualizado",
                                "telefono": "+1234567890",
                                "pais": "México",
                                "ciudad": "Ciudad de México"
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{base_url}}/usuarios/me",
                            "host": ["{{base_url}}"],
                            "path": ["usuarios", "me"]
                        }
                    }
                },
                {
                    "name": "Obtener Usuario por ID",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/usuarios/1",
                            "host": ["{{base_url}}"],
                            "path": ["usuarios", "1"]
                        }
                    }
                }
            ]
        }
    
    @staticmethod
    def _generate_paquetes_turisticos_folder() -> dict[str, Any]:
        """Genera la carpeta de paquetes turísticos"""
        return {
            "name": "🧳 Paquetes Turísticos",
            "description": "Gestión de paquetes turísticos y búsquedas",
            "item": [
                PostmanGenerator._create_paquete_turistico_request(),
                PostmanGenerator._create_get_paquetes_turisticos_request(),
                PostmanGenerator._create_get_paquete_turistico_by_id_request(),
                PostmanGenerator._create_update_paquete_turistico_request(),
                PostmanGenerator._create_search_paquetes_turisticos_request(),
                PostmanGenerator._create_my_paquetes_turisticos_request()
            ]
        }
    
    @staticmethod
    def _create_propiedad_request() -> dict[str, Any]:
        """Crea la request para crear propiedad"""
        return {
            "name": "Crear Propiedad",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{access_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "titulo": "Hermosa casa en la playa",
                        "descripcion": "Casa moderna con vista al mar",
                        "tipo_propiedad": "casa",
                        "capacidad_maxima": 6,
                        "habitaciones": 3,
                        "baños": 2,
                        "precio_por_noche": 150.00,
                        "precio_limpieza": 50.00,
                        "precio_servicio": 25.00,
                        "pais": "México",
                        "ciudad": "Cancún",
                        "direccion": "Av. Kukulcan 123",
                        "codigo_postal": "77500",
                        "hora_check_in": "15:00",
                        "hora_check_out": "11:00",
                        "permite_mascotas": True,
                        "permite_fumar": False,
                        "permite_fiestas": False
                    }, indent=2)
                },
                "url": {
                    "raw": "{{base_url}}/propiedades/",
                    "host": ["{{base_url}}"],
                    "path": ["propiedades", ""]
                }
            }
        }
    
    @staticmethod
    def _create_get_propiedades_request() -> dict[str, Any]:
        """Crea la request para obtener todas las propiedades"""
        return {
            "name": "Obtener Todas las Propiedades",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/propiedades/?skip=0&limit=10",
                    "host": ["{{base_url}}"],
                    "path": ["propiedades", ""],
                    "query": [
                        {"key": "skip", "value": "0"},
                        {"key": "limit", "value": "10"}
                    ]
                }
            }
        }
    
    @staticmethod
    def _create_get_propiedad_by_id_request() -> dict[str, Any]:
        """Crea la request para obtener propiedad por ID"""
        return {
            "name": "Obtener Propiedad por ID",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/propiedades/1",
                    "host": ["{{base_url}}"],
                    "path": ["propiedades", "1"]
                }
            }
        }
    
    @staticmethod
    def _create_update_propiedad_request() -> dict[str, Any]:
        """Crea la request para actualizar propiedad"""
        return {
            "name": "Actualizar Propiedad",
            "request": {
                "method": "PUT",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{access_token}}"},
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "titulo": "Casa actualizada",
                        "precio_por_noche": 200.00
                    }, indent=2)
                },
                "url": {
                    "raw": "{{base_url}}/propiedades/1",
                    "host": ["{{base_url}}"],
                    "path": ["propiedades", "1"]
                }
            }
        }
    
    @staticmethod
    def _create_search_propiedades_request() -> dict[str, Any]:
        """Crea la request para buscar propiedades"""
        return {
            "name": "Buscar Propiedades",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "pais": "México",
                        "ciudad": "Cancún",
                        "precio_min": 100,
                        "precio_max": 300,
                        "capacidad_minima": 4,
                        "permite_mascotas": True
                    }, indent=2)
                },
                "url": {
                    "raw": "{{base_url}}/propiedades/search",
                    "host": ["{{base_url}}"],
                    "path": ["propiedades", "search"]
                }
            }
        }
    
    @staticmethod
    def _create_my_propiedades_request() -> dict[str, Any]:
        """Crea la request para obtener mis propiedades"""
        return {
            "name": "Mis Propiedades (Anfitrión)",
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                "url": {
                    "raw": "{{base_url}}/propiedades/anfitrion/mis-propiedades",
                    "host": ["{{base_url}}"],
                    "path": ["propiedades", "anfitrion", "mis-propiedades"]
                }
            }
        }
    
    @staticmethod
    def _generate_reservas_folder() -> dict[str, Any]:
        """Genera la carpeta de reservas"""
        return {
            "name": "📅 Reservas",
            "description": "Gestión de reservas y calendario",
            "item": [
                {
                    "name": "Crear Reserva",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "propiedad_id": 1,
                                "fecha_check_in": "2024-02-01",
                                "fecha_check_out": "2024-02-05",
                                "numero_huespedes": 4,
                                "precio_total": 600.00,
                                "precio_por_noche": 150.00,
                                "precio_limpieza": 50.00,
                                "precio_servicio": 25.00,
                                "motivo_viaje": "Vacaciones",
                                "notas_especiales": "Llegada tarde"
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{base_url}}/reservas/",
                            "host": ["{{base_url}}"],
                            "path": ["reservas", ""]
                        }
                    }
                },
                {
                    "name": "Obtener Mis Reservas",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/reservas/?skip=0&limit=10",
                            "host": ["{{base_url}}"],
                            "path": ["reservas", ""],
                            "query": [
                                {
                                    "key": "skip",
                                    "value": "0"
                                },
                                {
                                    "key": "limit",
                                    "value": "10"
                                }
                            ]
                        }
                    }
                },
                {
                    "name": "Obtener Reserva por ID",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/reservas/1",
                            "host": ["{{base_url}}"],
                            "path": ["reservas", "1"]
                        }
                    }
                },
                {
                    "name": "Cancelar Reserva",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "motivo": "Cambio de planes"
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{base_url}}/reservas/cancel/1",
                            "host": ["{{base_url}}"],
                            "path": ["reservas", "cancel", "1"]
                        }
                    }
                }
            ]
        }
    
    @staticmethod
    def _generate_reviews_folder() -> dict[str, Any]:
        """Genera la carpeta de reviews"""
        return {
            "name": "⭐ Reviews",
            "description": "Sistema de calificaciones y comentarios",
            "item": [
                {
                    "name": "Crear Review",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "reserva_id": 1,
                                "propiedad_id": 1,
                                "calificacion": 5,
                                "comentario": "Excelente experiencia, muy recomendado",
                                "limpieza": 5,
                                "comunicacion": 5,
                                "llegada": 5,
                                "precision": 5,
                                "ubicacion": 5,
                                "valor": 5
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{base_url}}/reviews/",
                            "host": ["{{base_url}}"],
                            "path": ["reviews", ""]
                        }
                    }
                },
                {
                    "name": "Obtener Reviews de Propiedad",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/reviews/propiedad/1?skip=0&limit=10",
                            "host": ["{{base_url}}"],
                            "path": ["reviews", "propiedad", "1"],
                            "query": [
                                {
                                    "key": "skip",
                                    "value": "0"
                                },
                                {
                                    "key": "limit",
                                    "value": "10"
                                }
                            ]
                        }
                    }
                },
                {
                    "name": "Obtener Review por ID",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/reviews/1",
                            "host": ["{{base_url}}"],
                            "path": ["reviews", "1"]
                        }
                    }
                }
            ]
        }
    
    @staticmethod
    @staticmethod
    def _generate_favoritos_folder() -> dict[str, Any]:
        """Genera la carpeta de favoritos"""
        return {
            "name": "❤️ Favoritos",
            "description": "Gestión de propiedades favoritas",
            "item": [
                {
                    "name": "Agregar a Favoritos",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "propiedad_id": 1
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{base_url}}/favoritos/",
                            "host": ["{{base_url}}"],
                            "path": ["favoritos", ""]
                        }
                    }
                },
                {
                    "name": "Obtener Mis Favoritos",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/favoritos/?skip=0&limit=10",
                            "host": ["{{base_url}}"],
                            "path": ["favoritos", ""],
                            "query": [
                                {
                                    "key": "skip",
                                    "value": "0"
                                },
                                {
                                    "key": "limit",
                                    "value": "10"
                                }
                            ]
                        }
                    }
                },
                {
                    "name": "Verificar si es Favorito",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/favoritos/check/1",
                            "host": ["{{base_url}}"],
                            "path": ["favoritos", "check", "1"]
                        }
                    }
                },
                {
                    "name": "Eliminar de Favoritos",
                    "request": {
                        "method": "DELETE",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/favoritos/1",
                            "host": ["{{base_url}}"],
                            "path": ["favoritos", "1"]
                        }
                    }
                }
            ]
        }

# Instancia global del generador
postman_generator = PostmanGenerator()



@router.get("/download")
async def download_postman_collection(request: Request):
    """Descarga la colección de Postman como archivo JSON"""
    try:
        collection = postman_generator.generate_collection(request)
        
        # Crear directorio si no existe
        os.makedirs("downloads", exist_ok=True)
        
        # Guardar archivo con timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"airbnb_clone_api_postman_collection_{timestamp}.json"
        filepath = os.path.join("downloads", filename)
        
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(json.dumps(collection, indent=2, ensure_ascii=False))
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logger.error(f"Error descargando colección Postman: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error descargando colección Postman"
        )



 