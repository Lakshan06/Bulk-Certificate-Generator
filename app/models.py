import uuid
import datetime
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    completed_with_errors = "completed_with_errors"

class CertificateStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String, nullable=False)
    issue_date = Column(Date, nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.pending, nullable=False)
    total = Column(Integer, nullable=False)
    succeeded = Column(Integer, default=0, nullable=False)
    failed = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), index=True, nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    course = Column(String, nullable=True)
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.pending, nullable=False)
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="certificates")
