from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import asyncio
import os
import shutil
from sse_starlette.sse import EventSourceResponse

from app.database import get_db
from app.models.admission import AdmissionApplication
from app.services.auth import require_role

router = APIRouter(prefix="/admission", tags=["admission"])

class AdmissionCreate(BaseModel):
    target_org_id: int
    applicant_person_id: Optional[int] = None
    status: str = "ENQUIRY"

class AdmissionResponse(BaseModel):
    id: int
    target_org_id: int
    applicant_person_id: Optional[int]
    status: str
    is_locked: bool
    documents: Dict[str, Any]
    applied_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=AdmissionResponse)
async def create_application(app: AdmissionCreate, db: AsyncSession = Depends(get_db)):
    db_app = AdmissionApplication(**app.model_dump())
    db.add(db_app)
    await db.commit()
    await db.refresh(db_app)
    return db_app

@router.get("/", response_model=List[AdmissionResponse])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdmissionApplication))
    return result.scalars().all()

@router.post("/{app_id}/upload-document", response_model=AdmissionResponse)
async def upload_document(
    app_id: int, 
    doc_type: str, # e.g., 'birth_certificate', 'father_nic', 'transfer_certificate'
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    # Fetch application
    result = await db.execute(select(AdmissionApplication).where(AdmissionApplication.id == app_id))
    db_app = result.scalars().first()
    
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    if db_app.is_locked:
        raise HTTPException(status_code=403, detail="Application is locked by admin. Documents cannot be modified.")
        
    # Create directory: uploads/registration_{id}/
    upload_dir = f"uploads/registration_{app_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update documents JSON
    docs = dict(db_app.documents) if db_app.documents else {}
    docs[doc_type] = file_path
    db_app.documents = docs
    
    await db.commit()
    await db.refresh(db_app)
    return db_app

@router.post("/{app_id}/lock", response_model=AdmissionResponse)
async def lock_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    result = await db.execute(select(AdmissionApplication).where(AdmissionApplication.id == app_id))
    db_app = result.scalars().first()
    
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    db_app.is_locked = True
    await db.commit()
    await db.refresh(db_app)
    return db_app

class StatusUpdate(BaseModel):
    status: str

@router.put("/{app_id}/status", response_model=AdmissionResponse)
async def update_status(
    app_id: int,
    status_update: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    result = await db.execute(select(AdmissionApplication).where(AdmissionApplication.id == app_id))
    db_app = result.scalars().first()
    
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    db_app.status = status_update.status
    if status_update.status in ["ACCEPTED", "REJECTED", "WITHDRAWN"]:
        db_app.decided_at = datetime.utcnow()
        
    await db.commit()
    await db.refresh(db_app)
    return db_app


# --- Load Control & In-Memory Queue Demonstration ---
admission_queue = asyncio.Queue()

async def admission_worker():
    while True:
        app_id, user_channel = await admission_queue.get()
        # Simulate heavy processing that would otherwise block or crash the server under load
        await user_channel.put(f"Processing application {app_id}...")
        await asyncio.sleep(2)
        
        await user_channel.put("Running background checks...")
        await asyncio.sleep(2)
        
        await user_channel.put(f"Application {app_id} processing complete!")
        await user_channel.put(None)  # Signal completion
        admission_queue.task_done()

@router.get("/{app_id}/process-heavy")
async def process_heavy_admission(app_id: int, request: Request):
    """
    Demonstrates in-memory queueing with SSE to prevent Cloud Run timeouts
    and give real-time feedback without using Redis.
    """
    user_channel = asyncio.Queue()
    position = admission_queue.qsize() + 1
    
    # Place the job in the queue
    await admission_queue.put((app_id, user_channel))
    
    async def event_generator():
        # Inform the user they are queued immediately
        yield {"data": f"Job queued. You are position {position} in line."}
        
        while True:
            # If client disconnects early, break
            if await request.is_disconnected():
                break
                
            msg = await user_channel.get()
            if msg is None:
                yield {"data": "DONE"}
                break
            yield {"data": msg}
            
    return EventSourceResponse(event_generator())
