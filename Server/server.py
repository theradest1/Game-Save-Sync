from flask import Flask, request, send_from_directory
import json
from datetime import datetime
import os

app = Flask(__name__)
port = 3030
if os.name == 'nt':  # 'nt' represents Windows
    print("Running on Windows")
    dirSeperator = "\\"
elif os.name == 'posix':  # 'posix' represents Linux, Unix, or macOS
    print("Running on Linux or Unix")
    dirSeperator = "/"
else:
    print("Running on an unknown system (directories will prolly be messed up)")
    dirSeperator = "/"
base_dir = dirSeperator.join(__file__.split(dirSeperator)[0:-1])
config_dir = base_dir + dirSeperator + "config.json"

#get save directory
with open(config_dir, 'r') as configFile:
    config = json.load(configFile)
    save_dir = config[0]["saveDir"]

def currentDateTime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    print(file.filename)
    file.save(save_dir + dirSeperator + file.filename)

    with open(config_dir, 'r') as configFile:
        config = json.load(configFile)        
    #save new id
    with open(config_dir, "w") as configFile:
        config[1]["lastUpload"][file.filename.split(".")[0]] = currentDateTime()
        json.dump(config, configFile, indent=4)
    
    return 'File uploaded successfully!', 200

@app.route('/download/<saveID>')
def download_file(saveID):
    #print("Client requested save with ID", saveID)
    
    with open(config_dir, 'r') as configFile:
        config = json.load(configFile)        
    #save new id
    with open(config_dir, "w") as configFile:
        config[1]["lastDownload"][saveID] = currentDateTime()
        json.dump(config, configFile, indent=4)
    
    return send_from_directory(save_dir, str(saveID) + ".zip", as_attachment=True)

@app.route("/getInfo/<saveID>")
def saveInfo(saveID):
    lastDownload = "none"
    lastUpload = "none"
    with open(config_dir, 'r') as configFile:
        config = json.load(configFile)
        if str(saveID) in config[1]["lastDownload"]:
            lastDownload = config[1]["lastDownload"][str(saveID)]
        if str(saveID) in config[1]["lastUpload"]:
            lastUpload = config[1]["lastUpload"][str(saveID)]
    return f"{lastDownload}\n{lastUpload}"

@app.route('/getID')
def giveCurrentID():
    #get current id
    with open(config_dir, 'r') as configFile:
        config = json.load(configFile)
        currentID = config[0]["currentID"]
        
    #save new id
    with open(config_dir, "w") as configFile:
        config[0]["currentID"] = config[0]["currentID"] + 1
        json.dump(config, configFile, indent=4)
        
    print("Current ID:", currentID)
    return str(currentID)
        
if __name__ == '__main__':
    app.run(debug=True, port=port, host='0.0.0.0')
