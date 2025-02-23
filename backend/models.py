from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from database import Base
from datetime import datetime

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    domain = Column(String)
    
    contacts = relationship("Contact", back_populates="organization")
    emails = relationship("Email", back_populates="organization")

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="contacts")
    emails_sent = relationship("Email", foreign_keys="Email.sender_id", back_populates="sender")
    emails_received = relationship("Email", secondary="email_recipients", back_populates="recipients")

class Mailbox(Base):
    __tablename__ = "mailboxes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # Name of the uploaded file
    type = Column(String)  # 'pst' or 'mbox'
    last_processed = Column(DateTime, nullable=True)
    total_messages = Column(Integer, default=0)
    processed_messages = Column(Integer, default=0)
    
    emails = relationship("Email", back_populates="mailbox")

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String)
    sender_id = Column(Integer, ForeignKey("contacts.id"))
    received_date = Column(DateTime)
    body = Column(Text)
    importance = Column(String)
    processed = Column(Boolean, default=False)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    mailbox = relationship("Mailbox", back_populates="emails")
    organization = relationship("Organization", back_populates="emails")
    sender = relationship("Contact", foreign_keys=[sender_id], back_populates="emails_sent")
    recipients = relationship("Contact", secondary="email_recipients", back_populates="emails_received")
    attachments = relationship("Attachment", back_populates="email")

class EmailRecipient(Base):
    __tablename__ = "email_recipients"
    
    email_id = Column(Integer, ForeignKey("emails.id"), primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), primary_key=True)
    recipient_type = Column(String)  # 'to', 'cc', or 'bcc'

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    storage_path = Column(String)
    processed = Column(Boolean, default=False)
    extracted_text = Column(Text, nullable=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    
    email = relationship("Email", back_populates="attachments")
