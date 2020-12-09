import hashlib
import os

from google.cloud import storage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'mp4', 'gif'}
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

        return '', 204, headers
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    if 'file' not in request.files:
        return "Missing File", 400, headers

    file = request.files['file']
    if file.filename == '':
        return "Empty Filename", 400, headers

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_STORAGE_BUCKET)
        file_hash = hashlib.md5(file.read()).hexdigest()
        extension = filename.rsplit('.', 1)[1].lower()
        blob = bucket.blob(f'{file_hash}.{extension}')
        file.seek(0)
        blob.upload_from_file(file)
        return f'{file_hash}.out.{extension}', 200, headers