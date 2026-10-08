from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import JobCreate, JobResponse, JobStatusResponse, CertificateListResponse
from app.services import job_service, generator
from app.config import settings
from app import models
import zipfile
import io
import os
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(job_in: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if len(job_in.recipients) > settings.max_recipients_per_job:
        raise HTTPException(
            status_code=422,
            detail=f"Too many recipients. Maximum is {settings.max_recipients_per_job}."
        )
    
    job = job_service.create_job(db, job_in)
    
    background_tasks.add_task(generator.process_job, job.id)
    
    return JobResponse(job_id=job.id, status=job.status, total=job.total)

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    progress = 0.0
    if job.total > 0:
        progress = ((job.succeeded + job.failed) / job.total) * 100.0
    
    return JobStatusResponse(
        job_id=job.id,
        event_name=job.event_name,
        status=job.status,
        total=job.total,
        succeeded=job.succeeded,
        failed=job.failed,
        progress_percent=progress,
        created_at=job.created_at,
        completed_at=job.completed_at
    )

@router.get("/{job_id}/certificates", response_model=CertificateListResponse)
def get_job_certificates(job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return CertificateListResponse(certificates=job.certificates)

@router.get("/{job_id}/download")
def download_job_certificates_zip(job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    successful_certs = [c for c in job.certificates if c.status == models.CertificateStatus.success]
    if not successful_certs:
        raise HTTPException(status_code=409, detail="No successful certificates available for download yet")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for cert in successful_certs:
            if cert.file_path and os.path.exists(cert.file_path):
                filename = f"{cert.recipient_name.replace(' ', '_')}_{cert.id}.pdf"
                zip_file.write(cert.file_path, arcname=filename)
                
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=certificates_{job_id}.zip"}
    )
