import re
from sqlalchemy.orm import Session
from app import models, schemas

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def validate_recipient(recipient: schemas.RecipientCreate) -> tuple[bool, str | None]:
    if not recipient.name or not recipient.name.strip():
        return False, "Name cannot be empty"
    if len(recipient.name) > 100:
        return False, "Name is too long"
    if not recipient.email or not EMAIL_REGEX.match(recipient.email):
        return False, "Invalid email format"
    return True, None

def create_job(db: Session, job_in: schemas.JobCreate) -> models.Job:
    job = models.Job(
        event_name=job_in.event_name,
        issue_date=job_in.issue_date,
        total=len(job_in.recipients)
    )
    db.add(job)
    db.flush() # get job.id

    for rec in job_in.recipients:
        is_valid, error_msg = validate_recipient(rec)
        cert = models.Certificate(
            job_id=job.id,
            recipient_name=rec.name,
            recipient_email=rec.email,
            course=rec.course
        )
        if not is_valid:
            cert.status = models.CertificateStatus.failed
            cert.error_message = error_msg
            job.failed += 1
        
        db.add(cert)
        
    db.commit()
    db.refresh(job)
    return job
