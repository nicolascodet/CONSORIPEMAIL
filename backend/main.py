from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from services.ms_graph import MSGraphService
from services.email_service import EmailService
from database import SessionLocal, engine
import models
import uvicorn
from typing import List, Dict
import schemas
from services.text_extraction import TextExtractionService
import traceback

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_service = AuthService()
ms_graph_service = MSGraphService()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "running"}

@app.get("/auth/microsoft")
async def get_auth_url(request: Request):
    """Get Microsoft OAuth authorization URL"""
    try:
        print(f"Generating auth URL. Client IP: {request.client.host}")
        return auth_service.get_auth_url()
    except Exception as e:
        print(f"Error in get_auth_url: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/microsoft/callback")
async def auth_callback(
    request: Request,
    code: str,
    code_verifier: str,
    db: Session = Depends(get_db)
):
    """Handle Microsoft OAuth callback"""
    try:
        print(f"Received callback. Client IP: {request.client.host}")
        print(f"Code length: {len(code)}, Code verifier length: {len(code_verifier)}")
        
        # Get token from auth code
        token_data = auth_service.get_token(code, code_verifier)
        if not token_data:
            raise HTTPException(status_code=400, detail="Failed to get token")
            
        # Get user info using the access token
        print("Getting user info with access token")
        user_info = ms_graph_service.get_user_info(token_data["access_token"])
        
        # Create or update user in database
        print(f"Saving user info for: {user_info.get('mail')}")
        user = models.User(
            email=user_info["mail"],
            name=user_info["displayName"],
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"]
        )
        db.add(user)
        db.commit()
        
        return {"message": "Authentication successful", "user": user_info}
    except Exception as e:
        print(f"Error in auth_callback: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user")
async def get_user_info(request: Request, token: str):
    """Get user info from Microsoft Graph API"""
    try:
        print(f"Getting user info. Client IP: {request.client.host}")
        return ms_graph_service.get_user_info(token)
    except Exception as e:
        print(f"Error in get_user_info: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mailboxes/", response_model=schemas.Mailbox)
def create_mailbox(mailbox: schemas.MailboxCreate, db: Session = Depends(get_db)):
    """Add a new mailbox for email ingestion"""
    try:
        db_mailbox = models.Mailbox(**mailbox.dict())
        db.add(db_mailbox)
        db.commit()
        db.refresh(db_mailbox)
        return db_mailbox
    except Exception as e:
        print(f"Error in create_mailbox: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mailboxes/", response_model=List[schemas.Mailbox])
def list_mailboxes(db: Session = Depends(get_db)):
    """List all connected mailboxes"""
    try:
        return db.query(models.Mailbox).all()
    except Exception as e:
        print(f"Error in list_mailboxes: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mailboxes/{mailbox_id}/ingest")
def start_ingestion(mailbox_id: int, db: Session = Depends(get_db)):
    """Start email ingestion for a mailbox"""
    try:
        mailbox = db.query(models.Mailbox).filter(models.Mailbox.id == mailbox_id).first()
        if not mailbox:
            raise HTTPException(status_code=404, detail="Mailbox not found")
        
        # Initialize services
        graph_service = MSGraphService(access_token=mailbox.access_token)
        email_service = EmailService(db=db, graph_service=graph_service)
        
        # Process messages
        result = email_service.process_messages(mailbox_id)
        return {"status": "success", "details": result}
    except Exception as e:
        print(f"Error in start_ingestion: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-attachments")
def process_attachments(db: Session = Depends(get_db)):
    """Process all unprocessed attachments and extract text"""
    try:
        extraction_service = TextExtractionService(db)
        results = extraction_service.process_unextracted_attachments()
        return {
            "status": "success",
            "processed": results["success"],
            "failed": results["failed"],
            "total": results["total"]
        }
    except Exception as e:
        print(f"Error in process_attachments: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-attachment/{attachment_id}")
def process_single_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Process a single attachment and extract its text"""
    try:
        extraction_service = TextExtractionService(db)
        success = extraction_service.process_attachment(attachment_id)
        if success:
            return {"status": "success", "message": "Text extracted successfully"}
        else:
            return {"status": "failed", "message": "Failed to extract text"}
    except Exception as e:
        print(f"Error in process_single_attachment: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations")
def get_organizations(db: Session = Depends(get_db)):
    try:
        return {"message": "Will return organizations"}
    except Exception as e:
        print(f"Error in get_organizations: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts")
def get_contacts(db: Session = Depends(get_db)):
    try:
        return {"message": "Will return contacts"}
    except Exception as e:
        print(f"Error in get_contacts: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
