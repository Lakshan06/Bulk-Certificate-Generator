import pytest
from unittest.mock import patch

def test_individual_certificate_failure(client, db_session):
    original_render = __import__("app.certificate.renderer", fromlist=["render_certificate"]).render_certificate
    
    def mock_render(recipient_name, course, event_name, issue_date, output_path):
        if recipient_name == "Alice":
            raise ValueError("Simulated rendering failure")
        return original_render(recipient_name, course, event_name, issue_date, output_path)

    with patch("app.services.generator.render_certificate", side_effect=mock_render):
        response = client.post(
            "/api/v1/jobs",
            json={
                "event_name": "Failure Test",
                "issue_date": "2026-10-08",
                "recipients": [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"}
                ]
            }
        )
        job_id = response.json()["job_id"]
        
    status_res = client.get(f"/api/v1/jobs/{job_id}")
    data = status_res.json()
    assert data["status"] == "completed_with_errors"
    assert data["succeeded"] == 1
    assert data["failed"] == 1
    
    certs_res = client.get(f"/api/v1/jobs/{job_id}/certificates")
    certs = certs_res.json()["certificates"]
    
    alice_cert = next(c for c in certs if c["recipient_name"] == "Alice")
    assert alice_cert["status"] == "failed"
    assert "Simulated rendering failure" in alice_cert["error_message"]
    
    bob_cert = next(c for c in certs if c["recipient_name"] == "Bob")
    assert bob_cert["status"] == "success"
