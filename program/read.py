from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from email.mime.text import MIMEText
import base64

import kivy
import kivymd
from kivy.lang import Builder
from kivymd.uix.label import Label
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.list import MDList, TwoLineListItem
from kivy.uix.scrollview import ScrollView


# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def create_message(sender, to, subject, message_text):
    '''Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    '''
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
#  return {'raw': base64.urlsafe_b64encode(message.as_string())}
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


# -------------------------------------


def send_message(service, user_id, message):
    '''Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value 'me'
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    '''
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message

    except Exception as error:
        print('An error occurred: %s' % error)


# ----------------------------------------------


def main():
    '''Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    '''
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
#    results = service.users().labels().list(userId='me').execute()
#    labels = results.get('labels', [])

    # Sökoperatorer: https://support.google.com/mail/answer/7190
    inbox_messages = service.users().messages().list(userId='me', q='in:inbox').execute()
    inbox_ids = inbox_messages['messages']

    sent_messages = service.users().messages().list(userId='me', q='in:sent').execute()
    sent_ids = sent_messages['messages']

    draft_messages = service.users().messages().list(userId='me', q='in:drafts').execute()
    draft_messages = draft_messages['messages']


    # Rutnät
    class KivyGridLayout(GridLayout, MDApp):
        def __init__(self, **kwargs):
            # Rutnät konstruktor
            super(KivyGridLayout, self).__init__(**kwargs)

            # Antal kolumner
            self.cols = 1
            self.add_widget(Label(text='tja', size_hint=(0, .10), color='red'))

            self.main_grid = GridLayout()
            self.main_grid.cols = 2
            self.add_widget(self.main_grid)

            self.left_grid = GridLayout()
            self.left_grid.cols = 1
            self.left_grid.size_hint = (.15, 0)

            # Widgets
            self.left_grid.add_widget(MDRaisedButton(text='Inkorg', size_hint=(.4, .6)))
            self.left_grid.add_widget(MDRaisedButton(text='Skickat', size_hint=(.4, .6)))
            self.left_grid.add_widget(MDRaisedButton(text='Utkast', size_hint=(.4, .6)))
            self.left_grid.add_widget(MDRaisedButton(text='Skräppost', size_hint=(.4, .6)))
            self.left_grid.add_widget(MDRaisedButton(text='Papperskorgen', size_hint=(.4, .6)))

            self.main_grid.add_widget(self.left_grid)


            self.right_grid = GridLayout()
            self.right_grid.cols = 1

            self.scroll_view = ScrollView()
            self.list_view = MDList()
            self.scroll_view.add_widget(self.list_view)
            self.right_grid.add_widget(self.scroll_view)

            for id in inbox_ids[:20]:
                message = service.users().messages().get(userId='me', id = id['id']).execute()
                for header in message['payload']['headers']:
                    if header['value'].startswith('from'):
                        value2 = header['value'].split('(')
                    if header['name']=='Subject':
                        self.list_view.add_widget(TwoLineListItem(text=header['value'], secondary_text=value2[0]))

            self.main_grid.add_widget(self.right_grid)

    # Applikation
    class KivyApp(MDApp): 
        def build(self):
            return KivyGridLayout()
            
    KivyApp().run()


if __name__ == '__main__':
    main()
