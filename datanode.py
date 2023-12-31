#distributed database
import os

# Assert that the folder files exists
if os.path.isdir("files"):
    pass
elif os.path.exists("files"):
    print("ERROR: 'files' FOLDER COULD NOT BE CREATED BECAUSE A FILE EXISTS WITH THE SAME NAME")
    exit(1)
else:
    os.makedirs("files")

import rpyc

monitor = rpyc.connect_by_service("Monitor").root
PORT = 8090
monitor.register(PORT)

class FileProxy():
    def __init__(self, path, arg):
        self.file_descriptor = open(path, arg)
    def write(self, data):
        self.file_descriptor.write(data)
    def close(self):
        self.file_descriptor.close()

class DatanodeService(rpyc.Service):
    def on_connect(self, conn):
        pass
    def on_disconnect(self, conn):
        pass

    def exposed_file(self, id):
        return file(id)

    def exposed_delete(self, id):
        return delete(id)

    def exposed_upload(self, id, chunk_generator):
        return upload(id, chunk_generator)

    def exposed_getWriteFileProxy(self, id):
        print("Getting Write File Proxy {}".format(id))
        return FileProxy("files/{}".format(id), "wb")

def file(id):
    print("Downloading {}".format(id))
    file = open("files/{}".format(id), "rb")
    while True:
        chunk = file.read(2**20)
        if not chunk:
            break
        yield chunk
    file.close()

def delete(id):
    print("Removing {}".format(id))
    os.remove("files/{}".format(id))

def upload(id, chunk_generator):
    print("Uploading {}".format(id))

    file = open("files/{}".format(id), "wb")
    for chunk in chunk_generator:
        file.write(chunk)
    file.close()

    return id


import threading
import time

def periodicallyPingMonitor():
    while True:
        monitor.ping(PORT)
        time.sleep(7)


# Initialize remote object server and register it to name service
if __name__ == "__main__":
    periodicallyPingMonitorThread = threading.Thread(target=periodicallyPingMonitor)
    periodicallyPingMonitorThread.start()

    from rpyc.utils.server import ThreadedServer

    t = ThreadedServer(DatanodeService, port=PORT, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
