from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle

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

def download_attachments(service, start_date, end_date, download_folder="attachments"):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        
    query = f'after:{start_date} before:{end_date} has:attachment'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    filename = part['filename']
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        att = service.users().messages().attachments().get(
                            userId='me', messageId=message['id'], id=att_id
                        ).execute()
                        data = att['data']
                    
                    file_data = base64.urlsafe_b64decode(data)
                    filepath = os.path.join(download_folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_data)
                    print(f"Downloaded: {filename}")

def main():
    service = authenticate()
    start_date = "2024/10/01"  # Format: YYYY/MM/DD
    end_date = "2024/10/31"    # Format: YYYY/MM/DD
    download_attachments(service, start_date, end_date)

if __name__ == '__main__':
    main()
