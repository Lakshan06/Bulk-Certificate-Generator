from app.services.generator import process_job
import zipfile
import io

def test_retrieving_certificates(client, db_session):
    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Retrieval Test",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Alice", "email": "alice@example.com"}
            ]
        }
    )
    job_id = response.json()["job_id"]
    
    certs_res = client.get(f"/api/v1/jobs/{job_id}/certificates")
    certs = certs_res.json()["certificates"]
    cert_id = certs[0]["id"]
    
    # Download single certificate
    download_res = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    
    # Download ZIP
    zip_res = client.get(f"/api/v1/jobs/{job_id}/download")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"
    
    zip_buffer = io.BytesIO(zip_res.content)
    with zipfile.ZipFile(zip_buffer, "r") as zip_file:
        files = zip_file.namelist()
        assert len(files) == 1
        assert "Alice" in files[0]
