# Google

# pip install vimeo_downloader
# pip install google-auth-oauthlib
# pip install google-api-python-client
# pip install beautifulsoup4

import google.auth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from vimeo_downloader import Vimeo
from bs4 import BeautifulSoup 
import requests
import json
import os
import shutil
import time
import re


# Create google token
def createGoogleToken():
    scopes = [
        "https://www.googleapis.com/auth/drive",
        ]
    
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
    creds = flow.run_local_server()
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    google_drive = googleapiclient.discovery.build('drive', 'v3', credentials=creds)    

    return google_drive

def connectionGoogle():
    with open('token.json', 'r') as token_file:
        token_data = token_file.read()

    creds = Credentials.from_authorized_user_info(info=json.loads(token_data))
    service = build('drive', 'v3', credentials=creds)
    return service

def loadFileInGoogle(folder_id, title, service=""):
    print('Uploading videos to Google Drive')
    file = os.listdir('./video')
    
    file_path = os.path.join(os.getcwd(), f'video/{title}.mp4')
    file_metadata = {
                    'name': title,
                    'parents': [folder_id]
                }
    media = MediaFileUpload(file_path, resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('Load file in Google Drive')
    time.sleep(1)

    # Clear folder
    folder_path = os.path.join(os.getcwd(), f'video')
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    print(f'Deleted files: {file[0]}')

def sanitize_filename(filename):
    return re.sub(r'[^\w\d]+', '', filename)

def vimeoDownloader(url, filder_id_gd="", access_token=""):
    print('\nStarting to parse the link')
    try:
        video = Vimeo(url)
        stream = video.streams
        best_stream = stream[-1]
        title = best_stream.title

        title_res = sanitize_filename(title)
        print(f"Name file save: {title_res}")

        print('Downloading the video')
        best_stream.download(download_directory=os.path.join(os.getcwd(), 'video'), filename=title_res)
        print('Video downloaded from the link... Done!!!')

        if not access_token == "":
            print('Starting a download to Google Drive')
            loadFileInGoogle(filder_id_gd, title_res, access_token)
    except:
        print('Error downloading video')

def getCoursesVideo(path, filder_id_gd, access_token):
    with open(path) as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    container_div = soup.find('div', class_='container-iframe')
    iframes = container_div.find_all('iframe')
    if iframes:
        for iframe in iframes:
            vimeoDownloader(iframe.get('src'), filder_id_gd, access_token)
            

if __name__ == '__main__':

    # Create token
    def start():
        print('# | 1. Automated video download from Teachable sites')
        print('# | 2. Download a better quality video from Vimeo')
        command = input("What command do you want to execute? You want to execute the command number:\n")
        if command == '1':
            # Id folders in Google Drive 
            folder_id = [
                '1nONYZov1zkPWR_NvxlwuQh30IcifbauE',
                '1nbrndyF0GV4fQHY1fgkFCzmqrMgcBbTm',
                '1njqxnEG6sod3838WAi_atWcvTp4Q5wsj'
            ]

            #* --- Сonnect Google -----
            # In case the token is not created
            # access_token = createGoogleToken()

            # If the token has already been created
            access_token = connectionGoogle()

            # Количе
            courses_count = 4
            for el in range(courses_count):
                print(f"### | Load the files into the folder courses_{el}")
                path_folder = os.path.join(os.getcwd(), f'courses_{el}')
                cursor_folder = os.listdir(path_folder)

                for file in cursor_folder:
                    print(f"I start processing the file in the path: {os.path.join(path_folder, file)} to the folder with the id {folder_id[el]}")
                    getCoursesVideo(f"{path_folder}/{file}", folder_id[el], access_token)
                
                print('\n')

        elif command == '2':
            #  example "https://player.vimeo.com/video/302839415"
            url = input("Enter the link to download the video from Vimeo, in the best quality:\n")
            vimeoDownloader(url)
        else:
            print('Unfortunately I do not know this command, you have to type in the number 1 or number 2, and then press the "Enter" button')
            start()

    start()