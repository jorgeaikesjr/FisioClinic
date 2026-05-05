"""
test_reports.py — Testes dos endpoints de relatórios.
"""


class TestAbsencesReport:
    def test_empty_report(self, client):
        r = client.get("/api/v1/reports/absences")
        assert r.status_code == 200
        assert r.json() == []

    def test_faltou_appears_in_report(self, client, created_appointment):
        aid = created_appointment["id"]
        client.patch(f"/api/v1/appointments/{aid}", json={"status": "Faltou"})

        r = client.get("/api/v1/reports/absences")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["absences_count"] == 1

    def test_realizado_not_in_absences_report(self, client, created_appointment):
        aid = created_appointment["id"]
        client.patch(f"/api/v1/appointments/{aid}", json={"status": "Realizado"})
        r = client.get("/api/v1/reports/absences")
        assert r.json() == []

    def test_cancelled_not_in_absences_report(self, client, created_appointment):
        aid = created_appointment["id"]
        client.delete(f"/api/v1/appointments/{aid}")
        r = client.get("/api/v1/reports/absences")
        assert r.json() == []

    def test_filter_by_date_range_hit(self, client, created_appointment):
        aid = created_appointment["id"]
        client.patch(f"/api/v1/appointments/{aid}", json={"status": "Faltou"})
        r = client.get("/api/v1/reports/absences?start_date=2026-06-01T00:00:00&end_date=2026-06-30T23:59:59")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_filter_by_date_range_miss(self, client, created_appointment):
        aid = created_appointment["id"]
        client.patch(f"/api/v1/appointments/{aid}", json={"status": "Faltou"})
        # Agendamento é em junho/2026, filtro é em janeiro
        r = client.get("/api/v1/reports/absences?start_date=2026-01-01T00:00:00&end_date=2026-01-31T23:59:59")
        assert r.status_code == 200
        assert r.json() == []

    def test_ordered_by_absences_desc(self, client, created_patient, created_intern):
        """Paciente com mais faltas deve aparecer primeiro."""
        # Cria um segundo paciente
        r2 = client.post("/api/v1/patients/", json={"name": "Segundo Paciente", "contact": "11000000000"})
        p2_id = r2.json()["id"]

        # 1 falta para o primeiro paciente
        r = client.post("/api/v1/appointments/", json={
            "patient_id": created_patient["id"],
            "intern_id": created_intern["id"],
            "start_time": "2026-06-10T09:00:00",
            "end_time": "2026-06-10T09:50:00",
        })
        client.patch(f"/api/v1/appointments/{r.json()['id']}", json={"status": "Faltou"})

        # 2 faltas para o segundo paciente (precisa de 2 estagiários distintos)
        r2_intern = client.post("/api/v1/interns/", json={"name": "Outro Estagiário"})
        intern2_id = r2_intern.json()["id"]

        for start, end, intern in [
            ("2026-06-11T09:00:00", "2026-06-11T09:50:00", created_intern["id"]),
            ("2026-06-11T10:00:00", "2026-06-11T10:50:00", intern2_id),
        ]:
            ra = client.post("/api/v1/appointments/", json={
                "patient_id": p2_id,
                "intern_id": intern,
                "start_time": start,
                "end_time": end,
            })
            client.patch(f"/api/v1/appointments/{ra.json()['id']}", json={"status": "Faltou"})

        r = client.get("/api/v1/reports/absences")
        data = r.json()
        assert data[0]["absences_count"] >= data[1]["absences_count"]


class TestWeeklySummaryReport:
    def test_missing_params_returns_422(self, client):
        r = client.get("/api/v1/reports/weekly-summary")
        assert r.status_code == 422

    def test_empty_week(self, client):
        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-06-01T00:00:00&end_date=2026-06-07T23:59:59")
        assert r.status_code == 200
        assert r.json() == []

    def test_appointment_in_range_appears(self, client, created_appointment):
        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-06-10T00:00:00&end_date=2026-06-10T23:59:59")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert "patient_name" in data[0]
        assert "start_time" in data[0]
        assert "end_time" in data[0]
        assert "status" in data[0]

    def test_cancelled_excluded_from_summary(self, client, created_appointment):
        aid = created_appointment["id"]
        client.delete(f"/api/v1/appointments/{aid}")
        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-06-10T00:00:00&end_date=2026-06-10T23:59:59")
        assert r.json() == []

    def test_faltou_included_in_summary(self, client, created_appointment):
        aid = created_appointment["id"]
        client.patch(f"/api/v1/appointments/{aid}", json={"status": "Faltou"})
        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-06-10T00:00:00&end_date=2026-06-10T23:59:59")
        data = r.json()
        assert len(data) == 1
        assert data[0]["status"] == "Faltou"

    def test_payment_fields_present(self, client, appointment_payload):
        appointment_payload["payment_method"] = "Cartão de Crédito"
        appointment_payload["amount_paid"] = 200.0
        r = client.post("/api/v1/appointments/", json=appointment_payload)
        assert r.status_code == 201

        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-06-10T00:00:00&end_date=2026-06-10T23:59:59")
        data = r.json()
        assert data[0]["payment_method"] == "Cartão de Crédito"
        assert data[0]["amount_paid"] == 200.0

    def test_out_of_range_excluded(self, client, created_appointment):
        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-01-01T00:00:00&end_date=2026-01-07T23:59:59")
        assert r.json() == []

    def test_ordered_by_start_time(self, client, created_patient, created_intern):
        """Resultados devem estar em ordem cronológica."""
        intern2 = client.post("/api/v1/interns/", json={"name": "Estagiário 2"}).json()

        for start, end, intern in [
            ("2026-06-10T14:00:00", "2026-06-10T14:50:00", intern2["id"]),
            ("2026-06-10T09:00:00", "2026-06-10T09:50:00", created_intern["id"]),
        ]:
            client.post("/api/v1/appointments/", json={
                "patient_id": created_patient["id"],
                "intern_id": intern,
                "start_time": start,
                "end_time": end,
            })

        r = client.get("/api/v1/reports/weekly-summary?start_date=2026-06-10T00:00:00&end_date=2026-06-10T23:59:59")
        data = r.json()
        assert len(data) == 2
        assert data[0]["start_time"] < data[1]["start_time"]
