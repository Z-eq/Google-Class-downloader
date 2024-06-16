import os
import pickle
import io
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Define the scopes required
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def download_file(service, file_id, file_name, download_folder):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(download_folder, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

def main():
    creds = None
    # Ensure reauthentication by deleting the token.pickle file if it exists
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Loading client secrets from file...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)  # Specify a port here
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        classroom_service = build('classroom', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        # Fetch courses
        try:
            courses_response = classroom_service.courses().list().execute()
            courses = courses_response.get('courses', [])
            
            if not courses:
                print('No courses found.')
                return
            
            # Print available courses and their IDs
            print('Available courses:')
            for course in courses:
                print(f'{course["name"]} - {course["id"]}')
            
            # Prompt user to enter a course ID
            selected_course_id = input('Enter the numerical course ID you want to download materials from: ')
            
            # Find the selected course
            selected_course = next((course for course in courses if course['id'] == selected_course_id), None)
            
            if not selected_course:
                print('Course not found.')
                return
            
            print(f'Selected course: {selected_course["name"]}')
            
            # Prompt user to enter a coursework ID
            selected_coursework_id = input('Enter the coursework ID within the selected course: ')
            
            # Ask user what types of files to download
            download_pdfs = input('Do you want to download PDFs? (yes/no): ').strip().lower() == 'yes'
            download_videos = input('Do you want to download videos? (yes/no): ').strip().lower() == 'yes'
            
            # Fetch coursework for the selected course
            coursework_response = classroom_service.courses().courseWork().list(courseId=selected_course_id).execute()
            coursework = coursework_response.get('courseWork', [])
            
            if not coursework:
                print(f'No coursework found for course: {selected_course["name"]}')
                return
            
            # Process and download materials for the specific coursework
            selected_coursework = next((work for work in coursework if work['id'] == selected_coursework_id), None)
            
            if not selected_coursework:
                print('Coursework not found.')
                return
            
            if 'materials' in selected_coursework:
                for material in selected_coursework['materials']:
                    if 'driveFile' in material:
                        file_id = material['driveFile']['driveFile']['id']
                        file_name = material['driveFile']['driveFile']['title']
                        mime_type = material['driveFile']['driveFile']['mimeType']
                        if (download_pdfs and mime_type == 'application/pdf') or (download_videos and mime_type.startswith('video/')):
                            print(f'Downloading {file_name} from Google Drive')
                            download_file(drive_service, file_id, file_name, './downloads')
            else:
                print('No materials found for the selected coursework.')
        except HttpError as err:
            print(f'An HTTP error occurred: {err}')
    except GoogleAuthError as auth_err:
        print(f'An authentication error occurred: {auth_err}')
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
