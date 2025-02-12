from typing import Dict, Optional, List
import msal
from config import settings
import secrets
import hashlib
import base64

class AuthService:
    # Define required scopes as a list to avoid frozenset issues
    SCOPES: List[str] = [
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/Mail.Read',
        'offline_access',
        'openid',
        'profile'
    ]
    
    # Define redirect URI
    REDIRECT_URI = "http://localhost:3000/auth/callback"

    def __init__(self):
        """Initialize the auth service with MSAL client"""
        try:
            # Use PublicClientApplication instead of ConfidentialClientApplication for PKCE
            self.client = msal.PublicClientApplication(
                client_id=settings.MS_CLIENT_ID,
                authority=f"https://login.microsoftonline.com/{settings.MS_TENANT_ID}"
            )
            print(f"AuthService initialized with tenant {settings.MS_TENANT_ID}")
        except Exception as e:
            print(f"Error initializing AuthService: {str(e)}")
            raise

    def _generate_code_verifier(self) -> str:
        """Generate a code verifier for PKCE"""
        # Generate a code verifier that meets PKCE requirements
        # - minimum length of 43 characters
        # - maximum length of 128 characters
        # - contains only alphanumeric characters plus '-', '.', '_', '~'
        code_verifier = secrets.token_urlsafe(96)  # generates 128 characters
        return code_verifier

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate a code challenge for PKCE"""
        # Generate a code challenge according to PKCE spec
        # 1. Take the code verifier
        # 2. Hash it with SHA256
        # 3. Base64URL encode it
        # 4. Remove padding ('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('ascii')).digest()
        ).decode('ascii').rstrip('=')
        return code_challenge

    def get_auth_url(self) -> Dict[str, str]:
        """Generate Microsoft OAuth authorization URL with PKCE"""
        try:
            # Generate PKCE code verifier and challenge
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)

            # Generate state for CSRF protection
            state = secrets.token_urlsafe(32)

            auth_url = self.client.get_authorization_request_url(
                scopes=self.SCOPES,
                redirect_uri=self.REDIRECT_URI,
                state=state,
                code_challenge=code_challenge,
                code_challenge_method="S256"
            )
            print(f"Generated auth URL with scopes: {self.SCOPES}")
            print(f"Code verifier length: {len(code_verifier)}")
            print(f"Code challenge length: {len(code_challenge)}")
            return {
                "auth_url": auth_url,
                "code_verifier": code_verifier,
                "state": state
            }
        except Exception as e:
            print(f"Error generating auth URL: {str(e)}")
            raise

    def get_token(self, auth_code: str, code_verifier: str) -> Optional[Dict[str, str]]:
        """Exchange authorization code for access token using PKCE"""
        try:
            print(f"Attempting to get token with code length: {len(auth_code)}")
            print(f"Code verifier length: {len(code_verifier)}")
            
            result = self.client.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=self.SCOPES,
                redirect_uri=self.REDIRECT_URI,
                code_verifier=code_verifier
            )
            
            if "error" in result:
                error_msg = f"Error getting token: {result.get('error')} - {result.get('error_description')}"
                print(error_msg)
                return None

            print("Successfully acquired token")
            return {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in")
            }
        except Exception as e:
            print(f"Exception getting token: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh an expired access token"""
        try:
            print("Attempting to refresh token")
            result = self.client.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=self.SCOPES
            )
            
            if "error" in result:
                error_msg = f"Error refreshing token: {result.get('error')} - {result.get('error_description')}"
                print(error_msg)
                return None

            print("Successfully refreshed token")
            return {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in")
            }
        except Exception as e:
            print(f"Exception refreshing token: {str(e)}")
            raise
