# Bulk Certificate Generator

A backend API for generating bulk certificates asynchronously. Built with Python, FastAPI, and SQLite.

## Overview
This API allows clients to submit a list of recipients and generate customized PDF certificates for all of them in bulk. Processing happens asynchronously in the background. It provides robust error handling to ensure that if one certificate generation fails, the rest of the job continues seamlessly.

## Tech Stack
- **Framework:** FastAPI
- **Database & ORM:** SQLite via SQLAlchemy 2.0
- **PDF Generation:** ReportLab
- **Background Task:** FastAPI BackgroundTasks
- **Testing:** Pytest

## Setup

1. **Clone the repository and enter the directory:**
   ```bash
   git clone <repo-url>
   cd bulk-certificate-generator
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the example config:
   ```bash
   cp .env.example .env
   ```

## Run the Server

Start the FastAPI application:
```bash
uvicorn app.main:app --reload
```
The interactive Swagger API documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Web UI
A simple frontend is available at: [http://localhost:8000/ui](http://localhost:8000/ui)
It allows you to:
- Easily submit a job by filling out a form
- Poll and visualize the background job progress in real-time
- View results and download individual certificates or the full ZIP archive


## Run Tests
Run the test suite with pytest:
```bash
pytest -v
```

## API Usage Examples

### 1. Submit a Request
Submit a bulk request to create a certificate generation job.
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/jobs" \
     -H "Content-Type: application/json" \
     -d '{
       "event_name": "Python Bootcamp 2026",
       "issue_date": "2026-10-08",
       "recipients": [
         {"name": "Arun Kumar", "email": "arun@example.com", "course": "Python Basics"},
         {"name": "Priya S", "email": "priya@example.com", "course": "Python Basics"}
       ]
     }'
```
*Returns a `202 Accepted` status with a `job_id`.*

### 2. Check Status
Poll the job status using the `job_id`:
```bash
curl "http://127.0.0.1:8000/api/v1/jobs/{job_id}"
```

### 3. Retrieve Certificates
Download a ZIP file containing all successful certificates for the job:
```bash
curl -OJ "http://127.0.0.1:8000/api/v1/jobs/{job_id}/download"
```
Or download a single certificate by its ID (obtained from `/api/v1/jobs/{job_id}/certificates`):
```bash
curl -OJ "http://127.0.0.1:8000/api/v1/certificates/{certificate_id}/download"
```

## Design Decisions

- **Why FastAPI:** Provides built-in request validation (Pydantic), automatic OpenAPI documentation, and very clean routing.
- **Background Processing:** A request with thousands of certificates will time out if processed synchronously. BackgroundTasks allows for instant client response, while the generator processes one by one.
- **Why SQLite:** Requires zero setup, making it very easy for anyone to run the project. Switching to PostgreSQL only requires changing the `DATABASE_URL` config.
- **Isolated Failures:** Each certificate generation is wrapped in a `try/except` block. Recipient-level validation is handled carefully so one failure does not halt the entire job.
- **UUID Filenames:** Eliminates path traversal and special-character risks on disk.
- **Layered Architecture:** Routes (`HTTP` logic), Services (`business/database` logic), and Certificate Renderer (pure function). This keeps the system highly testable and loosely coupled.

## Future Improvements
- Migration to **Celery/RQ** with a Redis broker for a durable queue (avoids losing in-progress jobs if the server restarts).
- **Cloud Storage** (AWS S3) for certificates instead of local disk.
- Adding **Authentication** (e.g., OAuth2 or API keys).
- Implementing email delivery of certificates.
