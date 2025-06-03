# Import required libraries for email processing and data handling
import os
import json
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
from ..ai.ollama_client import OllamaClient
from .gmail_client import GmailClient
import re

class EmailProcessor:
    """
    Main class for processing emails using AI and managing email drafts.
    Handles email categorization, reply generation, and statistics tracking.
    """
    def __init__(self, 
                 gmail_client: GmailClient,
                 ollama_client: OllamaClient,
                 emails_path: str,
                 drafts_path: str):
        """
        Initialize the email processor with required clients and storage paths.
        
        Args:
            gmail_client: Gmail API client for email operations
            ollama_client: AI client for email processing
            emails_path: Directory to store processed email data
            drafts_path: Directory to store email drafts
        """
        self.gmail_client = gmail_client
        self.ollama_client = ollama_client
        self.emails_path = emails_path
        self.drafts_path = drafts_path
        
        # Create storage directories if they don't exist
        os.makedirs(emails_path, exist_ok=True)
        os.makedirs(drafts_path, exist_ok=True)
        
    def process_emails(self, limit: int = 50) -> Dict[str, Any]:
        """
        Process recent emails and generate statistics.
        
        Args:
            limit: Maximum number of emails to process
            
        Returns:
            Dictionary containing processing statistics
        """
        # Fetch recent emails from Gmail
        emails = self.gmail_client.fetch_emails(limit)
        
        # Initialize tracking variables
        processed_emails = []
        categories = {"URGENT": 0, "IMPORTANT": 0, "LOW_PRIORITY": 0}
        
        for email in emails:
            # Use AI to categorize the email
            cat_result = self.ollama_client.categorize_email(
                email['subject'], email['body'], email.get('sender', "")
            )
            category = cat_result["category"]
            confidence = cat_result.get("confidence", 0)
            rationale = cat_result.get("rationale", "")
            categories[category] += 1
            
            # Generate AI-powered draft reply
            draft_reply = self.ollama_client.generate_reply(
                email['subject'], email['body'], category)
            
            # Clean the draft reply to remove AI artifacts
            cleaned_reply = self.clean_email_body(draft_reply)
            
            # Create draft in Gmail
            draft_result = self.gmail_client.create_draft(
                to=email['sender'],
                subject=f"Re: {email['subject']}",
                body=cleaned_reply
            )
            
            # Store processed email data
            processed_email = {
                **email,
                'category': category,
                'confidence': confidence,
                'rationale': rationale,
                'draft_reply': cleaned_reply,
                'draft_id': draft_result.get('id'),
                'processed_at': datetime.now().isoformat()
            }
            processed_emails.append(processed_email)
            
            # Save processed data to files
            self._save_email(processed_email)
            self._save_draft(processed_email)
            
            # Log processing results
            print(f"Created draft for email: {email['subject']}")
            if draft_result['status'] == 'draft_created':
                print(f"Draft ID: {draft_result['id']}")
            else:
                print(f"Error creating draft: {draft_result.get('error')}")
        
        # Generate and return processing statistics
        stats = {
            'total_emails': len(processed_emails),
            'categories': categories,
            'processed_at': datetime.now().isoformat()
        }
        
        return stats
    
    def _save_email(self, email: Dict[str, Any]) -> None:
        """
        Save processed email data to CSV file.
        
        Args:
            email: Dictionary containing email data
        """
        df = pd.DataFrame([email])
        file_path = os.path.join(self.emails_path, 'emails.csv')
        
        # Append to existing file or create new one
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, index=False)
    
    def _save_draft(self, email: Dict[str, Any]) -> None:
        """
        Save draft reply to JSON file.
        
        Args:
            email: Dictionary containing email and draft data
        """
        draft = {
            'email_id': email['id'],
            'subject': email['subject'],
            'draft_reply': email['draft_reply'],
            'category': email['category'],
            'confidence': email.get('confidence', 0),
            'rationale': email.get('rationale', ''),
            'created_at': email['processed_at']
        }
        
        file_path = os.path.join(self.drafts_path, f"draft_{email['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(draft, f, indent=2)

    def clean_email_body(self, text: str) -> str:
        """
        Clean the email body by removing AI artifacts and formatting.
        
        Args:
            text: Raw email body text
            
        Returns:
            Cleaned email body text
        """
        # Remove content between <think> tags
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Remove lines starting with common AI prefixes
        text = re.sub(r'^(Let me|I\'ll|I will|Here\'s|Here is).*$', '', text, flags=re.MULTILINE)
        # Remove lines containing thinking process indicators
        text = re.sub(r'.*thinking process.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'.*thought process.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # Remove metadata lines
        text = re.sub(r'^\*\*Subject:\*\*.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\*\*Category:\*\*.*$', '', text, flags=re.MULTILINE)
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        return text

    def send_drafted_email(self, draft_id: str, recipient: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Send a drafted email to the specified recipient.
        
        Args:
            draft_id: The ID of the draft to send
            recipient: The email address of the recipient
            confirm: Must be True to actually send the email. If False, returns preview only.
            
        Returns:
            Dictionary containing send status and result
        """
        # Load the draft from storage
        draft_path = os.path.join(self.drafts_path, f"draft_{draft_id}.json")
        if not os.path.exists(draft_path):
            return {'status': 'error', 'error': 'Draft not found'}

        with open(draft_path, 'r') as f:
            draft = json.load(f)

        # Clean the email body
        cleaned_body = self.clean_email_body(draft['draft_reply'])

        # Return preview if not confirmed
        if not confirm:
            return {
                'status': 'preview',
                'preview': {
                    'to': recipient,
                    'subject': draft['subject'],
                    'body': cleaned_body
                }
            }

        # Send the email if confirmed
        result = self.gmail_client.send_email(
            to=recipient,
            subject=draft['subject'],
            body=cleaned_body
        )

        # Move draft to sent folder if successful
        if result['status'] == 'sent':
            sent_path = os.path.join(self.drafts_path, 'sent', f"sent_{draft_id}.json")
            os.makedirs(os.path.dirname(sent_path), exist_ok=True)
            os.rename(draft_path, sent_path)

        return result
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """
        Get statistics for daily email digest.
        
        Returns:
            Dictionary containing email statistics
        """
        emails_file = os.path.join(self.emails_path, 'emails.csv')
        if not os.path.exists(emails_file):
            return {
                'total_emails': 0,
                'categories': {"URGENT": 0, "IMPORTANT": 0, "LOW_PRIORITY": 0},
                'processed_at': datetime.now().isoformat()
            }
        
        # Read and process email statistics
        df = pd.read_csv(emails_file)
        categories = df['category'].value_counts().to_dict()
        
        return {
            'total_emails': len(df),
            'categories': categories,
            'processed_at': datetime.now().isoformat()
        } 