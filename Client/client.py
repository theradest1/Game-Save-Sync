import requests
import tkinter as tk
from tkinter import filedialog, simpledialog
import zipfile
import os
import json

#create exe with:
#pyinstaller client.py --onefile -w

config = []

if os.name == 'nt':  # 'nt' represents Windows
    print("Running on Windows")
    dirSeperator = "\\"
elif os.name == 'posix':  # 'posix' represents Linux, Unix, or macOS
    print("Running on Linux or Unix")
    dirSeperator = "/"
else:
    print("Running on an unknown system (directories will prolly be messed up)")
    dirSeperator = "/"
base_dir = "./"
config_dir = base_dir + "config.json"

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
    root.geometry("300x400")

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
    
    button6 = tk.Button(root, text="Add ID", command=addID)
    button6.pack()
    
    button4 = tk.Button(root, text="Save Info", command=saveInfo)
    button4.pack()
    
    button5 = tk.Button(root, text="Remove save", command=removeSave)
    button5.pack()
    
    button6 = tk.Button(root, text="Set server", command=setServer)
    button6.pack()
    

    # Status label to display information
    global status_label
    status_label = tk.Label(root, text="Status: done")
    status_label.pack()

    # Start the GUI event loop
    root.mainloop()
    
def sendFile(file_path):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path.split(dirSeperator)[-1], file, 'multipart/form-data')}
        response = requests.post(uploadURL, files=files)

    if response.status_code != 200:
        print("File upload failed. Status code:", response.status_code)
        setStatus("Error - check console", False)


def zipDirectory(directory, zip_name):
    zip_path = base_dir + dirSeperator + zip_name
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
        zippedFileDir = base_dir + dirSeperator + str(saveID) + ".zip"
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
    global config, saves, uploadURL, downloadURL, currentIDURL, infoURL
    with open(config_dir, 'r') as configFile:
        allConfig = json.load(configFile)
        print(allConfig)
        config = allConfig[1]
        
        baseURL = allConfig[0]["baseURL"]
        uploadURL = baseURL + allConfig[0]["uploadURL"]
        downloadURL = baseURL + allConfig[0]["downloadURL"]
        currentIDURL = baseURL + allConfig[0]["getIDURL"]
        infoURL = baseURL + allConfig[0]["infoURL"]
        
    #this is just for displaying saves
    saves = []
    for saveData in config:
        saves.append(saveData["name"])

def saveConfig():
    with open(config_dir, 'r') as configFile:
        allConfig = json.load(configFile)
    with open(config_dir, 'w') as configFile:
        allConfig[1] = config
        json.dump(allConfig, configFile, indent=4)
        
def upload():
    selectedIndex = listbox.curselection()[0]
    pushChanges(selectedIndex)
    
def download():
    selectedIndex = listbox.curselection()[0] 
    pullChanges(selectedIndex)
    
def saveInfo():
    setStatus("Getting save info...")
    
    selectedIndex = listbox.curselection()[0]
    saveName = config[selectedIndex]["name"]
    saveID = config[selectedIndex]["id"]
    savePath = config[selectedIndex]["path"]
    
    response = requests.get(infoURL + "/" + str(saveID))
    
    if response.status_code != 200:
        print("Info get failed", response.status_code)
        setStatus("Couldnt get external save info", False)
        lastDownload = "idk"
        lastUpload = "idk"
    else:
        setStatus("Done!")
        lastDownload = response.text.split("\n")[0]
        lastUpload = response.text.split("\n")[1]
    
    simpledialog.messagebox.showinfo(f"Save Info",f"Name: {saveName}\n\nID: {saveID}\n\nPath: {savePath}\n\nLast upload to server: {lastUpload}\n\nLast download from server: {lastDownload}")
    
def addID():
    
    savePath = filedialog.askdirectory()

    # Check if a folder was selected or dialog was canceled
    if not savePath:
        print("Selection canceled or no folder chosen.")
        root.deiconify()
        return
    
    saveID = int(simpledialog.askstring("Input", "Enter the ID (from your friend):"))
    saveName = simpledialog.askstring("Input", "Enter the name (anything):")
    
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
    
def removeSave():
    selectedIndex = listbox.curselection()[0]
    del config[selectedIndex]
    saveConfig()
    loadConfig()
    listbox.delete(selectedIndex) #update gui
    setStatus("Done!")
    
def setServer():
    serverIP = simpledialog.askstring("Input", "Enter server's IP:")
    serverPort = simpledialog.askstring("Input", "Enter server's port:")
    
    baseURL = f"http://{serverIP}:{serverPort}/"
    
    with open(config_dir, 'r') as configFile:
        allConfig = json.load(configFile)
    with open(config_dir, 'w') as configFile:
        allConfig[0]["baseURL"] = baseURL
        json.dump(allConfig, configFile, indent=4)

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
        setStatus("Selection canceled or no folder chosen.")
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


