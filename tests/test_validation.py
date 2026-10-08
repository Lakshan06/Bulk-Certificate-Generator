def test_validation_empty_recipients(client):
    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Test Event",
            "issue_date": "2026-10-08",
            "recipients": []
        }
    )
    assert response.status_code == 422

def test_validation_missing_event_name(client):
    response = client.post(
        "/api/v1/jobs",
        json={
            "issue_date": "2026-10-08",
            "recipients": [{"name": "Alice", "email": "alice@example.com"}]
        }
    )
    assert response.status_code == 422

def test_validation_invalid_recipient_marks_failed(client):
    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Test Event",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "", "email": "invalid-email"}
            ]
        }
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    cert_response = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert cert_response.status_code == 200
    certs = cert_response.json()["certificates"]
    
    assert len(certs) == 2
    failed_cert = next(c for c in certs if c["status"] == "failed")
    assert failed_cert["error_message"] == "Name cannot be empty"
