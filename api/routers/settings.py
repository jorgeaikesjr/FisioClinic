from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/clinic-type")
def get_clinic_type():
    """
    Retorna o tipo de clínica configurado no .env.
    Usado pelo frontend para mostrar/ocultar campos de pagamento.
    """
    return {"clinic_type": settings.CLINIC_TYPE}
