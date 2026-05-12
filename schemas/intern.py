from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class InternBase(BaseModel):
    name: str = Field(..., description="Nome completo do estagiário/aluno")
    contact: Optional[str] = Field(None, description="Contato (Telefone/Email)")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    is_active: bool = Field(True, description="Status de atividade do estagiário")

class InternCreate(InternBase):
    pass

class InternUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome completo do estagiário/aluno")
    contact: Optional[str] = Field(None, description="Contato (Telefone/Email)")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    is_active: Optional[bool] = Field(None, description="Status de atividade do estagiário")

class InternResponse(InternBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
