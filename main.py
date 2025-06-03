# Import required libraries
import os
from dotenv import load_dotenv
from src.email.gmail_client import GmailClient
from src.email.email_processor import EmailProcessor
from src.ai.ollama_client import OllamaClient

def main():
    # Load environment variables from config/.env file
    # This includes API keys, configuration settings, and other sensitive data
    load_dotenv('config/.env')
    
    # Initialize Gmail client with OAuth2 credentials
    # This handles authentication and communication with Gmail API
    gmail_client = GmailClient(
        credentials_path='config/credentials.json',  # OAuth2 credentials file
        token_path='config/token.json',             # OAuth2 token storage
        user_email=os.getenv('GMAIL_USER_EMAIL')    # Target Gmail account from environment
    )
    
    # Initialize Ollama client for AI model integration
    # This connects to the local Ollama server for AI processing
    ollama_client = OllamaClient(
        host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),  # Ollama server address
        model=os.getenv('OLLAMA_MODEL', 'deepseek-r1:7b')        # AI model to use
    )
    
    # Initialize email processor
    # This is the main component that handles email processing and AI integration
    email_processor = EmailProcessor(
        gmail_client=gmail_client,                              # Gmail client instance
        ollama_client=ollama_client,                           # AI client instance
        emails_path=os.getenv('EMAILS_STORAGE_PATH', 'data/emails'),  # Where to store processed emails
        drafts_path=os.getenv('DRAFTS_STORAGE_PATH', 'data/drafts')   # Where to store email drafts
    )
    
    try:
        # Main program loop
        while True:
            # Get user command
            command = input("\nEnter command (type 'process' to process emails, 'help' for options, 'exit' to quit): ").strip().lower()
            
            if command == 'exit':
                print("Exiting...")
                break
            elif command == 'help':
                # Display available commands
                print("\nAvailable commands:")
                print("  help  - Show this help message")
                print("  exit  - Exit the program")
                print("  process - Process new emails")
                print("  stats - Show current email statistics")
            elif command == 'process':
                # Process new emails
                print("Processing emails...")
                print(f"Drafts will be created in {os.getenv('GMAIL_USER_EMAIL')}")
                # Process emails with specified limit from environment variable
                stats = email_processor.process_emails(
                    limit=int(os.getenv('EMAIL_FETCH_LIMIT', '50'))
                )
                # Display processing results
                print(f"Processed {stats['total_emails']} emails")
                print(f"Categories: {stats['categories']}")
            elif command == 'stats':
                # Display current email statistics
                stats = email_processor.get_daily_stats()
                print("\nCurrent Email Statistics:")
                print(f"Total Emails: {stats['total_emails']}")
                print("Categories:", stats['categories'])
            else:
                print("Unknown command. Type 'help' for available options.")
    
    except KeyboardInterrupt:
        # Handle graceful exit on Ctrl+C
        print("\nExiting...")

# Entry point of the program
if __name__ == "__main__":
    main() 