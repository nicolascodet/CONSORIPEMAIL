from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from services.file_processor import EmailFileProcessor
from services.email_service import EmailService
from services.llm_analyzer import LLMAnalyzer, EmailAnalysis
from database import SessionLocal, engine
import models
import uvicorn
from typing import List, Dict
import schemas
from services.text_extraction import TextExtractionService
import traceback
import os
from config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process PST or MBOX file"""
    # Validate file type
    if not file.filename.lower().endswith(('.pst', '.mbox')):
        raise HTTPException(
            status_code=400,
            detail="Only .pst and .mbox files are supported"
        )
    
    # Save uploaded file
    file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file
        processor = EmailFileProcessor(db)
        if file.filename.lower().endswith('.pst'):
            stats = processor.process_pst_file(file_path)
        else:
            stats = processor.process_mbox_file(file_path)
        
        # Cleanup
        processor.cleanup_upload(file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "stats": stats
        }
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

@app.get("/mailboxes")
def list_mailboxes(db: Session = Depends(get_db)):
    """List all processed mailboxes"""
    mailboxes = db.query(models.Mailbox).all()
    return mailboxes

@app.post("/process-attachments")
def process_attachments(db: Session = Depends(get_db)):
    """Process all unprocessed attachments and extract text"""
    text_service = TextExtractionService()
    try:
        attachments = db.query(models.Attachment).filter(
            models.Attachment.processed == False
        ).all()
        
        for attachment in attachments:
            try:
                extracted_text = text_service.extract_text(attachment.storage_path)
                attachment.extracted_text = extracted_text
                attachment.processed = True
                db.add(attachment)
            except Exception as e:
                print(f"Failed to process attachment {attachment.id}: {str(e)}")
        
        db.commit()
        return {"status": "success", "processed": len(attachments)}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process attachments: {str(e)}"
        )

@app.get("/organizations")
def get_organizations(db: Session = Depends(get_db)):
    """Get list of organizations from email domains"""
    return db.query(models.Organization).all()

@app.get("/contacts")
def get_contacts(db: Session = Depends(get_db)):
    """Get list of contacts from emails"""
    return db.query(models.Contact).all()

llm_analyzer = LLMAnalyzer()

@app.get("/emails/{email_id}/analysis")
async def analyze_email(email_id: int, db: Session = Depends(get_db)) -> EmailAnalysis:
    """
    Analyze a single email using LLM to extract insights.
    """
    email = db.query(models.Email).filter(models.Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Get sender and recipients
    sender = db.query(models.Contact).filter(models.Contact.id == email.sender_id).first()
    recipients = []  # You'll need to implement recipient tracking in your models

    analysis = await llm_analyzer.analyze_email(
        subject=email.subject,
        body=email.body,
        sender=sender.email if sender else "",
        recipients=recipients
    )
    return analysis

@app.get("/threads/{thread_id}/analysis")
async def analyze_thread(thread_id: str, db: Session = Depends(get_db)):
    """
    Analyze an email thread using LLM.
    """
    # You'll need to implement thread tracking in your models
    emails = db.query(models.Email).filter(models.Email.thread_id == thread_id).all()
    if not emails:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread_emails = []
    for email in emails:
        sender = db.query(models.Contact).filter(models.Contact.id == email.sender_id).first()
        thread_emails.append({
            "sender": sender.email if sender else "",
            "timestamp": email.received_date,
            "subject": email.subject,
            "body": email.body
        })

    analysis = await llm_analyzer.analyze_thread(thread_emails)
    return analysis

@app.get("/attachments/{attachment_id}/analysis")
async def analyze_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """
    Analyze an email attachment using LLM.
    """
    attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Read attachment content
    file_path = os.path.join(settings.ATTACHMENT_STORAGE_PATH, attachment.file_path)
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read attachment: {str(e)}")

    analysis = await llm_analyzer.analyze_attachment_content(content, attachment.filename)
    return analysis

@app.get("/emails/search")
async def semantic_search(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Perform semantic search across emails using LLM embeddings.
    """
    # This would be implemented using embeddings for better performance
    # For now, we'll use the LLM to analyze the query and find relevant emails
    raise HTTPException(status_code=501, detail="Semantic search not yet implemented")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
