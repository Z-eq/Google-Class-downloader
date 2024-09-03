import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

import io
import pprint

#def main():
    service = get_classroom_service()
    courses = service.courses().list(pageSize=1).execute()
    for course in courses['courses']:
        print(course['name'])
    
    downd_files = []

    for course in courses['courses']:
        course_name = course['name']
        course_id = course['id']
        print("Downloading files for course:", course_name)
        
        if not os.path.exists(course_name):
            os.makedirs(os.path.join(course_name, "cours"))
            os.makedirs(os.path.join(course_name, "td"))
        else:
            print(f"{course_name} already exists")

        anoncs = service.courses().announcements().list(courseId=course_id).execute()
        work = service.courses().courseWork().list(courseId=course_id).execute()

        downd_files.extend(download_annonc_files(anoncs, course_name))
        downd_files.extend(download_works_files(work, course_name))
        
    pprint.pprint(downd_files)

def get_classroom_service():
    SCOPES = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.announcements.readonly',
        'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly'
    ]
    creds = None
    if os.path.exists('classroom-token.json'):
        creds = Credentials.from_authorized_user_file('classroom-token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('classroom-token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        return build('classroom', 'v1', credentials=creds)
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('drive-token.json'):
        creds = Credentials.from_authorized_user_file('drive-token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('drive-token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        return build('drive', 'v3', credentials=creds)
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def download_file(file_id, file_name, course_name):
    service = get_drive_service()
    if not service:
        print('Drive service initialization failed.')
        return
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.seek(0)
        with open(os.path.join(course_name, file_name), 'wb') as f:
            f.write(fh.read())
    except HttpError as error:
        print(f'An error occurred: {error}')

def download_annonc_files(announcements, course_name):
    downloaded = []
    if announcements.get('announcements'):
        present_files = getListOfFiles(os.path.join('./', course_name))

        for announcement in announcements['announcements']:
            try:
                for val in announcement['materials']:
                    file_id = val['driveFile']['driveFile']['id']
                    file_name = val['driveFile']['driveFile']['title']
                    extension = os.path.splitext(file_name)[1][1:]
                    if valid(extension) and file_name not in present_files:
                        print("DOWNLOADING", file_name)
                        download_file(file_id, file_name, course_name)
                        downloaded.append(f"Announcement: {course_name}: {file_name}")
                    elif file_name in present_files:
                        print(f"{file_name} already exists")
                    elif not valid(extension):
                        print(f"Unsupported file type: {extension}")
            except KeyError:
                continue
    return downloaded

def download_works_files(works, course_name):
    downloaded = []
    if works.get('courseWork'):
        present_files = getListOfFiles(os.path.join('./', course_name))

        for work in works['courseWork']:
            try:
                for val in work['materials']:
                    file_id = val['driveFile']['driveFile']['id']
                    file_name = val['driveFile']['driveFile']['title']

                    if file_name.startswith("[Template]"):
                        file_altern_link = val['driveFile']['driveFile']['alternateLink']
                        file_id = file_altern_link.split('=')[1]
                    
                    extension = os.path.splitext(file_name)[1][1:]
                    if valid(extension) and file_name not in present_files:
                        print("DOWNLOADING", file_name)
                        download_file(file_id, file_name, course_name)
                        downloaded.append(f"Devoir: {course_name}: {file_name}")
                    elif file_name in present_files:
                        print(f"{file_name} already exists")
                    elif not valid(extension):
                        print(f"Unsupported file type: {extension}")
            except KeyError:
                continue
    return downloaded

def valid(ch):
    return ch in [
        'pdf', 'docx', 'pptx', 'png', 'jpg', 'html', 'css', 'js', 'java',
        'class', 'txt', 'r', 'm', 'sql', 'doc', 'mp3', 'rar', 'zip', 'py', 'c'
    ]

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = []
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles += getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return [os.path.basename(ch) for ch in allFiles]
