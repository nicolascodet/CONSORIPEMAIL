from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EmailBase(BaseModel):
    subject: str
    sender: str
    recipients: List[str]
    received_datetime: datetime
    body_text: str
    body_html: Optional[str]
    internet_message_id: str
    conversation_id: str
    has_attachments: bool

class EmailCreate(EmailBase):
    pass

class Email(EmailBase):
    id: int
    mailbox_id: str

    class Config:
        from_attributes = True

class MailboxBase(BaseModel):
    email: str
    access_token: str
    refresh_token: str

class MailboxCreate(MailboxBase):
    pass

class Mailbox(MailboxBase):
    id: int
    last_sync: Optional[datetime] = None

    class Config:
        from_attributes = True
