import time
import json
import hashlib
import logging
import time
from datetime import date
from datetime import datetime
import json
import hashlib

'''
CLIENT PROTOCOLO
Request and Response Processing
'''

_BUFFER_SIZE = 1024
_ENCODING = "utf-8"
_BOOK_PATH = "new_Book.pdf"
_VIDEO_PATH = "new_Video.mp4"


class Protocol():

    def __init__(self, address, socket, request):
        logging.basicConfig(
            filename='.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info(
            f'\n\n{date.today().strftime("%B %d, %Y")} - {datetime.now().strftime("%H:%M:%S")}\n')
        self.addr = address
        self.sock = socket
        self.req = request
        self.start = None
        self.end = None
        self._server_files = {}
        self._request = ''
        self._server_hash = {}
        self._hash = {
            "algorithm": "sha224",
            "book": {
                "digested": '0',
                "size": '0',
                "block": '0'
            },
            "video": {
                "digested": '0',
                "size": '0',
                "block": '0'
            }
        }

    def execute(self):
        print(f'\n--> [Client] Connection Established with Server {self.addr}')
        logging.info(
            f'\n--> [Client] Connection Established with Server {self.addr}')
        self.start = time.time()
        self._read()

    def _read(self):
        data = self.sock.recv(_BUFFER_SIZE)
        if data:
            formatted = json.loads(data.decode(
                _ENCODING).replace('"', "").replace("'", '"'))
            self._server_files = formatted
            # prints JSON server files object
            #print(json.dumps(self._server_files, indent=4, sort_keys=True))
            self.request_hash()
            self.process_download(self.req)

    def request_hash(self):
        self._request = "HASH"
        self.sock.sendall(self._request.encode(_ENCODING))
        data = self.sock.recv(_BUFFER_SIZE)
        if data:
            formatted = json.loads(data.decode(
                _ENCODING).replace('"', "").replace("'", '"'))
            self._server_hash = formatted
            # prints JSON server hash object
            #print(json.dumps(self._server_hash, indent=4, sort_keys=True))

    def process_download(self, req):
        file_path = ''
        if req == "BOOK":
            file_path = _BOOK_PATH
        else:
            file_path = _VIDEO_PATH

        self._request = req
        self.sock.sendall(self._request.encode(_ENCODING))
        data_recieved = 0

        with open(file_path, 'wb') as f:
            while True:
                data = self.sock.recv(_BUFFER_SIZE)
                if not data:
                    f.close()
                    break

                data_recieved += len(data)
                f.write(data)

                #downloaded_percent = (data_recieved / float(self._server_files["book"]["size"])) * 100
                #print("* --> [Client] Downloading {0:.2f} %".format(downloaded_percent))
        print("* --> [Client] Finished Downloading")
        logging.info("* --> [Client] Finished Downloading")
        # self.close()
        self.process_hash(_BOOK_PATH, req)

    def process_hash(self, file_path, req):
        # self.request_hash()
        hasher = hashlib.sha1()
        with open(file_path, 'rb') as af:
            buf = af.read()
            hasher.update(buf)

        self._request = req
        if self._request == "BOOK":
            self._hash["book"]["digested"] = repr(hasher.hexdigest())
            self._hash["book"]["size"], self._hash["book"]["block"] = hasher.digest_size, hasher.block_size

            if self._hash.get("book").get("digest") == self._server_hash.get("book").get("digest"):
                cad = '* --> [Client] File downloaded completely and without modifications'
                print(cad)
                logging.info(cad)
                json_local = f'* --> [Cliente] Hash {json.dumps(self._hash, indent=4, sort_keys=True)}'
                json_server = f'* --> [Cliente] Server Hash {json.dumps(self._server_hash, indent=4, sort_keys=True)}'
                logging.info(json_local)
                logging.info(json_server)
            else:
                cad = "* --> [Client] The downloaded file is different from the Server's original"
                print(cad)
                logging.info(cad)
                json_local = f'* --> [Cliente] Hash {json.dumps(self._hash, indent=4, sort_keys=True)}'
                json_server = f'* --> [Cliente] Server Hash {json.dumps(self._server_hash, indent=4, sort_keys=True)}'
                print(json_local)
                print(json_server)
                logging.info(json_local)
                logging.info(json_server)
        else:
            self._hash["video"]["digested"] = repr(hasher.hexdigest())
            self._hash["video"]["size"], self._hash["video"]["block"] = hasher.digest_size, hasher.block_size

            if self._hash.get("video").get("digest") == self._server_hash.get("video").get("digest"):
                cad = '* --> [Client] File downloaded completely and without modifications'
                print(cad)
                logging.info(cad)
                json_local = f'* --> [Cliente] Hash {json.dumps(self._hash, indent=4, sort_keys=True)}'
                json_server = f'* --> [Cliente] Server Hash {json.dumps(self._server_hash, indent=4, sort_keys=True)}'
                logging.info(json_local)
                logging.info(json_server)
            else:
                cad = "* --> [Client] The downloaded file is different from the Server's original"
                print(cad)
                logging.info(cad)
                json_local = f'* --> [Cliente] Hash {json.dumps(self._hash, indent=4, sort_keys=True)}'
                json_server = f'* --> [Cliente] Server Hash {json.dumps(self._server_hash, indent=4, sort_keys=True)}'
                print(json_local)
                print(json_server)
                logging.info(json_local)
                logging.info(json_server)

        self.close()

    def close(self):
        try:
            self.sock.close()
            self.end = time.time()

            elapsed = self.end - self.start
            cad = '* --> [Client] Connection Elapsed Time:\n* --> {0:0.6f} seconds'.format(
                elapsed)
            print(cad)
            logging.info(cad)
            cad = '--> [Client] Connection finished\n'
            print(cad)
            logging.info(cad)

        except OSError as e:
            logging.error(
                f'[Socket Close Error] --> self.sock.close() @ Thread {self.addr}\n{repr(e)}')
            print(
                f'[Socket Close Error] --> self.sock.close() @ Thread {self.addr}\n{repr(e)}')
        finally:
            self.sock = None
