"""
MercadoLibre OAuth 2.0 Authentication Manager

Handles the complete OAuth 2.0 flow for MercadoLibre API access:
- Authorization URL generation
- Temporary callback server
- Token exchange and refresh
- Automatic token management
"""

import os
import webbrowser
import urllib.parse
import json
import time
from typing import Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from loguru import logger

# Load environment variables
load_dotenv()


class TokenData(BaseModel):
    """Token data model for validation"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    scope: str
    created_at: float = Field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 5 minute buffer)"""
        return time.time() > (self.created_at + self.expires_in - 300)


class AuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    def do_GET(self):
        """Handle GET request from MercadoLibre OAuth redirect"""
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # Store the authorization code in server instance
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.server.auth_state = query_params.get('state', [None])[0]
            self.send_success_response()
        elif 'error' in query_params:
            self.server.auth_error = query_params['error'][0]
            self.send_error_response(query_params['error'][0])
        else:
            self.send_error_response("No authorization code received")
    
    def send_success_response(self):
        """Send success page to user"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html>
        <head><title>MercadoLibre Auth Success</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #3483fa;">🎉 Authentication Successful!</h1>
            <p>You have successfully authorized the MercadoLibre API access.</p>
            <p>You can close this window and return to your application.</p>
            <script>setTimeout(() => window.close(), 3000);</script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def send_error_response(self, error: str):
        """Send error page to user"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <html>
        <head><title>MercadoLibre Auth Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #ff6b6b;">❌ Authentication Error</h1>
            <p>Error: {error}</p>
            <p>Please try again or check your application configuration.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress default server logging"""
        pass


class MercadoLibreAuth:
    """
    MercadoLibre OAuth 2.0 Authentication Manager
    
    Handles complete authentication flow including:
    - Authorization URL generation
    - Token exchange
    - Token refresh
    - Token storage and retrieval
    """
    
    def __init__(self):
        # Load configuration from environment
        self.client_id = os.getenv('MERCADOLIBRE_CLIENT_ID')
        self.client_secret = os.getenv('MERCADOLIBRE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('MERCADOLIBRE_REDIRECT_URI', 'http://localhost:8080/auth/callback')
        self.oauth_state = os.getenv('OAUTH_STATE', 'ml_oauth_secure_state')
        self.scopes = os.getenv('OAUTH_SCOPES', 'offline_access,read').split(',')
        
        # API URLs (Corregidas para México)
        self.auth_url = os.getenv('ML_AUTH_URL', 'https://auth.mercadolibre.com.mx/authorization')
        self.token_url = os.getenv('ML_TOKEN_URL', 'https://api.mercadolibre.com/oauth/token')
        
        # Token storage
        self.token_file = Path('.env_tokens')
        self.current_token: Optional[TokenData] = None
        
        # Validate configuration
        self._validate_config()
        
        # Load existing token if available
        self._load_saved_token()
    
    def _validate_config(self) -> None:
        """Validate required configuration"""
        if not self.client_id:
            raise ValueError("MERCADOLIBRE_CLIENT_ID not found in environment variables")
        if not self.client_secret:
            raise ValueError("MERCADOLIBRE_CLIENT_SECRET not found in environment variables")
        
        logger.info(f"✅ OAuth configuration loaded: Client ID {self.client_id}")
    
    def _load_saved_token(self) -> None:
        """Load previously saved token if it exists"""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                self.current_token = TokenData(**token_data)
                logger.info("✅ Loaded existing token from storage")
            except Exception as e:
                logger.warning(f"Could not load saved token: {e}")
                self.current_token = None
    
    def _save_token(self, token_data: TokenData) -> None:
        """Save token to file"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data.model_dump(), f, indent=2)
            logger.info("✅ Token saved successfully")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    def get_authorization_url(self) -> str:
        """Generate authorization URL for MercadoLibre OAuth"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.oauth_state,
            'scope': ' '.join(self.scopes)
        }
        
        url = f"{self.auth_url}?" + urllib.parse.urlencode(params)
        logger.info(f"📋 Authorization URL generated: {url}")
        return url
    
    def start_callback_server(self, port: int = 8080) -> HTTPServer:
        """Start temporary HTTP server to receive OAuth callback"""
        server = HTTPServer(('localhost', port), AuthCallbackHandler)
        server.auth_code = None
        server.auth_error = None
        server.auth_state = None
        
        logger.info(f"🌐 Started callback server on http://localhost:{port}")
        return server
    
    def authenticate(self, timeout: int = 300) -> bool:
        """
        Perform complete OAuth authentication flow
        
        Args:
            timeout: Maximum time to wait for user authorization (seconds)
            
        Returns:
            bool: True if authentication successful
        """
        logger.info("🚀 Starting OAuth 2.0 authentication flow...")
        
        # Check if we have a valid token already
        if self.current_token and not self.current_token.is_expired:
            logger.info("✅ Valid token already exists, skipping authentication")
            return True
        
        # Start callback server
        server = self.start_callback_server()
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        try:
            # Open authorization URL in browser
            auth_url = self.get_authorization_url()
            logger.info("🌐 Opening authorization URL in browser...")
            webbrowser.open(auth_url)
            
            print("\n" + "="*60)
            print("🔐 MERCADOLIBRE OAUTH AUTHENTICATION")
            print("="*60)
            print("1. Your browser should open automatically")
            print("2. Log into your MercadoLibre account")
            print("3. Authorize the application")
            print("4. Wait for the confirmation message")
            print("="*60)
            print(f"⏰ Waiting up to {timeout} seconds for authorization...")
            
            # Wait for authorization code
            start_time = time.time()
            while time.time() - start_time < timeout:
                if server.auth_code:
                    logger.info("✅ Authorization code received!")
                    break
                elif server.auth_error:
                    logger.error(f"❌ Authorization error: {server.auth_error}")
                    return False
                time.sleep(1)
            else:
                logger.error("⏰ Timeout waiting for authorization")
                return False
            
            # Exchange code for token
            if self._exchange_code_for_token(server.auth_code):
                logger.info("🎉 Authentication completed successfully!")
                return True
            else:
                logger.error("❌ Failed to exchange code for token")
                return False
                
        finally:
            server.shutdown()
            logger.info("🛑 Callback server stopped")
    
    def exchange_code_for_token(self, auth_code: str) -> TokenData:
        """
        Exchange authorization code for access token (public method)
        
        Args:
            auth_code (str): Authorization code from OAuth callback
            
        Returns:
            TokenData: Token data object
        """
        if self._exchange_code_for_token(auth_code):
            return self.current_token
        else:
            raise Exception("Failed to exchange code for token")
    
    def _exchange_code_for_token(self, auth_code: str) -> bool:
        """Exchange authorization code for access token"""
        logger.info("🔄 Exchanging authorization code for access token...")
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.current_token = TokenData(**token_data)
            self._save_token(self.current_token)
            
            logger.info("✅ Access token obtained successfully!")
            return True
            
        except requests.RequestException as e:
            logger.error(f"❌ Token exchange failed: {e}")
            return False
    
    def refresh_token(self) -> bool:
        """Refresh the current access token"""
        if not self.current_token or not self.current_token.refresh_token:
            logger.error("❌ No refresh token available")
            return False
        
        logger.info("🔄 Refreshing access token...")
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.current_token.refresh_token
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            # Keep the same refresh token if not provided
            if 'refresh_token' not in token_data:
                token_data['refresh_token'] = self.current_token.refresh_token
            
            self.current_token = TokenData(**token_data)
            self._save_token(self.current_token)
            
            logger.info("✅ Token refreshed successfully!")
            return True
            
        except requests.RequestException as e:
            logger.error(f"❌ Token refresh failed: {e}")
            return False
    
    def get_valid_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary
        
        Returns:
            str: Valid access token or None if authentication fails
        """
        # No token at all - need to authenticate
        if not self.current_token:
            if self.authenticate():
                return self.current_token.access_token
            return None
        
        # Token expired - try to refresh
        if self.current_token.is_expired:
            if self.refresh_token():
                return self.current_token.access_token
            else:
                # Refresh failed - try full authentication
                if self.authenticate():
                    return self.current_token.access_token
                return None
        
        # Token is valid
        return self.current_token.access_token
    
    def is_authenticated(self) -> bool:
        """Check if we have a valid authentication"""
        return self.current_token is not None and not self.current_token.is_expired
    
    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        return self.current_token is not None and not self.current_token.is_expired
    
    @property
    def token_data(self) -> Optional[TokenData]:
        """Get current token data"""
        return self.current_token
    
    def logout(self) -> None:
        """Clear stored authentication"""
        self.current_token = None
        if self.token_file.exists():
            self.token_file.unlink()
        logger.info("✅ Logged out successfully")


def main():
    """Test the authentication flow"""
    print("🧪 Testing MercadoLibre OAuth Authentication...")
    
    auth = MercadoLibreAuth()
    
    if auth.authenticate():
        print("✅ Authentication successful!")
        print(f"📋 Token expires in: {auth.current_token.expires_in} seconds")
        print(f"🔑 Access token: {auth.current_token.access_token[:20]}...")
    else:
        print("❌ Authentication failed!")


if __name__ == "__main__":
    main() 