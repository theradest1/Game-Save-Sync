from flask import Flask, request, send_from_directory

app = Flask(__name__)
port = 3030
base_dir = "\\".join(__file__.split("\\")[0:-1])
save_dir = base_dir + "\\Saves"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    print(file.filename)
    file.save(file.filename)
    
    return 'File uploaded successfully!', 200

@app.route('/download/<saveID>')
def download_file(saveID):
    print("Client requested save with ID", saveID)
    # Replace 'file_to_send.txt' with the desired name of the file sent to the client
    return send_from_directory(save_dir, str(saveID) + ".zip", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=port)
