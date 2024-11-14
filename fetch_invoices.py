from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle
import io
from PyPDF2 import PdfReader
import tempfile

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_messages(service, start_date, end_date):
    """Fetch messages with attachments within the date range."""
    query = f'after:{start_date} before:{end_date} has:attachment'
    results = service.users().messages().list(userId='me', q=query).execute()
    return results.get('messages', [])

def get_attachment_data(service, message_id, part):
    """Extract attachment data from a message part."""
    if 'data' in part['body']:
        return part['body']['data']
    
    att_id = part['body']['attachmentId']
    att = service.users().messages().attachments().get(
        userId='me', messageId=message_id, id=att_id
    ).execute()
    return att['data']

def extract_pdf_text(file_data):
    """Extract text content from a PDF file."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(base64.urlsafe_b64decode(file_data))
        temp_path = temp_file.name
    
    try:
        return read_pdf_content(temp_path)
    finally:
        os.unlink(temp_path)

def read_pdf_content(pdf_path):
    """Read and extract text from a PDF file at the given path."""
    try:
        pdf = PdfReader(pdf_path)
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text().lower()
        return pdf_text
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return ""

def contains_search_strings(text, search_strings):
    """Check if any search string is present in the text."""
    return any(search_string.lower() in text for search_string in search_strings)

def save_attachment(file_data, filename, download_folder):
    """Save the attachment to the specified folder."""
    filepath = os.path.join(download_folder, filename)
    with open(filepath, 'wb') as f:
        f.write(base64.urlsafe_b64decode(file_data))
    print(f"Downloaded: {filename}")

def download_attachments(service, start_date, end_date, search_strings=[], download_folder="attachments"):
    """Main function to download PDF attachments containing specified strings."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    messages = get_messages(service, start_date, end_date)
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        
        if 'parts' not in payload:
            continue
            
        for part in payload['parts']:
            if not (part.get('filename') and part['filename'].lower().endswith('.pdf')):
                continue
                
            try:
                # Get attachment data
                data = get_attachment_data(service, message['id'], part)
                
                # Extract and check PDF content
                pdf_text = extract_pdf_text(data)
                if contains_search_strings(pdf_text, search_strings):
                    save_attachment(data, part['filename'], download_folder)
                    
            except Exception as e:
                print(f"Error processing {part.get('filename', 'unknown file')}: {str(e)}")

def main():
    service = authenticate()
    start_date = "2024/10/01"
    end_date = "2024/10/31"
    search_strings = ["9512302884", "IAPP"] 
    download_attachments(service, start_date, end_date, search_strings)

if __name__ == '__main__':
    main()
