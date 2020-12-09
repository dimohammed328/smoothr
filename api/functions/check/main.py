import os

from google.cloud import storage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'mp4'}
GCP_STORAGE_BUCKET = os.environ.get('GCP_STORAGE_BUCKET')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check(request):
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '3600'
        }

        return '', 204, headers
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    args = request.args
    if 'file' not in args:
        return 'Missing File', 400, headers
    file = args['file']
    if allowed_file(file):
        filename = secure_filename(file)
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_STORAGE_BUCKET)
        blob = bucket.get_blob(filename)
        if not blob:
            return "Not Found", 404, headers
        else:
            return blob.public_url, 200, headers
