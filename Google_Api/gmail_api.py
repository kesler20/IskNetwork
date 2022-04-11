API_kEYS = 'AIzaSyCOtUVXjkThgCrsmJUTBN0JoTfUDRF-7uw'
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = r'Google_Api\client_secret_971955567226-7b8bhee7fa4krl3qqetea54d0ojdjblt.apps.googleusercontent.com.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']


def Create_Service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(pickle_file)
        return None


service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def send_code_to_recipient(recipient, service=service):
    
    emailMsg = ''
    code = [randint(0,9) for i in range(5)]
    for rand_num in code:
        emailMsg += str(rand_num)
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = str(recipient)
    print(f'emai lsent to {recipient}')
    mimeMessage['subject'] = 'Password recovery code'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    print(message)
    return code
