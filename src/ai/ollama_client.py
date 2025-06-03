# Import required libraries for AI model interaction
import requests
from typing import Dict, Any, List
import json
from ollama import Client

class OllamaClient:
    """
    Client for interacting with Ollama AI models.
    Handles email categorization, reply generation, and digest creation.
    """
    def __init__(self, host: str = "http://localhost:11434", model: str = "deepseek-r1:7b"):
        """
        Initialize Ollama client with server host and model name.
        
        Args:
            host: Ollama server address
            model: Name of the AI model to use
        """
        self.host = host
        self.model = model
        self.client = Client(host=host)
        
    def categorize_email(self, subject: str, body: str, sender: str = "") -> dict:
        """
        Categorize email into Urgent/Important/Low Priority, with confidence and rationale.
        
        Args:
            subject: Email subject line
            body: Email body text
            sender: Email sender address
            
        Returns:
            Dictionary containing category, confidence score, and rationale
        """
        # Construct prompt for email categorization
        prompt = f"""You are an expert email assistant. Analyze the following email and:
1. Categorize it as one of: URGENT, IMPORTANT, or LOW_PRIORITY.
2. Give a confidence score (0-100) for your choice.
3. Briefly explain your reasoning.

Criteria:
- URGENT: Requires immediate action, has severe consequences if delayed, or uses urgent language.
- IMPORTANT: Needs action but not immediately, or is from a key stakeholder, but not an emergency.
- LOW_PRIORITY: Can be handled later, is informational, or not time-sensitive.

Email Subject: {subject}
Email Body: {body}
Sender: {sender}

Respond in this format:
Category: <category>
Confidence: <number>
Rationale: <short explanation>"""

        # Get AI response
        response = self._generate(prompt)
        
        # Parse the response using regex
        import re
        category_match = re.search(r'Category:\s*(URGENT|IMPORTANT|LOW_PRIORITY)', response, re.IGNORECASE)
        confidence_match = re.search(r'Confidence:\s*(\d+)', response)
        rationale_match = re.search(r'Rationale:\s*(.*)', response)

        # Extract and validate results
        category = category_match.group(1).upper() if category_match else "LOW_PRIORITY"
        confidence = int(confidence_match.group(1)) if confidence_match else 0
        rationale = rationale_match.group(1).strip() if rationale_match else ""

        return {
            "category": category,
            "confidence": confidence,
            "rationale": rationale
        }
    
    def generate_reply(self, email_subject: str, email_body: str, category: str) -> str:
        """
        Generate a draft reply for the email.
        
        Args:
            email_subject: Original email subject
            email_body: Original email body
            category: Email category (URGENT/IMPORTANT/LOW_PRIORITY)
            
        Returns:
            Generated email reply text
        """
        # Construct prompt for reply generation
        prompt = f"""Generate a professional email reply for:
        Subject: {email_subject}
        Category: {category}
        
        Format the response as a clean email with:
        - Subject line
        - Professional greeting
        - Clear body
        - Professional signature
        
        Do not include any thinking process or <think> tags.
        """
        
        return self._generate(prompt)
    
    def generate_digest(self, email_stats: Dict[str, Any]) -> str:
        """
        Generate a daily email digest.
        
        Args:
            email_stats: Dictionary containing email statistics
            
        Returns:
            Formatted digest text
        """
        # Construct prompt for digest generation
        prompt = f"""Generate a daily email digest report based on these statistics:
        {json.dumps(email_stats, indent=2)}
        
        Include:
        - Summary of emails received
        - Categorization breakdown
        - Key action items
        - Reply status
        
        Format as a clear, concise report:
        """
        
        return self._generate(prompt)
    
    def generate_draft_email(self, subject: str, message: str, category: str) -> str:
        """
        Generate a professional email draft based on subject, message, and category.
        
        Args:
            subject: Email subject
            message: Email message content
            category: Email category
            
        Returns:
            Generated email draft text
        """
        # Construct prompt for draft generation
        prompt = f"""Write ONLY the email draft, no explanations or reasoning:

Subject: {subject}
Message: {message}
Category: {category}

Output format:
Dear [recipient's name],

[body]

Best regards,
[your name]"""
        
        return self._generate(prompt)
    
    def _generate(self, prompt: str) -> str:
        """
        Make API call to Ollama using the Python client.
        
        Args:
            prompt: Text prompt for the AI model
            
        Returns:
            Generated response text
        """
        try:
            # Call Ollama API
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            # Clean the output by removing the input prompt if present
            if prompt in response['response']:
                return response['response'].split(prompt)[-1].strip()
            else:
                return response['response'].strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "" 