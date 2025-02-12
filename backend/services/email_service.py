import os
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import models
from services.ms_graph import MSGraphService
from config import settings

class EmailService:
    def __init__(self, db: Session, graph_service: MSGraphService):
        self.db = db
        self.graph_service = graph_service
        self.storage_path = settings.ATTACHMENT_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)
    
    def process_messages(self, mailbox_id: int, batch_size: int = 50) -> Dict[str, Any]:
        """Process messages from the mailbox"""
        mailbox = self.db.query(models.Mailbox).filter(models.Mailbox.id == mailbox_id).first()
        if not mailbox:
            raise ValueError("Mailbox not found")
        
        processed = 0
        try:
            messages = self.graph_service.get_messages(top=batch_size)
            for msg in messages:
                if self._should_process_message(msg):
                    self._process_single_message(msg, mailbox)
                    processed += 1
            
            # Update last sync time
            mailbox.last_sync = datetime.utcnow()
            self.db.commit()
            
            return {
                "status": "success",
                "processed": processed,
                "total": len(messages)
            }
        
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error processing messages: {str(e)}")
    
    def _should_process_message(self, message: Dict[str, Any]) -> bool:
        """Determine if a message should be processed"""
        # Check if message already exists
        existing = self.db.query(models.Email).filter(
            models.Email.internet_message_id == message.get("internetMessageId")
        ).first()
        
        return not existing
    
    def _process_single_message(self, message: Dict[str, Any], mailbox: models.Mailbox) -> None:
        """Process a single message and its attachments"""
        # Create email record
        email = models.Email(
            subject=message.get("subject", ""),
            sender=message.get("from", {}).get("emailAddress", {}).get("address", ""),
            recipients=[r.get("emailAddress", {}).get("address", "") 
                       for r in message.get("toRecipients", [])],
            received_datetime=datetime.fromisoformat(message.get("receivedDateTime", "")),
            body_text=message.get("body", {}).get("content", ""),
            body_html=message.get("body", {}).get("content", "") 
                     if message.get("body", {}).get("contentType", "") == "html" else None,
            internet_message_id=message.get("internetMessageId", ""),
            conversation_id=message.get("conversationId", ""),
            has_attachments=message.get("hasAttachments", False),
            mailbox_id=mailbox.id
        )
        
        self.db.add(email)
        self.db.flush()  # Get email.id without committing
        
        # Process attachments if any
        if email.has_attachments:
            self._process_attachments(message.get("id"), email.id)
    
    def _process_attachments(self, message_id: str, email_id: int) -> None:
        """Process attachments for a message"""
        attachments = self.graph_service.get_message_attachments(message_id)
        
        for att in attachments:
            # Create directory for attachments if it doesn't exist
            attachment_dir = os.path.join(self.storage_path, str(email_id))
            os.makedirs(attachment_dir, exist_ok=True)
            
            filename = att.get("name", "")
            storage_path = os.path.join(attachment_dir, filename)
            
            # Save attachment metadata
            attachment = models.Attachment(
                filename=filename,
                content_type=att.get("contentType", ""),
                size=att.get("size", 0),
                storage_path=storage_path,
                email_id=email_id
            )
            
            self.db.add(attachment)
            
            # Save attachment content
            if att.get("contentBytes"):
                with open(storage_path, "wb") as f:
                    f.write(att.get("contentBytes").encode())
