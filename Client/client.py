import requests
import tkinter as tk
from tkinter import filedialog
import zipfile
import os

url = 'http://localhost:3030/upload'  # Replace with the server URL you want to send the file to

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename()  # Show file selection dialog

    if file_path:
        print("Selected file:", file_path)
        return file_path
    else:
        print("No file selected")
        exit()

    
def sendFile(file_path):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path.split("/")[-1], file, 'multipart/form-data')}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        print("File uploaded successfully!")
    else:
        print("File upload failed. Status code:", response.status_code)


def zipDirectory(directory, zip_name):
    zip_path = os.path.abspath(zip_name)
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))
    return zip_path
    
def pushChanges(save_path):
    print("Compressing...")
    zippedFile = zipDirectory(save_path, "temp.zip")
    print("Sending...")
    sendFile(zippedFile)
    print("Done!")

while True:
    file_path = open_file_dialog()
    pushChanges(file_path)
    


