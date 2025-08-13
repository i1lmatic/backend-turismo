from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models.review import ReviewResponse, ReviewCreate, ReviewUpdate
from app.models.usuario import UsuarioResponse
from app.repositories.instances import review_repository
from app.auth.auth_handler import auth_handler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: UsuarioResponse = Depends(auth_handler.get_current_user)
):
    """Crea una nueva review para un paquete turístico"""
    try:
        # Asignar el autor actual
        review_data.autor_id = current_user.id
        
        review = await review_repository.create_review(review_data)
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/paquete/{paquete_id}", response_model=List[ReviewResponse])
async def get_reviews_by_paquete(
    paquete_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtiene las reviews de un paquete turístico"""
    try:
        reviews = await review_repository.get_reviews_by_paquete(paquete_id, skip, limit)
        return reviews
    except Exception as e:
        logger.error(f"Error al obtener reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review_by_id(review_id: str):
    """Obtiene una review específica"""
    try:
        review = await review_repository.get_review_by_id(review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review no encontrada"
            )
        
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 