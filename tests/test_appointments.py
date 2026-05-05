"""
test_appointments.py — Testes completos de agendamentos.

Cobre:
  - Criação (happy path + campos obrigatórios + validação de tipos)
  - Regras de negócio (data_fim > data_inicio, conflito de horário, paciente inativo)
  - Leitura, atualização de status e campos de pagamento
  - Cancelamento lógico (soft delete)
  - Endpoint de calendário
"""


# ─────────────────────────────────────────────────────────────────────────────
# CRIAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateAppointment:
    def test_create_ok(self, client, appointment_payload):
        r = client.post("/api/v1/appointments/", json=appointment_payload)
        assert r.status_code == 201
        body = r.json()
        assert body["patient_id"] == appointment_payload["patient_id"]
        assert body["intern_id"] == appointment_payload["intern_id"]
        assert body["status"] == "Agendado"
        assert "id" in body

    def test_create_with_payment_ok(self, client, appointment_payload):
        appointment_payload["payment_method"] = "Pix"
        appointment_payload["amount_paid"] = 150.0
        r = client.post("/api/v1/appointments/", json=appointment_payload)
        assert r.status_code == 201
        body = r.json()
        assert body["payment_method"] == "Pix"
        assert body["amount_paid"] == 150.0

    def test_create_missing_patient_id_returns_422(self, client, created_intern):
        r = client.post("/api/v1/appointments/", json={
            "intern_id": created_intern["id"],
            "start_time": "2026-06-10T09:00:00",
            "end_time":   "2026-06-10T09:50:00",
        })
        assert r.status_code == 422

    def test_create_missing_intern_id_returns_422(self, client, created_patient):
        r = client.post("/api/v1/appointments/", json={
            "patient_id": created_patient["id"],
            "start_time": "2026-06-10T09:00:00",
            "end_time":   "2026-06-10T09:50:00",
        })
        assert r.status_code == 422

    def test_create_missing_times_returns_422(self, client, created_patient, created_intern):
        r = client.post("/api/v1/appointments/", json={
            "patient_id": created_patient["id"],
            "intern_id":  created_intern["id"],
        })
        assert r.status_code == 422

    def test_create_invalid_datetime_format_returns_422(self, client, created_patient, created_intern):
        r = client.post("/api/v1/appointments/", json={
            "patient_id": created_patient["id"],
            "intern_id":  created_intern["id"],
            "start_time": "not-a-date",
            "end_time":   "also-not-a-date",
        })
        assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# REGRAS DE NEGÓCIO
# ─────────────────────────────────────────────────────────────────────────────

class TestAppointmentBusinessRules:
    def test_end_before_start_returns_400(self, client, appointment_payload):
        """data_fim <= data_inicio deve retornar 400."""
        payload = appointment_payload | {
            "start_time": "2026-06-10T10:00:00",
            "end_time":   "2026-06-10T09:00:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 400
        assert "término" in r.json()["detail"].lower() or "início" in r.json()["detail"].lower()

    def test_end_equal_start_returns_400(self, client, appointment_payload):
        payload = appointment_payload | {
            "start_time": "2026-06-10T09:00:00",
            "end_time":   "2026-06-10T09:00:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 400

    def test_conflict_same_intern_exact_overlap(self, client, appointment_payload, created_appointment):
        """Mesmo estagiário, mesmo horário → 400 (conflito exato)."""
        r = client.post("/api/v1/appointments/", json=appointment_payload)
        assert r.status_code == 400
        assert "conflito" in r.json()["detail"].lower() or "horário" in r.json()["detail"].lower()

    def test_conflict_partial_overlap_start_inside(self, client, appointment_payload, created_appointment):
        """Estagiário com agendamento 09:00-09:50; novo 09:30-10:20 → conflito."""
        payload = appointment_payload | {
            "start_time": "2026-06-10T09:30:00",
            "end_time":   "2026-06-10T10:20:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 400

    def test_conflict_partial_overlap_end_inside(self, client, appointment_payload, created_appointment):
        """Novo agendamento 08:30-09:30 sobrepõe com 09:00-09:50 → conflito."""
        payload = appointment_payload | {
            "start_time": "2026-06-10T08:30:00",
            "end_time":   "2026-06-10T09:30:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 400

    def test_conflict_containing_overlap(self, client, appointment_payload, created_appointment):
        """Novo agendamento engloba completamente o existente → conflito."""
        payload = appointment_payload | {
            "start_time": "2026-06-10T08:00:00",
            "end_time":   "2026-06-10T11:00:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 400

    def test_no_conflict_adjacent_after(self, client, appointment_payload, created_appointment):
        """09:50 imediato após 09:50 → sem conflito (toca mas não sobrepõe)."""
        payload = appointment_payload | {
            "start_time": "2026-06-10T09:50:00",
            "end_time":   "2026-06-10T10:40:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 201

    def test_no_conflict_adjacent_before(self, client, appointment_payload, created_appointment):
        """Agendamento que termina exatamente em 09:00 → sem conflito."""
        payload = appointment_payload | {
            "start_time": "2026-06-10T08:00:00",
            "end_time":   "2026-06-10T09:00:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 201

    def test_no_conflict_different_intern(self, client, appointment_payload, created_appointment, client_extra_intern):
        """Horário idêntico mas estagiário diferente → sem conflito."""
        payload = appointment_payload | {"intern_id": client_extra_intern["id"]}
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 201

    def test_multiple_appointments_same_patient_ok(self, client, appointment_payload, created_appointment, created_intern):
        """Paciente pode ter vários agendamentos em horários distintos."""
        # Cria um segundo estagiário para evitar conflito de estagiário
        r2 = client.post("/api/v1/interns/", json={"name": "Segundo Estagiário"})
        second_intern_id = r2.json()["id"]
        payload = appointment_payload | {
            "intern_id":  second_intern_id,
            "start_time": "2026-06-10T10:00:00",
            "end_time":   "2026-06-10T10:50:00",
        }
        r = client.post("/api/v1/appointments/", json=payload)
        assert r.status_code == 201

    def test_inactive_patient_cannot_be_scheduled(self, client, appointment_payload, created_patient):
        """Paciente inativo não pode ser agendado → 400."""
        pid = created_patient["id"]
        client.delete(f"/api/v1/patients/{pid}")  # inativa via soft delete
        r = client.post("/api/v1/appointments/", json=appointment_payload)
        assert r.status_code == 400
        assert "inativ" in r.json()["detail"].lower()

    def test_cancelled_appointment_does_not_block_same_slot(self, client, appointment_payload, created_appointment):
        """Após cancelar, o mesmo horário fica livre para o mesmo estagiário."""
        aid = created_appointment["id"]
        client.delete(f"/api/v1/appointments/{aid}")  # cancela
        r = client.post("/api/v1/appointments/", json=appointment_payload)
        assert r.status_code == 201


# Fixture auxiliar para testar diferente estagiário
import pytest

@pytest.fixture()
def client_extra_intern(client):
    r = client.post("/api/v1/interns/", json={"name": "Estagiário B"})
    return r.json()


# ─────────────────────────────────────────────────────────────────────────────
# LEITURA
# ─────────────────────────────────────────────────────────────────────────────

class TestReadAppointment:
    def test_list_empty(self, client):
        r = client.get("/api/v1/appointments/")
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_created(self, client, created_appointment):
        r = client.get("/api/v1/appointments/")
        ids = [a["id"] for a in r.json()]
        assert created_appointment["id"] in ids

    def test_get_by_id_ok(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.get(f"/api/v1/appointments/{aid}")
        assert r.status_code == 200
        assert r.json()["id"] == aid

    def test_get_by_id_not_found(self, client):
        r = client.get("/api/v1/appointments/nao-existe")
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# ATUALIZAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateAppointment:
    def test_update_status_to_realizado(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.patch(f"/api/v1/appointments/{aid}", json={"status": "Realizado"})
        assert r.status_code == 200
        assert r.json()["status"] == "Realizado"

    def test_update_status_to_faltou(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.patch(f"/api/v1/appointments/{aid}", json={"status": "Faltou"})
        assert r.status_code == 200
        assert r.json()["status"] == "Faltou"

    def test_update_payment_fields(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.patch(f"/api/v1/appointments/{aid}", json={
            "payment_method": "Dinheiro",
            "amount_paid": 80.0,
        })
        assert r.status_code == 200
        body = r.json()
        assert body["payment_method"] == "Dinheiro"
        assert body["amount_paid"] == 80.0

    def test_update_times_ok(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.patch(f"/api/v1/appointments/{aid}", json={
            "start_time": "2026-06-10T11:00:00",
            "end_time":   "2026-06-10T11:50:00",
        })
        assert r.status_code == 200

    def test_update_times_conflict_returns_400(self, client, appointment_payload, created_appointment, created_intern):
        """Mover horário para colidir com outro agendamento → 400."""
        # Cria segundo agendamento em horário diferente, mesmo estagiário
        payload2 = appointment_payload | {
            "start_time": "2026-06-10T11:00:00",
            "end_time":   "2026-06-10T11:50:00",
        }
        r2 = client.post("/api/v1/appointments/", json=payload2)
        assert r2.status_code == 201
        aid2 = r2.json()["id"]

        # Tenta mover o segundo para cima do primeiro
        r = client.patch(f"/api/v1/appointments/{aid2}", json={
            "start_time": "2026-06-10T09:20:00",
            "end_time":   "2026-06-10T10:10:00",
        })
        assert r.status_code == 400

    def test_update_not_found_returns_404(self, client):
        r = client.patch("/api/v1/appointments/nao-existe", json={"status": "Realizado"})
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# CANCELAMENTO (SOFT DELETE)
# ─────────────────────────────────────────────────────────────────────────────

class TestCancelAppointment:
    def test_cancel_changes_status(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.delete(f"/api/v1/appointments/{aid}")
        assert r.status_code == 200
        assert r.json()["status"] == "Cancelado"

    def test_cancel_with_reason(self, client, created_appointment):
        aid = created_appointment["id"]
        r = client.delete(f"/api/v1/appointments/{aid}?reason=Paciente+desmarcou")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "Cancelado"
        assert "desmarcou" in (body.get("cancel_reason") or "")

    def test_cancelled_appointment_still_in_list(self, client, created_appointment):
        aid = created_appointment["id"]
        client.delete(f"/api/v1/appointments/{aid}")
        r = client.get("/api/v1/appointments/")
        ids = [a["id"] for a in r.json()]
        assert aid in ids

    def test_cancel_not_found_returns_404(self, client):
        r = client.delete("/api/v1/appointments/nao-existe")
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT DE CALENDÁRIO
# ─────────────────────────────────────────────────────────────────────────────

class TestCalendarEndpoint:
    def test_calendar_returns_event(self, client, created_appointment):
        r = client.get("/api/v1/appointments/calendar?start=2026-06-10T00:00:00&end=2026-06-10T23:59:59")
        assert r.status_code == 200
        events = r.json()
        assert len(events) >= 1
        event = events[0]
        # Valida campos esperados pelo FullCalendar
        assert "id" in event
        assert "title" in event
        assert "start" in event
        assert "end" in event
        assert "status" in event

    def test_calendar_title_format(self, client, created_appointment, created_patient, created_intern):
        r = client.get("/api/v1/appointments/calendar?start=2026-06-10T00:00:00&end=2026-06-10T23:59:59")
        title = r.json()[0]["title"]
        assert created_patient["name"] in title
        assert created_intern["name"] in title

    def test_calendar_empty_range(self, client, created_appointment):
        """Intervalo fora do agendamento deve retornar lista vazia."""
        r = client.get("/api/v1/appointments/calendar?start=2025-01-01T00:00:00&end=2025-01-31T23:59:59")
        assert r.status_code == 200
        assert r.json() == []

    def test_calendar_missing_params_returns_422(self, client):
        r = client.get("/api/v1/appointments/calendar")
        assert r.status_code == 422
