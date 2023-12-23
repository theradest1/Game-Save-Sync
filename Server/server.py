from flask import Flask, request

app = Flask(__name__)
port = 3030

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    # Here, you can specify where and how to save the file
    # For example, to save in the current directory with the same name:
    print(file.filename)
    file.save(file.filename)
    
    return 'File uploaded successfully!', 200

if __name__ == '__main__':
    app.run(debug=True, port=port)
