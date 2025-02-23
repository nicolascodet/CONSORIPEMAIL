import os
import pypff
import mailbox
from datetime import datetime
from typing import Dict, Any, List
import models
from database import SessionLocal
from config import settings
import shutil

class EmailFileProcessor:
    def __init__(self):
        self.db = SessionLocal()

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a PST or MBOX file."""
        try:
            # Create mailbox record
            mailbox_obj = models.Mailbox(
                name=os.path.basename(file_path),
                type='pst' if file_path.lower().endswith('.pst') else 'mbox',
                last_processed=datetime.utcnow()
            )
            self.db.add(mailbox_obj)
            self.db.commit()

            if file_path.lower().endswith('.pst'):
                stats = self.process_pst_file(file_path, mailbox_obj)
            elif file_path.lower().endswith('.mbox'):
                stats = self.process_mbox_file(file_path, mailbox_obj)
            else:
                raise ValueError("Unsupported file type")

            # Update mailbox stats
            mailbox_obj.total_messages = stats['total_messages']
            mailbox_obj.processed_messages = stats['processed_messages']
            self.db.commit()

            return stats
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    def process_pst_file(self, file_path: str, mailbox_obj: models.Mailbox) -> Dict[str, Any]:
        """Process a PST file."""
        try:
            pst = pypff.file()
            pst.open(file_path)
            root = pst.get_root_folder()
            
            stats = {
                'total_messages': 0,
                'processed_messages': 0,
                'attachments': 0
            }
            
            self._process_pst_folder(root, stats, mailbox_obj)
            
            return stats
        except Exception as e:
            print(f"Error processing PST file: {e}")
            raise

    def _process_pst_folder(self, folder: pypff.folder, stats: Dict[str, int], mailbox_obj: models.Mailbox) -> None:
        """Process a folder in a PST file."""
        for i in range(folder.get_number_of_sub_folders()):
            self._process_pst_folder(folder.get_sub_folder(i), stats, mailbox_obj)

        for i in range(folder.get_number_of_messages()):
            message = folder.get_message(i)
            stats['total_messages'] += 1
            
            try:
                self._process_email(
                    subject=message.get_subject() or "",
                    sender=message.get_sender_name() or "",
                    received_date=message.get_delivery_time(),
                    body=message.get_plain_text_body() or "",
                    attachments=self._get_pst_attachments(message),
                    mailbox_obj=mailbox_obj
                )
                stats['processed_messages'] += 1
            except Exception as e:
                print(f"Error processing message: {e}")

    def process_mbox_file(self, file_path: str, mailbox_obj: models.Mailbox) -> Dict[str, Any]:
        """Process an MBOX file."""
        try:
            mbox = mailbox.mbox(file_path)
            
            stats = {
                'total_messages': len(mbox),
                'processed_messages': 0,
                'attachments': 0
            }
            
            for message in mbox:
                try:
                    self._process_email(
                        subject=message['subject'] or "",
                        sender=message['from'] or "",
                        received_date=datetime.fromtimestamp(message.get_date()),
                        body=self._get_mbox_body(message),
                        attachments=self._get_mbox_attachments(message),
                        mailbox_obj=mailbox_obj
                    )
                    stats['processed_messages'] += 1
                except Exception as e:
                    print(f"Error processing message: {e}")
            
            return stats
        except Exception as e:
            print(f"Error processing MBOX file: {e}")
            raise

    def _process_email(self, subject: str, sender: str, received_date: datetime,
                      body: str, attachments: List[Dict[str, Any]], 
                      mailbox_obj: models.Mailbox) -> None:
        """Process a single email."""
        try:
            # Create or get sender contact
            contact = self.db.query(models.Contact).filter_by(email=sender).first()
            if not contact:
                # Try to extract organization from email domain
                org = None
                if '@' in sender:
                    domain = sender.split('@')[1]
                    org = self.db.query(models.Organization).filter_by(domain=domain).first()
                    if not org:
                        org = models.Organization(
                            name=domain.split('.')[0].capitalize(),
                            domain=domain
                        )
                        self.db.add(org)
                        self.db.flush()

                contact = models.Contact(
                    email=sender,
                    organization_id=org.id if org else None
                )
                self.db.add(contact)
                self.db.flush()

            # Create email record
            email = models.Email(
                subject=subject,
                sender_id=contact.id,
                received_date=received_date,
                body=body,
                importance='normal',
                mailbox_id=mailbox_obj.id
            )
            self.db.add(email)
            self.db.flush()

            # Process attachments
            for attachment_data in attachments:
                attachment = models.Attachment(
                    email_id=email.id,
                    filename=attachment_data['filename'],
                    storage_path=attachment_data['path'],
                    processed=False
                )
                self.db.add(attachment)
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def _get_pst_attachments(self, message: pypff.message) -> List[Dict[str, Any]]:
        """Extract attachments from a PST message."""
        attachments = []
        for i in range(message.get_number_of_attachments()):
            attachment = message.get_attachment(i)
            filename = attachment.get_name() or f"attachment_{i}"
            
            # Save attachment to file
            file_path = os.path.join(settings.attachment_storage_path, filename)
            with open(file_path, 'wb') as f:
                f.write(attachment.read_buffer())
            
            attachments.append({
                'filename': filename,
                'path': file_path
            })
        
        return attachments

    def _get_mbox_attachments(self, message: mailbox.Message) -> List[Dict[str, Any]]:
        """Extract attachments from an MBOX message."""
        attachments = []
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    # Save attachment to file
                    file_path = os.path.join(settings.attachment_storage_path, filename)
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    attachments.append({
                        'filename': filename,
                        'path': file_path,
                        'content_type': part.get_content_type()
                    })
        
        return attachments

    def _get_mbox_body(self, message: mailbox.Message) -> str:
        """Extract the text body from an MBOX message."""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        return message.get_payload(decode=True).decode() if message.get_payload() else ""
