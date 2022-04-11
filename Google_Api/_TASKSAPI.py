import pandas as pd
import datetime
import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# link to the api documentation can be found at https://developers.google.com/tasks
# refresh the token on the link below if you dont have permission switch to uchekesla account 
# donwload json and update secret_file 
# delete the pickle file that you have created
# and to renew credentials go to https://console.cloud.google.com/apis/credentials?authuser=1&project=learned-vault-319419 

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

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0, 000).isoformat() + 'Z'
    return dt

"""
Initialize response
"""
def construct_service_and_response_for_tasklists():
    CLIENT_SECRET_FILE = r'automated_system\Google_Api\client_secret_1028475286088-bj03n932hpj20nhpmo2qp9ljdndhjueb.apps.googleusercontent.com.json'
    API_NAME = 'tasks'
    API_VERSION = 'v1'
    SCOPES = ["https://www.googleapis.com/auth/tasks"]
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    response = service.tasklists().list().execute()
    return service, response

def construct_service_and_response_for_tasks(index_of_main_tasklists):
    CLIENT_SECRET_FILE = r'automated_system\Google_Api\client_secret_30-09-2021.apps.googleusercontent.com.json'
    API_NAME = 'tasks'
    API_VERSION = 'v1'
    SCOPES = ["https://www.googleapis.com/auth/tasks"]
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    servc, respns = construct_service_and_response_for_tasklists()
    Tasklist = respns.get('items')[index_of_main_tasklists]['id']
    response = service.tasks().list(
        tasklist=Tasklist
    ).execute()
    return service, response
"""
Insert Method
"""
def construct_request_body(title, notes=None, due=None, status='needsAction', deleted=False):
    try:
        request_body = {
        'title': title,
        'notes': notes,
        'due': due,
        'deleted': deleted,
        'status': status
        }
        return request_body
    except Exception:
        return None

def insert_tasklist(title, index_of_main_tasklists, notes, dt):
    service, response = construct_service_and_response_for_tasklists()
    Tasklist = response.get('items')[index_of_main_tasklists]
    TasklistId = Tasklist['id']
    new_task_response = service.tasklists().insert(
        body=construct_request_body(title, notes=notes, due=dt),
    ).execute()
    print(new_task_response)

def insert_task_to_tasklist(title, index_of_main_tasklists, notes, dt):
    service, response = construct_service_and_response_for_tasklists()
    Tasklist = response.get('items')[index_of_main_tasklists]
    TasklistId = Tasklist['id']
    new_task_response = service.tasks().insert(
        body=construct_request_body(title, notes=notes, due=dt),
        tasklist=TasklistId
    ).execute()
    print(new_task_response)

def update_main_task_title(index, title):
    service, response = construct_service_and_response_for_tasklists() 
    Tasklist = response.get('items')[index]
    print(Tasklist)
    Tasklist['title'] = title
    service.tasklists().update(tasklist=Tasklist['id'], body=Tasklist).execute()

"""
List Method
"""
dt_Max = convert_to_RFC_datetime(2022, 5, 1)

def list_tasks_due_dt(index_of_main_tasklists, dt_Max):
    service, response = construct_service_and_response_for_tasklists()
    Tasklist = response.get('items')[index_of_main_tasklists]
    TasklistId = Tasklist['id']

    response = service.tasks().list(
        tasklist=TasklistId,
        dueMax=dt_Max,
        showCompleted=False
    ).execute()
    lstItems = response.get('items')
    nextPageToken = response.get('nextPageToken')
    print(pd.DataFrame(lstItems))

"""
    Delete Method
    isinstance(int(item.get('title').replace('Tasklst #', '')), int):
    int(item.get('title').replace('Tasklst #', '')) > 50:
    service.tasklists().delete(tasklist=item.get('id')).execute()
"""
def delete_tasklists(index_of_main_tasklists):
    service, response = construct_service_and_response_for_tasklists()
    Tasklist = response.get('items')[index_of_main_tasklists]
    TasklistId = Tasklist['id']
    new_task_response = service.tasklists().delete(
        tasklist=TasklistId
    ).execute()
    print(new_task_response)

def delete_tasks(index_of_main_tasklists,index_of_main_tasks):
    service0, response0 = construct_service_and_response_for_tasklists()
    Tasklist0 = response0.get('items')[index_of_main_tasklists]
    TasklistId0 = Tasklist0['id']
    service, response = construct_service_and_response_for_tasks(index_of_main_tasklists)
    Tasklist = response.get('items')[index_of_main_tasks]
    TasklistId = Tasklist['id']
    new_task_response = service.tasks().delete(
        tasklist=TasklistId0,
        task=TasklistId
    ).execute()
    print(new_task_response)
