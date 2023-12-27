import requests
import tkinter as tk
from tkinter import filedialog
import zipfile
import os
import json

uploadURL = 'http://localhost:3030/upload'
downloadURL = 'http://localhost:3030/download'
config = []

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
        response = requests.post(uploadURL, files=files)

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

def unzipFile(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
def pushChanges(saveIndex):
    saveData = config[saveIndex]
    savePath = saveData["path"]
    saveID = saveData["id"]
    
    print("Compressing...")
    print(savePath)
    zippedFile = zipDirectory(savePath, str(saveID) + ".zip")
    print("Sending...")
    #sendFile(zippedFile)
    print("Deleteing...")
    os.remove(zippedFile)
    print("Done!")

def pullChanges(saveIndex):
    saveID = config[saveIndex]["id"]
    print("Sending request for " + config[saveIndex]["name"])
    response = requests.get(downloadURL + "/" + str(saveID))

    if response.status_code == 200:
        with open(str(saveID) + ".zip", 'wb') as file:
            file.write(response.content)
        print(f"File '{str(saveID)}.zip' downloaded successfully!")
    else:
        print("File download failed. Status code:", response.status_code)
    
    unzipFile(str(saveID) + ".zip", "")

def loadConfig():
    global config    
    with open("config.json", 'r') as configFile:
        config = json.load(configFile)

def saveConfig():
    global config
    with open("config.json", 'w') as configFile:
        json.dump(config, configFile)

def printOptions(options):
    count = 0
    for option in options:
        print(str(count) + ": " + option)
        count += 1

loadConfig()
while True:
    action = input("push or pull save: ")
    
    saves = []
    for saveData in config:
        saves.append(saveData["name"])
    
    if action == "push":
        printOptions(saves)
        pushChanges(int(input("? ")))
    elif action == "pull":
        printOptions(saves)
        pullChanges(int(input("? ")))
    else:
        print("unknown command")


