import datetime
import traceback
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.config import settings
from app.certificate.renderer import render_certificate

def process_job(job_id: str):
    db: Session = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return
        
        job.status = models.JobStatus.processing
        db.commit()

        # Get all pending certificates
        pending_certs = db.query(models.Certificate).filter(
            models.Certificate.job_id == job_id,
            models.Certificate.status == models.CertificateStatus.pending
        ).all()

        for cert in pending_certs:
            try:
                output_path = settings.output_dir / f"{cert.id}.pdf"
                render_certificate(
                    recipient_name=cert.recipient_name,
                    course=cert.course,
                    event_name=job.event_name,
                    issue_date=job.issue_date,
                    output_path=output_path,
                )
                
                cert.status = models.CertificateStatus.success
                cert.file_path = str(output_path.absolute())
                job.succeeded += 1
            except Exception as e:
                cert.status = models.CertificateStatus.failed
                cert.error_message = str(e)
                job.failed += 1
            
            # Commit progress after each item as per plan
            db.commit()

        # Update final job status
        job.completed_at = datetime.datetime.utcnow()
        if job.failed == 0:
            job.status = models.JobStatus.completed
        else:
            job.status = models.JobStatus.completed_with_errors
        
        db.commit()

    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        traceback.print_exc()
    finally:
        db.close()
