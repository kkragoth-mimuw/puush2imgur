import time
import yaml
import sys
import os
import pyimgur
import argparse

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# You can insert imgur api secrets here
# or set them as env var - IMGUR_ID and IMGUR_SECRET
# or set them in secrets.yaml
client_id = ''
client_secret = ''


home = os.path.expanduser("~")
path = os.path.join(home, 'Pictures')


def show_notification(msg):
    if sys.platform == "linux" or sys.platform == "linux2":
        os.system('notify-send -t 3 puush2imgur: ' + msg)
    else:
        print('puush2imgur: ' + msg)


def upload_photo(client, path):
    print("Upload photo initialized: {0}".format(path))
    try:
        uploaded_image = client.upload_image(path, title="Uploaded with script")
    except Exception as e:
        show_notification("[failed]" + str(e))
        return

    show_notification(uploaded_image.link)


class PuushEventHandler(FileSystemEventHandler):
    def __init__(self, client):
        self.client = client

    def on_created(self, event):
        upload_photo(self.client, event.src_path)


def get_secret_credentials():
    global client_id
    global client_secret

    try:
        with open('secrets.yaml', 'r') as stream:
            try:
                cfg = yaml.load(stream)
                client_id = cfg['client_id']
                client_secret = cfg['client_secret']

            except yaml.YAMLError as exc:
                exit(exc)
    except FileNotFoundError:
        exit("Please insert imgur api credentials")


def main():
    global client_id
    global client_secret
    global path

    client_id = os.environ.get("IMGUR_ID")
    client_secret = os.environ.get("IMGUR_SECRET")

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path')
    parser.add_argument('-i', '--client_id')
    parser.add_argument('-s', '--client_secret')
    args = parser.parse_args()

    if args.path:
        path = os.path.expanduser(args.path)

    if args.client_id:
        client_id = args.client_id

    if args.client_secret:
        client_secret = args.client_secret

    if client_id is None and client_secret is None:
        get_secret_credentials()

    imgur_client = pyimgur.Imgur(client_id)
    observer = Observer()
    event_handler = PuushEventHandler(imgur_client)
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()