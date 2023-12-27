from flask import Flask, request, send_from_directory
import json

app = Flask(__name__)
port = 3030
base_dir = "\\".join(__file__.split("\\")[0:-1])

#get save directory
with open(base_dir + "\\config.json", 'r') as configFile:
    config = json.load(configFile)
    save_dir = config["saveDir"]


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    print(file.filename)
    file.save(save_dir + "\\" + file.filename)
    
    return 'File uploaded successfully!', 200

@app.route('/download/<saveID>')
def download_file(saveID):
    print("Client requested save with ID", saveID)
    # Replace 'file_to_send.txt' with the desired name of the file sent to the client
    return send_from_directory(save_dir, str(saveID) + ".zip", as_attachment=True)

@app.route('/getID')
def giveCurrentID():
    #get current id
    with open(base_dir + "\\config.json", 'r') as configFile:
        config = json.load(configFile)
        currentID = config["currentID"]
        
    #save new id
    with open(base_dir + "\\config.json", "w") as configFile:
        config["currentID"] = config["currentID"] + 1
        json.dump(config, configFile, indent=4)
        
    print("Current ID:", currentID)
    return str(currentID)
        
if __name__ == '__main__':
    app.run(debug=True, port=port)
