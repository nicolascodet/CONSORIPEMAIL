import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
import logging
from sqlalchemy.orm import Session
import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextExtractionService:
    def __init__(self, db: Session):
        self.db = db
    
    def process_attachment(self, attachment_id: int) -> bool:
        """Process a single attachment and extract its text"""
        attachment = self.db.query(models.Attachment).filter(
            models.Attachment.id == attachment_id
        ).first()
        
        if not attachment or not os.path.exists(attachment.storage_path):
            logger.error(f"Attachment {attachment_id} not found or file missing")
            return False
        
        try:
            # Extract text based on file type
            text = self._extract_text(attachment.storage_path, attachment.content_type)
            if text:
                attachment.text_content = text
                attachment.text_extracted = True
                self.db.commit()
                return True
            
            logger.warning(f"No text extracted from attachment {attachment_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing attachment {attachment_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def process_unextracted_attachments(self) -> dict:
        """Process all attachments that haven't had text extracted yet"""
        attachments = self.db.query(models.Attachment).filter(
            models.Attachment.text_extracted == False
        ).all()
        
        results = {"success": 0, "failed": 0, "total": len(attachments)}
        
        for attachment in attachments:
            success = self.process_attachment(attachment.id)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def _extract_text(self, file_path: str, content_type: str) -> Optional[str]:
        """Extract text from a file based on its content type"""
        if not os.path.exists(file_path):
            return None
            
        try:
            if "pdf" in content_type.lower():
                return self._extract_pdf_text(file_path)
            elif "word" in content_type.lower() or file_path.endswith(".docx"):
                return self._extract_docx_text(file_path)
            else:
                logger.warning(f"Unsupported file type: {content_type}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return None
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from a PDF file"""
        text = []
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            for page in pdf.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from a DOCX file"""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
