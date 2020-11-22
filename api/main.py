import os
from werkzeug.utils import secure_filename
from google.cloud import storage
import redis
import hashlib
ALLOWED_EXTENSIONS = {'mp4', 'gif'}
REDIS_HOST = os.environ.get('REDISHOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDISPORT', 6379))
GCP_STORAGE_BUCKET = os.environ.get('GCP_STORAGE_BUCKET')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload(request):
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    if 'file' not in request.files:
        return ("Missing File", 400, headers)

    file = request.files['file']
    if file.filename == '':
        return ("Empty Filename", 400, headers)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_STORAGE_BUCKET)
        hash = hashlib.md5(file.read()).hexdigest()
        extension = filename.rsplit('.', 1)[1].lower()
        blob = bucket.blob(f'{hash}.{extension}')
        file.seek(0)
        blob.upload_from_file(file)
        redis_name_to_hash = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1)
        redis_hash_to_name = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=2)
        redis_name_to_hash.set(filename,hash)
        redis_hash_to_name.set(hash,filename)
        return ("Uploaded File", 200, headers)