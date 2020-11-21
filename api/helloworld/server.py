import os
from flask import Flask, flash, request, redirect, url_for, Response
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:/Users/dansp/projects/smoothr/api/videos'
ALLOWED_EXTENSIONS = {'mp4', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return Response(response="Missing File", status=400)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return Response(response="Empty Filename", status=400)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return Response(response="Received File", status=200)

app.run(host="0.0.0.0", port=5000)