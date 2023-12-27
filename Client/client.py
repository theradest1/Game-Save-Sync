import requests
import tkinter as tk
from tkinter import filedialog, simpledialog
import zipfile
import os
import json

uploadURL = 'http://localhost:3030/upload'
downloadURL = 'http://localhost:3030/download'
currentIDURL = 'http://localhost:3030/getID'
config = []
base_dir = "\\".join(__file__.split("\\")[0:-1])

def setStatus(status, printMsg = True):
    status_label.config(text=status)
    root.update()
    
    if printMsg:
        print(status)

def create_window(string_list):
    global root
    # Create main window
    root = tk.Tk()
    root.title("")
    root.geometry("250x300")

    # Create a listbox to display string options
    global listbox
    listbox = tk.Listbox(root)
    for item in string_list:
        listbox.insert(tk.END, item)
    listbox.pack()
    
    listbox.selection_set(0)

    # Create buttons to trigger different functions
    button1 = tk.Button(root, text="Upload", command=upload)
    button1.pack()

    button2 = tk.Button(root, text="Download", command=download)
    button2.pack()
    
    button3 = tk.Button(root, text="Add Folder", command=addFolder)
    button3.pack()
    
    button4 = tk.Button(root, text="Save Info", command=saveInfo)
    button4.pack()

    # Status label to display information
    global status_label
    status_label = tk.Label(root, text="Status: done")
    status_label.pack()

    # Start the GUI event loop
    root.mainloop()
    
def sendFile(file_path):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path.split("\\")[-1], file, 'multipart/form-data')}
        response = requests.post(uploadURL, files=files)

    if response.status_code != 200:
        print("File upload failed. Status code:", response.status_code)
        setStatus("Error - check console", False)


def zipDirectory(directory, zip_name):
    zip_path = base_dir + "\\" + zip_name
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
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
    setStatus("Compressing...")
    zippedFile = zipDirectory(savePath, str(saveID) + ".zip")
    setStatus("Sending...")
    sendFile(zippedFile)
    setStatus("Cleaning up...")
    os.remove(zippedFile)
    setStatus("Done!")

def pullChanges(saveIndex):
    saveID = config[saveIndex]["id"]
    setStatus("Requesting...")
    response = requests.get(downloadURL + "/" + str(saveID))
    
    if response.status_code == 200:
        zippedFileDir = base_dir + "\\" + str(saveID) + ".zip"
        with open(zippedFileDir, 'wb') as file:
            file.write(response.content)
    else:
        print("File download failed. Status code:", response.status_code)
        setStatus("Error - check console", False)
        return
    
    saveDir = config[saveIndex]["path"]
    setStatus("Cleaning old save...")
    for filename in os.listdir(saveDir):
        file_path = os.path.join(saveDir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)  # Delete the file
    
    setStatus("Unzipping...")
    unzipFile(zippedFileDir, saveDir)
    setStatus("Cleaning up...")
    os.remove(zippedFileDir)
    setStatus("Done!")

def loadConfig():
    global config, saves 
    with open(base_dir + "\\config.json", 'r') as configFile:
        config = json.load(configFile)
        
    #this is just for displaying saves
    saves = []
    for saveData in config:
        saves.append(saveData["name"])

def saveConfig():
    global config
    with open(base_dir + "\\config.json", 'w') as configFile:
        json.dump(config, configFile, indent=4)
        
def upload():
    selectedIndex = listbox.curselection()[0]
    pushChanges(selectedIndex)
    
def download():
    selectedIndex = listbox.curselection()[0] 
    pullChanges(selectedIndex)
    
def saveInfo():
    selectedIndex = listbox.curselection()[0]
    saveName = config[selectedIndex]["name"]
    saveID = config[selectedIndex]["id"]
    savePath = config[selectedIndex]["path"]
    simpledialog.messagebox.showinfo(f"Save Info",f"Name: {saveName}\n\nID: {saveID}\n\nPath: {savePath}")

def addFolder():
    setStatus("Getting new save id...")
    
    response = requests.get(currentIDURL) #get new ID
    if response.status_code == 200:
        saveID = int(response.content)
    else:
        print("New ID get failed, Status code:", response.status_code)
        root.deiconify()
        setStatus("Error - check console", False)
        message_window.destroy
        return
    print("new ID: " + str(saveID))
    
    setStatus("Done!")
    root.withdraw()  # Hide the main window
    savePath = filedialog.askdirectory()

    # Check if a folder was selected or dialog was canceled
    if not savePath:
        print("Selection canceled or no folder chosen.")
        root.deiconify()
        return
    
    saveName = simpledialog.askstring("Input", "Enter a name:")
    
    config.append(
        {
            "path": savePath,
            "id": saveID,
            "name": saveName
        }
    )
    
    saveConfig()
    loadConfig()
    
    listbox.insert(tk.END, saveName) # update save list
    root.deiconify() # Unhide the main window
    root.mainloop()  # update tkinter

loadConfig()
    
create_window(saves)


