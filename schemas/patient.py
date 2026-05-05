from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class PatientBase(BaseModel):
    name: str = Field(..., description="Nome completo do paciente")
    contact: str = Field(..., description="Telefone ou e-mail de contato")
    guardian: Optional[str] = Field(None, description="Nome do responsável (se menor de idade)")
    anamnesis: Optional[str] = Field(None, description="Descrição da anamnese inicial")
    is_active: bool = Field(True, description="Status de atividade do paciente")

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome completo do paciente")
    contact: Optional[str] = Field(None, description="Telefone ou e-mail de contato")
    guardian: Optional[str] = Field(None, description="Nome do responsável (se menor de idade)")
    anamnesis: Optional[str] = Field(None, description="Descrição da anamnese inicial")
    is_active: Optional[bool] = Field(None, description="Status de atividade do paciente")

class PatientResponse(PatientBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
