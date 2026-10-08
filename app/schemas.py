import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from app.models import JobStatus, CertificateStatus

class RecipientCreate(BaseModel):
    name: str
    email: str
    course: Optional[str] = None

class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=1)
    issue_date: datetime.date
    recipients: List[RecipientCreate] = Field(..., min_length=1)

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    total: int

class JobStatusResponse(BaseModel):
    job_id: str
    event_name: str
    status: JobStatus
    total: int
    succeeded: int
    failed: int
    progress_percent: float
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

class CertificateResponse(BaseModel):
    id: str
    recipient_name: str
    recipient_email: str
    course: Optional[str]
    status: CertificateStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime.datetime
    
    model_config = {"from_attributes": True}

class CertificateListResponse(BaseModel):
    certificates: List[CertificateResponse]
