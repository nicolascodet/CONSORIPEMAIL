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
    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="contacts")

class Mailbox(Base):
    __tablename__ = "mailboxes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    last_sync = Column(DateTime, nullable=True)
    
    emails = relationship("Email", back_populates="mailbox")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    emails = relationship("Email", back_populates="user")

class Email(Base):
    __tablename__ = "emails_raw"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String)
    sender = Column(String)
    recipients = Column(JSON)  # List of email addresses
    received_datetime = Column(DateTime)
    body_text = Column(Text)
    body_html = Column(Text, nullable=True)
    internet_message_id = Column(String, index=True)
    conversation_id = Column(String, index=True)
    has_attachments = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    excluded = Column(Boolean, default=False)
    
    # Foreign Keys
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    mailbox = relationship("Mailbox", back_populates="emails")
    organization = relationship("Organization", back_populates="emails")
    user = relationship("User", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email")

class Attachment(Base):
    __tablename__ = "attachments_raw"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content_type = Column(String)
    size = Column(Integer)
    storage_path = Column(String)  # Path in local storage/GCS
    text_extracted = Column(Boolean, default=False)
    text_content = Column(Text, nullable=True)
    
    # Foreign Key
    email_id = Column(Integer, ForeignKey("emails_raw.id"))
    
    # Relationship
    email = relationship("Email", back_populates="attachments")
