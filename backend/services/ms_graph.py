import os
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

class MSGraphService:
    BASE_URL = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
    
    def _get_headers(self, access_token: Optional[str] = None) -> Dict[str, str]:
        """Get headers for Microsoft Graph API requests"""
        token = access_token or self.access_token
        if not token:
            raise ValueError("Access token is required")
            
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_user_info(self, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Get current user's information"""
        headers = self._get_headers(access_token)
        url = f"{self.BASE_URL}/me"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {
            "email": data.get("userPrincipalName", ""),
            "name": data.get("displayName", ""),
            "id": data.get("id", "")
        }
    
    def get_messages(self, folder: str = "inbox", top: int = 50, skip: int = 0, access_token: Optional[str] = None) -> List[Dict[Any, Any]]:
        """Fetch messages from specified folder"""
        headers = self._get_headers(access_token)
        url = f"{self.BASE_URL}/me/mailFolders/{folder}/messages"
        params = {
            "$top": top,
            "$skip": skip,
            "$select": "subject,from,toRecipients,receivedDateTime,bodyPreview,internetMessageId,conversationId,hasAttachments,body",
            "$orderby": "receivedDateTime desc"
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("value", [])
    
    def get_attachment(self, message_id: str, attachment_id: str, access_token: Optional[str] = None) -> Dict[Any, Any]:
        """Download a specific attachment"""
        headers = self._get_headers(access_token)
        url = f"{self.BASE_URL}/me/messages/{message_id}/attachments/{attachment_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_message_attachments(self, message_id: str, access_token: Optional[str] = None) -> List[Dict[Any, Any]]:
        """Get list of attachments for a message"""
        headers = self._get_headers(access_token)
        url = f"{self.BASE_URL}/me/messages/{message_id}/attachments"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("value", [])
