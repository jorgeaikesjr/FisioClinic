from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    patient_id: str = Field(..., description="ID do paciente associado ao agendamento")
    intern_id: str = Field(..., description="ID do estagiário associado ao agendamento")
    start_time: datetime = Field(..., description="Data e hora de início")
    end_time: datetime = Field(..., description="Data e hora de término")

class AppointmentCreate(AppointmentBase):
    payment_method: Optional[str] = Field(None, description="Forma de pagamento (Pix, Dinheiro, Cartão de Crédito, Cartão de Débito, Transferência)")
    amount_paid: Optional[float] = Field(None, description="Valor pago pelo paciente")
    recurrence_days: Optional[list[int]] = Field(None, description="Dias da semana para recorrência (0=Seg, 6=Dom)")
    recurrence_weeks: Optional[int] = Field(None, description="Número de semanas para a recorrência")

class AppointmentUpdate(BaseModel):
    patient_id: Optional[str] = Field(None, description="ID do paciente")
    intern_id: Optional[str] = Field(None, description="ID do estagiário")
    start_time: Optional[datetime] = Field(None, description="Data e hora de início")
    end_time: Optional[datetime] = Field(None, description="Data e hora de término")
    status: Optional[str] = Field(None, description="Status do agendamento (Agendado, Cancelado, Realizado, Faltou)")
    cancel_reason: Optional[str] = Field(None, description="Motivo do cancelamento")
    payment_method: Optional[str] = Field(None, description="Forma de pagamento")
    amount_paid: Optional[float] = Field(None, description="Valor pago")

class AppointmentResponse(AppointmentBase):
    id: str
    status: str
    cancel_reason: Optional[str] = None
    payment_method: Optional[str] = None
    amount_paid: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class CalendarEventResponse(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
