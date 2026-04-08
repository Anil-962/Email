import os
import logging
import base64
from email.message import EmailMessage

logger = logging.getLogger("api_gateway.gmail")

# Scopes mapped to access. Sending emails requires escalated privileges.
# WARNING: If token.json exists, it must be deleted to trigger re-auth for new scopes.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def _import_google_clients():
    """
    Import Gmail SDK modules on demand.
    This keeps app startup functional even if Gmail extras are not installed.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        return Request, Credentials, InstalledAppFlow, build
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing Gmail dependencies. Install with: "
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        ) from exc

def get_gmail_service():
    """
    Handles the stateless token management setup using Env Vars mapping and
    returns the constructed Google API client service.
    """
    Request, Credentials, InstalledAppFlow, build = _import_google_clients()
    creds = None
    
    # Secure paths handled via environment mappings
    token_file = os.environ.get("GMAIL_TOKEN_FILE", "token.json")
    credentials_file = os.environ.get("GMAIL_CREDENTIALS_FILE", "credentials.json")

    # Load existing authorized user configs
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
    # If there are no (valid) credentials available, let the user manually log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                logger.error(f"Missing OAuth2 file: {credentials_file}")
                raise ValueError(
                    f"OAuth2 Credentials file '{credentials_file}' not found. "
                    "Ensure you mapped the Google Cloud Console credentials securely."
                )
            
            # Spin up the desktop flow securely
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Cache token for subsequent API calls
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def fetch_latest_emails(max_results=10):
    """
    Securely fetches and parses the latest emails traversing the Gmail REST API.
    """
    logger.info(f"Connecting to Gmail API securely. Pulling {max_results} messages.")
    try:
        service = get_gmail_service()
        
        # Pull metadata overview (IDs and thread mappings)
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        email_data = []
        if not messages:
            return email_data
            
        # Hydrate individual email records via explicit GET routines
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            
            headers = msg_detail.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
            snippet = msg_detail.get('snippet', '')
            
            email_data.append({
                "id": msg['id'],
                "sender": sender,
                "subject": subject,
                "snippet": snippet
            })
            
        return email_data
        
    except Exception as e:
        logger.error(f"Critical Gmail Parsing Failure: {e}")
        raise

def send_email(recipient: str, subject: str, message_text: str):
    """
    Constructs a clean MIME email and dispatches it securely via the Gmail REST API.
    """
    logger.info(f"Connecting to Gmail API to dispatch email to {recipient}")
    try:
        service = get_gmail_service()
        
        message = EmailMessage()
        message.set_content(message_text)
        message['To'] = recipient
        message['Subject'] = subject
        
        # Gmail API requires URL-safe base64 encoding
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        payload = {
            'raw': encoded_message
        }
        
        # Dispatch the payload
        sent_message = service.users().messages().send(userId="me", body=payload).execute()
        logger.info(f"Email successfully dispatched to {recipient}. Message ID: {sent_message['id']}")
        return sent_message
        
    except Exception as e:
        logger.error(f"Critical Gmail Sending Failure: {e}")
        raise
