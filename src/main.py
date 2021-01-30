from __future__ import print_function
from utils import get_current_ms, elapsed_time_to_ms
import pickle
import os.path
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']


def get_creds():
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
                '../assets/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_labels_id(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    labels_names_id = {}
    for label in labels:
        if label['name'] == "Do Not delete":
            return label['id']
        labels_names_id[label['name']] = label['id']

    if 'Do Not delete' not in labels_names_id:
        return service.users().labels().create(userId='me', body={
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
            "name": "Do Not delete"
        }).execute()


def delete_old_messages(service, not_delete_id):
    """
    :brief: Delete any messages with label 'Old' and without 'Not delete' one

    :param service: gmail service
    :param not_delete_id: id of the label 'Not delete'
    """
    messages = service.users().messages().list(userId='me', maxResults=1000).execute()
    messages = messages.get('messages', [])

    for message_raw in messages:
        message_data = service.users().messages().get(userId='me',
                                                      id=message_raw[
                                                          'id']).execute()
        if (get_current_ms() - int(message_data['internalDate'])) > elapsed_time_to_ms(nb_year=1) \
                and not_delete_id not in message_data['labelIds']:
            service.users().messages().trash(userId='me', id=message_raw['id']).execute()
            print("A mail had been deleted.")


def main():
    service = build('gmail', 'v1', credentials=get_creds())
    do_not_delete_id = get_labels_id(service)

    while True:
        delete_old_messages(service, do_not_delete_id)
        time.sleep(60*60)  # 1 hour


if __name__ == '__main__':
    main()
