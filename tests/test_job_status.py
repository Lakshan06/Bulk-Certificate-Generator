from unittest.mock import patch

def test_job_status_and_progress(client, db_session):
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        response = client.post(
            "/api/v1/jobs",
            json={
                "event_name": "Status Test",
                "issue_date": "2026-10-08",
                "recipients": [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"}
                ]
            }
        )
        job_id = response.json()["job_id"]
        
        # Check status before processing
        status_res = client.get(f"/api/v1/jobs/{job_id}")
        assert status_res.status_code == 200
        assert status_res.json()["status"] == "pending"
    
    # Run the generator synchronously for the test
    from app.services.generator import process_job
    process_job(job_id)
    
    # Check status after processing
    status_res2 = client.get(f"/api/v1/jobs/{job_id}")
    data = status_res2.json()
    assert data["status"] == "completed"
    assert data["succeeded"] == 2
    assert data["failed"] == 0
    assert data["progress_percent"] == 100.0
