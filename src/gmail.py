import os.path
import base64
import json
import re
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging
import requests
from util import Util

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']

class Gmail:
    def __init__(self):
        self.creds = None
        self.conf_dir = Util.get_conf_dir()
        self.logger = Util.get_logger()
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.conf_dir + 'gmail_token.json'):
            self.logger.info("Trying to reuse saved gmail token. ({}).".format(self.conf_dir + 'gmail_token.json'))
            self.creds = Credentials.from_authorized_user_file(self.conf_dir + 'gmail_token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            self.logger.info("Gmail creds not found or not valid.")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.logger.info("Trying to refresh gmail creds.")
                self.creds.refresh(Request())
            else:
                self.logger.info("Starting gmail login flow.")
                flow = InstalledAppFlow.from_client_secrets_file(               
                    # your self.creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                    self.conf_dir + 'gmail_adc.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.conf_dir + 'gmail_token.json', 'w') as token:
                token.write(self.creds.to_json())

    @staticmethod
    def has_api_token():
        conf_dir = Util.get_conf_dir()
        return os.path.exists(conf_dir + '/gmail_adc.json')


    def get_garmin_code(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        code = None
        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=self.creds)
            while code is None:
                results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread from:alerts@account.garmin.com").execute()
                messages = results.get('messages',[]);
                if not messages:
                    self.logger.info('No new messages. Trying again in 5 seconds.')
                    time.sleep(5)
                    continue
                else:
                    message_count = 0
                    for message in messages:
                        msg = service.users().messages().get(userId='me', id=message['id']).execute()
                        data = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode("utf-8")
                        match = re.search(r'<strong[^>]*>(\d{6})</strong>', data)
                        if match:
                            code = match.group(1)
                            self.logger.info("Extracted Garmin code: " + code)

                        # mark the message as read
                        msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()                                                       
        except Exception as error:
            self.logger.info(f'An error occurred: {error}')
        return code
