import os
from flask import Flask, request, Response
from werkzeug.utils import secure_filename
from google.cloud import storage
import redis
import hashlib
ALLOWED_EXTENSIONS = {'mp4', 'gif'}
REDIS_HOST = os.environ.get('REDISHOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDISPORT', 6379))
GCP_STORAGE_BUCKET = os.environ.get('GCP_STORAGE_BUCKET')

print("Env Variables:")
print("REDIS_HOST", REDIS_HOST)
print("REDIS_PORT", REDIS_PORT)
print("GCP_STORAGE_BUCKET", GCP_STORAGE_BUCKET)

app = Flask(__name__)
def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return Response(response="Missing File", status=400)
    file = request.files['file']
    if file.filename == '':
        return Response(response="Empty Filename", status=400)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_STORAGE_BUCKET)
        hash = hashlib.md5(file.read()).hexdigest()
        extension = filename.rsplit('.', 1)[1].lower()
        blob = bucket.blob('.'.join([hash,extension]))
        file.seek(0)
        blob.upload_from_file(file)
        redis_name_to_hash = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1)
        redis_hash_to_name = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=2)
        redis_name_to_hash.set(filename,hash)
        redis_hash_to_name.set(hash,filename)
        return Response(response="Uploaded File", status=200)
app.run(host="0.0.0.0", port=5000)