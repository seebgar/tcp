import os
from threading import Thread
import hashlib

'''
SERVER PROTOCOL
Request and Response Processing
'''

_BOOK_PATH = 'book100.pdf'
_VIDEO_PATH = 'video200.mp4'
_BUFFER_SIZE = 1024  # 4086
_ENCODING = "utf-8"

_REQUEST = {
    "book": {
        "name": "Programming Computer Vision with Python",
        "size": str(os.stat(_BOOK_PATH).st_size)
    },
    "video": {
        "name": "Closer - Lemaitre",
        "size": str(os.stat(_VIDEO_PATH).st_size)
    },
    "hash": {
        "algorithm": "sha224"
    }
}


class ProtocolThread(Thread):

    def __init__(self, address, socket, logging):
        Thread.__init__(self)
        self.addr = address
        self.sock = socket
        self.logging = logging
        self._upstream = b""
        self._downstrem = b""
        self.response_created = False

    def execute(self):
        #self._read()
        self.process_header()

    def _read(self):
        data = self.sock.recv(_BUFFER_SIZE)
        if data:
            print(data)
        else:
            self.process_header()

    def process_header(self):
        message = repr(_REQUEST).encode(_ENCODING)
        self._upstream += message
        self.response_created = True
        self._write()

    def _write(self):
        if self._upstream:
            try:
                sent = self.sock.send(self._upstream)
            except BlockingIOError:
                pass
            else:
                self._upstream = self._upstream[sent:]
        self.process_content()

    def process_content(self):
        data = self.sock.recv(_BUFFER_SIZE)
        print(f'+ --> [Server] Got {data} Request.')
        if data:
            if data.decode(_ENCODING) == 'BOOK':
                print(f'+ --> [Server] Sending Book')
                hasher = hashlib.sha224()
                f = open(_BOOK_PATH, 'rb')
                #buf = f.read()
                while True:
                    l = f.read(_BUFFER_SIZE)
                    while (l):
                        self.sock.send(l)
                        l = f.read(_BUFFER_SIZE)
                        hasher.update(l)
                    if not l:
                        f.close()
                        _REQUEST["hash"]["digested"] = repr(hasher.hexdigest())
                        _REQUEST["hash"]["size"], _REQUEST["hash"]["block"] =  str(hasher.digest_size), str(hasher.block_size)
                        self.sock.send(repr(_REQUEST.get("hash")).encode(_ENCODING))
                        _REQUEST["hash"] = { "algorith": "sha224" }
                        self.close()
                        break
            if data.decode(_ENCODING) == 'VIDEO':
                print(f'+ --> [Server] Sending Video')
                hasher = hashlib.sha1()
                f = open(_VIDEO_PATH, 'rb')
                buf = f.read()
                hasher.update(buf)
                while True:
                    l = f.read(_BUFFER_SIZE)
                    while (l):
                        self.sock.send(l)
                        l = f.read(_BUFFER_SIZE)
                    if not l:
                        f.close()
                        #_REQUEST["hash"]["digested"] = repr(hasher.digest())
                        _REQUEST["hash"]["size"], _REQUEST["hash"]["block"] =  str(hasher.digest_size), str(hasher.block_size)
                        self.sock.send(repr(_REQUEST.get("hash")).encode(_ENCODING))
                        self.close()
                        break
        self.logging.info(f'+ --> [Server] Content Delivered.')
        print(f'+ --> [Server] Content Delivered.')

    def close(self):
        try:
            self.sock.close()
        except OSError as e:
            self.logging.error(
                f'[Socket Close Error] --> self.sock.close() @ Thread {self.addr}\n{repr(e)}')
            print(
                f'[Socket Close Error] --> self.sock.close() @ Thread {self.addr}\n{repr(e)}')
        finally:
            self.sock = None

    '''
    HASH
    '''

    def set_hash_Book(self):
        hasher = hashlib.sha1()
        with open(_BOOK_PATH, 'rb') as af:
            buf = af.read()
            hasher.update(buf)
        _REQUEST["hash"]["digested"] = hasher.digest()
        _REQUEST["hash"]["size"], _REQUEST["hash"]["block"] =  hasher.digest_size, hasher.block_size
        print(_REQUEST)

    def set_hash_Video(self):
        hasher = hashlib.sha1()
        with open(_VIDEO_PATH, 'rb') as af:
            buf = af.read()
            hasher.update(buf)
        _REQUEST["hash"]["digested"] = hasher.hexdigest()
