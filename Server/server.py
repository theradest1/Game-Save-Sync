from flask import Flask, request, send_from_directory
import json
from datetime import datetime

app = Flask(__name__)
port = 3030
base_dir = "\\".join(__file__.split("\\")[0:-1])

#get save directory
with open(base_dir + "\\config.json", 'r') as configFile:
    config = json.load(configFile)
    save_dir = config[0]["saveDir"]

def currentDateTime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    print(file.filename)
    file.save(save_dir + "\\" + file.filename)

    with open(base_dir + "\\config.json", 'r') as configFile:
        config = json.load(configFile)        
    #save new id
    with open(base_dir + "\\config.json", "w") as configFile:
        config[1]["lastUpload"][file.filename.split(".")[0]] = currentDateTime()
        json.dump(config, configFile, indent=4)
    
    return 'File uploaded successfully!', 200

@app.route('/download/<saveID>')
def download_file(saveID):
    #print("Client requested save with ID", saveID)
    
    with open(base_dir + "\\config.json", 'r') as configFile:
        config = json.load(configFile)        
    #save new id
    with open(base_dir + "\\config.json", "w") as configFile:
        config[1]["lastDownload"][saveID] = currentDateTime()
        json.dump(config, configFile, indent=4)
    
    return send_from_directory(save_dir, str(saveID) + ".zip", as_attachment=True)

@app.route("/getInfo/<saveID>")
def saveInfo(saveID):
    lastDownload = "none"
    lastUpload = "none"
    with open(base_dir + "\\config.json", 'r') as configFile:
        config = json.load(configFile)
        if str(saveID) in config[1]["lastDownload"]:
            lastDownload = config[1]["lastDownload"][str(saveID)]
        if str(saveID) in config[1]["lastUpload"]:
            lastUpload = config[1]["lastUpload"][str(saveID)]
    return f"{lastDownload}\n{lastUpload}"

@app.route('/getID')
def giveCurrentID():
    #get current id
    with open(base_dir + "\\config.json", 'r') as configFile:
        config = json.load(configFile)
        currentID = config[0]["currentID"]
        
    #save new id
    with open(base_dir + "\\config.json", "w") as configFile:
        config[0]["currentID"] = config[0]["currentID"] + 1
        json.dump(config, configFile, indent=4)
        
    print("Current ID:", currentID)
    return str(currentID)
        
if __name__ == '__main__':
    app.run(debug=True, port=port)
