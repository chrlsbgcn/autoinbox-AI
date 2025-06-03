# Import required libraries for Gmail API integration and email handling
import os
import pickle
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailClient:
    # Define required OAuth2 scopes for Gmail API access
    # readonly: Read email messages and settings
    # send: Send email messages
    # compose: Create and modify email drafts
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.compose']
    
    def __init__(self, credentials_path: str, token_path: str, user_email: str):
        """
        Initialize Gmail client with OAuth2 credentials and user email.
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
            user_email: Gmail account to use
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.user_email = user_email
        self.service = None
        
    def authenticate(self) -> None:
        """
        Authenticate with Gmail API using OAuth2.
        Handles token refresh and storage.
        """
        creds = None
        
        # Try to load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
                
        # If no valid token exists, get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Get new token through OAuth2 flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save token for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
                
        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)
        
    def fetch_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent emails from Gmail.
        
        Args:
            limit: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries containing id, subject, sender, date, and body
        """
        if not self.service:
            self.authenticate()
            
        # Get list of recent messages
        results = self.service.users().messages().list(
            userId='me', maxResults=limit).execute()
        messages = results.get('messages', [])
        
        emails = []
        for message in messages:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            # Extract email headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
            date = next((h['value'] for h in headers if h['name'] == 'Date'), "(No Date)")
            
            # Get email body based on message structure
            if 'parts' in msg['payload']:
                body = self._get_body_from_parts(msg['payload']['parts'])
            else:
                body = self._get_body_from_payload(msg['payload'])
                
            emails.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            })
            
        return emails
    
    def _get_body_from_parts(self, parts: List[Dict]) -> str:
        """
        Extract body from email parts (for multipart messages).
        
        Args:
            parts: List of email parts
            
        Returns:
            Concatenated plain text body
        """
        body = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body += part['body'].get('data', '')
        return body
    
    def _get_body_from_payload(self, payload: Dict) -> str:
        """
        Extract body from single-part email payload.
        
        Args:
            payload: Email payload dictionary
            
        Returns:
            Email body text
        """
        return payload['body'].get('data', '')

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Send an email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            
        Returns:
            Dictionary containing message ID and status
        """
        if not self.service:
            self.authenticate()

        # Create email message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        msg = MIMEText(body)
        message.attach(msg)

        # Encode message for Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        try:
            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'id': sent_message['id'],
                'threadId': sent_message['threadId'],
                'status': 'sent'
            }
        except Exception as e:
            print(f"Error sending email: {e}")
            return {'status': 'error', 'error': str(e)}

    def create_draft(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Create a draft email in Gmail.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            
        Returns:
            Dictionary containing draft ID and status
        """
        if not self.service:
            self.authenticate()

        # Create draft message
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = self.user_email  # Set the from address
        message['subject'] = subject

        msg = MIMEText(body)
        message.attach(msg)

        # Encode message for Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        try:
            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',  # This will use the authenticated user (nexvoiceph@gmail.com)
                body={'message': {'raw': raw_message}}
            ).execute()
            
            return {
                'id': draft['id'],
                'message_id': draft['message']['id'],
                'status': 'draft_created',
                'email': self.user_email
            }
        except Exception as e:
            print(f"Error creating draft: {e}")
            return {'status': 'error', 'error': str(e)} 