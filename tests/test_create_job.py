from app import models

def test_create_job_success(client, db_session):
    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Test Event",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Alice", "email": "alice@example.com"}
            ]
        }
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["total"] == 1
    
    # Check DB
    job = db_session.query(models.Job).filter(models.Job.id == data["job_id"]).first()
    assert job is not None
    assert job.total == 1
