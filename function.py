from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    """Get valid credentials with longer expiration time."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                # リフレッシュに失敗した場合は新規認証を行う
                creds = None
                
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', 
                SCOPES
            )
            # フローの設定を修正
            flow.authorization_url(
                access_type='offline',
                prompt='consent'
            )
            creds = flow.run_local_server(port=0)
            
        # 認証情報を保存
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

def todays_event():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        today = datetime.date.today()
        return_list = []

        if not events:
            return return_list
            
        for event in events:
            if event['start'].get('dateTime'):
                start = event['start'].get('dateTime')
            else:
                start = event['start'].get('date')
            event_date = datetime.datetime.strptime(start[:10], '%Y-%m-%d').date()
            if event_date == today:
                return_list.append(event['summary'])
        
        return return_list
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []