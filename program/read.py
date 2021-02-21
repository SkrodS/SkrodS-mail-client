from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
import html
import kivy
import kivymd
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.label import MDLabel
from kivy.uix.textinput import TextInput
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.button import MDRaisedButton, MDRoundFlatButton, MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.floatlayout import FloatLayout
from kivymd.app import MDApp
from kivymd.uix.list import MDList, TwoLineListItem
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
import weakref
from functools import partial


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


    # Laddar in mail. OBS, det är inte denna metod som tar lång tid vid uppstart och inläsning av mappar/inkorgar, utan det är själva loopen som ritar föremålen på skärmen som tar tid.
    def load():
        inbox_messages = service.users().messages().list(maxResults='20', userId='me', q='in:inbox').execute()
        inbox_ids = inbox_messages['messages']
        sent_messages = service.users().messages().list(maxResults='20', userId='me', q='in:sent').execute()
        sent_ids = sent_messages['messages']
        drafts_messages = service.users().messages().list(maxResults='20', userId='me', q='in:draft').execute()
        drafts_ids = drafts_messages['messages']
        
        inboxes = {'inbox_messages':inbox_messages, 'inbox_ids':inbox_ids, 'sent_messages':sent_messages, 'sent_ids':sent_ids, 'drafts_messages':drafts_messages, 'drafts_ids':drafts_ids}
        return inboxes

    # Returnar mejlens innehåll och om mejlens innehåll av någon anledning inte finns så returnas istället elementet 'snippet' som innehåller en bit av mejlet.
    def parse_msg(msg):
        if msg.get('payload').get('body').get('data'):
            return base64.urlsafe_b64decode(msg.get('payload').get('body').get('data').encode('ASCII')).decode('utf-8')
        return msg.get('snippet')

    # Laddar in mail enligt den angivna söktermen.
    def search_load(search_term):
        search_messages = service.users().messages().list(maxResults='20', userId='me', q=search_term).execute()
        search_ids = search_messages['messages']

        search_results = {'search_messages':search_messages, 'search_ids': search_ids}
        return search_results


    # Hemskärmen
    class HomeScreen(Screen, GridLayout, MDApp):
        def __init__(self, **kwargs):

            # Variabler som håller koll på vilken mapp som visas.
            self.inbox_bool = False
            self.sent_bool = False
            self.drafts_bool = False

            # Lägger till TwoLinwListItem i list_view för varje mail som finns i inbox.
            def inbox(self):
                if self.inbox_bool is True:
                    return
                elif self.inbox_bool is False:
                    self.list_view.clear_widgets()
                    self.inbox_bool = True
                    self.sent_bool = False
                    self.drafts_bool = False
                    inbox_ids = load()['inbox_ids']
                    
                    for id in inbox_ids[:20]:
                        message = service.users().messages().get(userId='me', id = id['id']).execute()
                        value1 = None
                        value2 = None
                        value3 = parse_msg(message)
                        for header in message['payload']['headers']:
                            if header['name']=='Subject':
                                if header['value']!='':
                                    value1 = header['value']
                                else:
                                    value1 = '(No subject)'
                            if header['name']=='From':
                                value2 = header['value']
                            if value1 != None and value2 != None:
                                self.list_view.add_widget(TwoLineListItem(text=value1, secondary_text='From: '+value2, on_press=(partial(self.changerReadMail, 'Subject: '+value1, 'From: '+value2, value3))))
                                value1 = None
                                value2 = None
            # Lägger till TwoLinwListItem i list_view för varje mail som finns i sent.
            def sent(self):
                if self.sent_bool is True:
                    return
                elif self.sent_bool is False:
                    self.list_view.clear_widgets()
                    self.inbox_bool = False
                    self.sent_bool = True
                    self.drafts_bool = False
                    sent_ids = load()['sent_ids']
                    
                    for id in sent_ids[:20]:
                        message = service.users().messages().get(userId='me', id = id['id']).execute()
                        value1 = None
                        value2 = None
                        value3 = parse_msg(message)
                        for header in message['payload']['headers']:
                            if header['name']=='Subject':
                                if header['value']!='':
                                    value1 = header['value']
                                else:
                                    value1 = '(No subject)'
                            if header['name']=='To':
                                value2 = header['value']
                            if value1 != None and value2 != None:
                                self.list_view.add_widget(TwoLineListItem(text=value1, secondary_text='To: '+value2, on_press=(partial(self.changerReadMail, 'Subject: '+value1, 'To: '+value2, value3))))
                                value1 = None
                                value2 = None

            # Lägger till TwoLinwListItem i list_view för varje mail som finns i drafts.
            def drafts(self):
                if self.drafts_bool is True:
                    return
                elif self.drafts_bool is False:
                    self.list_view.clear_widgets()
                    self.inbox_bool = False
                    self.sent_bool = False
                    self.drafts_bool = True
                    drafts_ids = load()['drafts_ids']
                    
                    for id in drafts_ids[:20]:
                        message = service.users().messages().get(userId='me', id=id['id']).execute()
                        value1 = None
                        value2 = None
                        value3 = parse_msg(message)
                        for header in message['payload']['headers']:
                            if header['name']=='Subject':
                                if header['value']!='':
                                    value1 = header['value']
                                else:
                                    value1 = '(No subject)'
                            if header['name']=='To':
                                value2 = header['value']
                            if value1 != None and value2 != None:
                                self.list_view.add_widget(TwoLineListItem(text=value1, secondary_text='To: '+value2, on_press=(partial(self.changerReadMail, 'Subject: '+value1, 'To: '+value2, value3))))
                                value1 = None
                                value2 = None

            # Lägger till TwoLinwListItem i list_view för varje mail som search_load returnerar.
            def search(self):
                self.list_view.clear_widgets()
                self.inbox_bool = False
                self.sent_bool = False
                self.drafts_bool = False
                search_ids = search_load(self.search_field.text)['search_ids']
                
                for id in search_ids[:20]:
                    message = service.users().messages().get(userId='me', id=id['id']).execute()
                    value1 = None
                    value2 = None
                    value3 = parse_msg(message)
                    for header in message['payload']['headers']:
                        if header['name']=='Subject':
                            if header['value']!='':
                                value1 = header['value']
                            else:
                                value1 = '(No subject)'
                        if header['name']=='From':
                            value2 = header['value']
                        if value1 != None and value2 != None:
                            self.list_view.add_widget(TwoLineListItem(text=value1, secondary_text='From: '+value2, on_press=(partial(self.changerReadMail, 'Subject: '+value1, 'From: '+value2, value3))))
                            value1 = None
                            value2 = None

            # Uppdaterar den mailboxen som är laddad.
            def refresh(self):
                if self.drafts_bool is True:
                    self.drafts_bool = False
                    drafts(self)
                elif self.sent_bool is True:
                    self.sent_bool = False
                    sent(self)
                elif self.inbox_bool is True:
                    self.inbox_bool = False
                    inbox(self)
                else:
                    return

            # Rutnät konstruktor
            super(HomeScreen, self).__init__(**kwargs)

            # HomeScreen är en GridLayout och består av ett antal grids i varandra. Nedan följer dessa grids och andra widgets.

            # Antal kolumner i grid
            self.first_grid = GridLayout()
            self.first_grid.cols = 2
            self.add_widget(self.first_grid)

            # Sökfält
            self.search_field = MDTextField(font_size='20sp')
            self.search_field.hint_text = 'Search'
            self.first_grid.add_widget(self.search_field)
            self.first_grid.add_widget(MDRoundFlatButton(text='Search', font_size='20sp', on_press=lambda x:search(self)))


            # En grid som innehäller två grids
            self.main_grid = GridLayout()
            self.main_grid.cols = 2
            self.first_grid.add_widget(self.main_grid)

            # Vänstra kolumnen av skärmen, innehåller menyn
            self.left_grid = GridLayout()
            self.left_grid.cols = 1
            self.left_grid.size_hint = (.12, 0)
            self.main_grid.add_widget(self.left_grid)

            # Högra kolumnen av skärmen, innehåller mails.
            self.right_grid = GridLayout()
            self.right_grid.cols = 1
            self.scroll_view = ScrollView()
            self.list_view = MDList()
            self.scroll_view.add_widget(self.list_view)
            self.first_grid.add_widget(MDRaisedButton(text='Refresh', font_size='20sp', size_hint=(None,.1), on_press=lambda x:refresh(self)))   
            self.right_grid.add_widget(self.scroll_view)
            self.main_grid.add_widget(self.right_grid)

            # Knappar för menyn
            self.left_grid.add_widget(MDRaisedButton(text='New', size_hint=(.3, .2), font_size='30sp', on_press=lambda x:self.changerNewMail()))
            self.left_grid.add_widget(MDFlatButton(text='Inbox', size_hint=(.3, .3), font_size='25sp', on_press=lambda x:inbox(self)))
            self.left_grid.add_widget(MDFlatButton(text='Sent', size_hint=(.3, .3), font_size='25sp', on_press=lambda x:sent(self)))
            self.left_grid.add_widget(MDFlatButton(text='Drafts', size_hint=(.3, .3), font_size='25sp', on_press=lambda x:drafts(self)))

            # Visar inkorgen när programmet startas
            inbox(self)

        # Metod som byter skärm till NewMail
        def changerNewMail(self, *args):
            self.manager.transition.direction = 'left'
            self.manager.current = 'mail'

        # Metod som byter skärm till ReadMail och byter ReadMail:s label-texter till rätt innehåll, ämne och avsändare.
        def changerReadMail(self, *args):
            self.manager.transition.direction = 'right'
            print(args)
            if args[0]=='':
                self.manager.get_screen('read').ids.subject_label.text = '(No subject)'
            else:
                self.manager.get_screen('read').ids.subject_label.text = args[0]
            self.manager.get_screen('read').ids.from_label.text = args[1]
            self.manager.get_screen('read').ids.content_label.text = html.unescape(args[2])
            self.manager.current = 'read'


    # Skärmen för nytt mail
    class NewMail(Screen, FloatLayout, MDApp):
        def __init__(self, **kwargs):
            super(NewMail, self).__init__(**kwargs)

            # Tillbaka knappen
            self.add_widget(MDFillRoundFlatButton(text='Back', font_size='20sp', size_hint=(.1,.1), pos_hint={'x':.01, 'y':.02}, on_press=lambda x: self.changerInbox()))   
            self.add_widget(MDFillRoundFlatButton(text='Send', font_size='20sp', size_hint=(.1,.1), pos_hint={'x':.89, 'y':.02}, on_press=lambda x: self.sendMail()))   

            # Nedan följer "Till:" fältet.
            self.to = MDTextField(helper_text_mode='on_focus', font_size='25sp', pos_hint={'x':.01, 'y':.88})  
            self.add_widget(self.to)
            self.to.hint_text = 'To:' # Jag var tvungen att göra denna raden och raden nedanför separata på grund av en bug i kivymd som diskuteras i följande github-tråd. https://github.com/kivymd/KivyMD/issues/493
            self.to.helper_text = 'Ex. robin.widjeback@elev.ga.ntig.se'

            # Nedan följer "Ämne:" fältet
            self.subject = MDTextField(helper_text_mode='on_focus', font_size='20sp', pos_hint={'x':.01, 'y':.78}, max_text_length=50)  
            self.add_widget(self.subject)
            self.subject.hint_text = 'Subject:' # Jag var tvungen att göra denna raden och raden nedanför separata på grund av en bug i kivymd som diskuteras i följande github-tråd. https://github.com/kivymd/KivyMD/issues/493
            self.subject.helper_text = 'Max 50 tecken'

            # Nedan följer textrutan för mailets innehåll
            self.content = MDTextField(pos_hint={'x':.01, 'top':.75}, multiline=True, max_height='380dp')  
            self.add_widget(self.content)
            self.content.hint_text = 'Content:' # Jag var tvungen att göra denna raden och raden nedanför separata på grund av en bug i kivymd som diskuteras i följande github-tråd. https://github.com/kivymd/KivyMD/issues/493

        # Byter till inkorgsskärmen
        def changerInbox(self, *args):
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'
        
        #Skickar mail
        def sendMail(self, *args):
            if '@' and '.' in self.to.text and self.to.text.count('@') == 1 and len(self.to.text) >= 5:
                self.to.error = False
                self.to.helper_text = 'Ex. robin.widjeback@elev.ga.ntig.se'
                new_mail = create_message('me', self.to.text, self.subject.text, self.content.text)
                send_message(service, 'me', new_mail)
                self.sent_dialog = MDDialog(title='Sent', text='Your mail to '+self.to.text+' has been sent!')
                self.sent_dialog.open()
                self.to.text = ''
                self.subject.text = ''
                self.content.text = ''
            else:
                self.to.error = True
                self.to.helper_text = 'Must contain one "@" and at least one "."'

    #Skärmen för att läsa mail
    class ReadMail(Screen, FloatLayout, MDApp):
        def __init__(self, **kwargs):
            super(ReadMail, self).__init__(**kwargs)
            # Skapar label för 'from'
            self.from_label = MDLabel(pos_hint={'x':.01, 'y':.45})
            self.ids['from_label'] = weakref.ref(self.from_label)
            self.add_widget(self.from_label)

            # Skapar label för 'subject'
            self.subject_label = MDLabel(pos_hint={'x':.01, 'y':.35})
            self.ids['subject_label'] = weakref.ref(self.subject_label)
            self.add_widget(self.subject_label)

            # Skapar label för 'content' och lägger content_label i en ScrollView. När en lång text laddas in i content_label sker, just nu,
            # en bugg som innebär att halva texten hamnar utanför skärmen. Jag har skrivit om detta på stackoverflow (https://stackoverflow.com/questions/66301927/having-trouble-centering-mdlabel-vertically-inside-scrollview-kivy-kivymd).
            self.scroll_view = ScrollView(pos_hint={'x':.01, 'y':.13}, do_scroll_x=False, size_hint_y=.65)
            self.content_label = MDLabel(size_hint_y=None)
            self.ids['content_label'] = weakref.ref(self.content_label)
            self.scroll_view.add_widget(self.content_label)
            self.add_widget(self.scroll_view)

            # Skapar tillbaka knappen.
            self.add_widget(MDFillRoundFlatButton(text='Back', font_size='20sp', size_hint=(.1,.1), pos_hint={'x':.01, 'y':.02}, on_press=lambda x:self.changerInbox()))   

        # Byter skärmen till HomeScreen.
        def changerInbox(self, *args):
            self.manager.transition.direction = 'left'
            self.manager.current = 'home'

    # Applikation
    class KivyApp(MDApp): 
        def build(self):
            #Bestämmer default skärmstorlek
            Window.size = (1000, 600)
            #Tillåter mig att använda flera skärmar, se skärmar i klasserna ovan!
            self.sm = ScreenManager()
            
            #Deklaration av skärmarna
            self.sm.add_widget(HomeScreen(name='home'))
            self.sm.add_widget(NewMail(name='mail'))
            self.sm.add_widget(ReadMail(name='read'))

            #Bestämmer att home (inkorgsskärmen) visas när programmet startas
            self.sm.current = 'home'
            return self.sm
        
    KivyApp().run()


if __name__ == '__main__':
    main()
