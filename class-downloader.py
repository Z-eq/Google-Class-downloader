from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

import io
import os
import os.path
from os import path
import pprint

def main():

    service = get_classroom_service()
    courses = service.courses().list(pageSize=1).execute()
    for course in courses['courses']:
        print(course['name'])
    
    downd_files=list()

    for course in courses['courses']:

        course_name = course['name']
        course_id = course['id']
        print("Downloading files for course : ", course_name)
        if not (path.exists(course_name)):
            os.mkdir('./' + course_name)
            os.mkdir('./' +course_name+ "/cours")
            os.mkdir('./' + course_name+"/td")
        else:
            print("{} Already exists ".format(course_name))

        anoncs = service.courses().announcements().list(
            courseId=course_id).execute()
        work = service.courses().courseWork().list(
            courseId=course_id).execute()

        downd_files = downd_files + download_annonc_files(anoncs, course_name)
        downd_files = downd_files + download_works_files(work, course_name)
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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('classroom-token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('classroom', 'v1', credentials=creds)
        return service
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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('drive-token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
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
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.seek(0)
        with open(os.path.join('./', course_name, file_name), 'wb') as f:
            f.write(fh.read())
            f.close()
    except HttpError as error:
        print(f'An error occurred: {error}')



def download_annonc_files(announcements, course_name):
    annonc_list = announcements.keys()
    downloaded = list()
    if (len(annonc_list) != 0):
        present_files = getListOfFiles(os.path.join('./', course_name))

        for announcement in announcements['announcements']:
            try:  #if this announcements contain a file then do this
                for val in announcement['materials']:
                    file_id = val['driveFile']['driveFile']['id']
                    file_name = val['driveFile']['driveFile']['title']
                    extension = (
                        os.path.splitext(file_name)
                    )[1]  #the extension exists in second elemnts of returned tuple
                    path_str = os.path.join('./', course_name, file_name)

                    if ((valid(extension[1:])) and (file_name not in present_files)) :
                        print("DOWNLOADING " ,file_name)
                        download_file(file_id, file_name, course_name)
                        downloaded.append("Annonoucemet :  "+course_name +' : ' + file_name)                        
                    elif (file_name in present_files):
                        print(file_name, "already exists")
                    elif not valid(extension[1:]):
                        print('Unsupported file type: ', extension[1:] )
                    else:
                        print("Something went wrong")
            except KeyError as e:
                continue
    return downloaded

def download_works_files(works, course_name):
    works_list = works.keys()
    downloaded = list()
    if (len(works_list) != 0):
        present_files = getListOfFiles(os.path.join('./', course_name))

        for work in works['courseWork']:
            try:  #if this announcements contain a file then do this
                for val in work['materials']:
                    file_id = val['driveFile']['driveFile']['id']
                    file_name = val['driveFile']['driveFile']['title']

                    if (file_name[0:10] == "[Template]"):
                        file_altern_link = val['driveFile']['driveFile']['alternateLink']

                        file_id = file_altern_link[file_altern_link.find('=')+1:]
                    extension = (
                        os.path.splitext(file_name)
                    )[1]  #the extension exists in second elemnts of returned tuple
                    path_str = os.path.join('./', course_name, file_name)
                    if valid(extension[1:]) and (file_name not in present_files) :
                        print("DOWNLOADING " ,file_name)
                        download_file(file_id, file_name, course_name)
                        downloaded.append("Devoir :  "+course_name +' : ' + file_name)                        
                    elif (file_name in present_files):
                        print(file_name, "already exists")
                    elif not valid(extension[1:]):
                        print('Unsupported file type: ', extension[1:] )
                    else:
                        print("Something went wrong")

            except KeyError as e:
                continue
    return downloaded


def valid(ch):
    return ch in [
        'pdf', 'docx', 'pptx', 'png', 'jpg', 'html', 'css', 'js', 'java',
        'class', 'txt', 'r', 'm', ' sql', 'doc', 'mp3', 'rar', 'zip', 'py', 'c'
    ]


def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # nam3es in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return [ch[ch.rfind('/')+1:] for ch in allFiles]

if __name__ == '__main__':
    main()
