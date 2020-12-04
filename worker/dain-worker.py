import contextlib
import json
import subprocess
import threading
import time
from pathlib import Path
from subprocess import CalledProcessError

from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud.pubsub_v1.subscriber.message import Message

PROJECT_ID = "graphical-envoy-287420"

PUBSUB_SUBSCRIPTION = "dain-worker"

INPUT_BUCKET = "fpsaas-inputs"
OUTPUT_BUCKET = "fpsaas-outputs"


# Adapted from https://stackoverflow.com/a/40965385
class MessageKeepAlive(contextlib.AbstractContextManager):
    def __init__(self, *, interval: int, message: Message):
        self._timer = None
        self.interval = interval
        self.message = message
        self.is_running = False
        self.next_call = time.time()

    def _run(self) -> None:
        self.is_running = False
        self._start()
        self.message.modify_ack_deadline(600)

    def _start(self) -> None:
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def _stop(self) -> None:
        self._timer.cancel()
        self.is_running = False

    def __enter__(self):
        self._start()

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop()


def download_input(input_name: str) -> None:
    storage_client = storage.Client()
    input_bucket = storage_client.bucket(INPUT_BUCKET)

    input_blob = input_bucket.get_blob(input_name)
    input_blob.download_to_filename(input_name)


def upload_result(output_name: str, input_name: str) -> None:
    storage_client = storage.Client()

    input_bucket = storage_client.bucket(INPUT_BUCKET)
    output_bucket = storage_client.bucket(OUTPUT_BUCKET)

    result_blob = output_bucket.blob(output_name)
    result_blob.upload_from_filename(output_name)

    original_blob = input_bucket.get_blob(input_name)

    # Update the input file's metadata to include the output download URL
    new_metadata = original_blob.metadata or {}
    new_metadata["result"] = result_blob.public_url

    original_blob.metadata = new_metadata
    original_blob.patch()


def process_message(message: Message) -> None:
    message_data = json.loads(message.data.decode())

    # Keep the message alive while we are processing it
    with MessageKeepAlive(message=message, interval=570):
        input_file = Path(f"./{message_data['name']}")
        output_file = Path(f"./{input_file.name}").with_suffix(".out.mp4")

        # Download the user's input video
        download_input(input_file.name)

        # Process the video with DAIN
        try:
            subprocess.check_call([
                "/usr/bin/python3",
                "run.py",
                "-i", input_file.name,
                "-o", output_file.name,
                "-ot", "video",
                "-a", "DAIN",
                "-pt", "60fps",
                "-net", "DAIN",
            ])
        # If the video can't be processed put the message back in the queue
        except CalledProcessError:
            message.nack()
            return

        # Upload the result
        upload_result(output_file.name, input_file.name)

        # Delete the temporary input/outputs
        input_file.unlink()
        output_file.unlink()

    # Acknowledge the message - we're done processing
    message.ack()


def main():
    subscriber_client = pubsub_v1.SubscriberClient()

    sub_path = subscriber_client.subscription_path(PROJECT_ID, PUBSUB_SUBSCRIPTION)

    # We can only process one message at a time to avoid running out of GPU memory
    flow_control = pubsub_v1.types.FlowControl(max_messages=1)

    future = subscriber_client.subscribe(sub_path, process_message, flow_control=flow_control)

    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()


if __name__ == '__main__':
    main()
