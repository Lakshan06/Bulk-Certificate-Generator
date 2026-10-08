from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import os

router = APIRouter(prefix="/certificates", tags=["certificates"])

@router.get("/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if cert.status != models.CertificateStatus.success:
        raise HTTPException(status_code=409, detail="Certificate is not ready or failed to generate")
        
    if not cert.file_path or not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on disk")
        
    filename = f"{cert.recipient_name.replace(' ', '_')}_Certificate.pdf"
    return FileResponse(
        path=cert.file_path, 
        filename=filename, 
        media_type="application/pdf"
    )
