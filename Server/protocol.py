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
    }
}

_HASH = {
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


class ProtocolThread(Thread):

    def __init__(self, address, socket, logging):
        Thread.__init__(self)
        self.addr = address
        self.sock = socket
        self.logging = logging
        self._upstream = b""
        self._downstrem = b""
        self._book_hashed = False
        self._video_hashed = False

    def execute(self):
        # self._read()
        self.process_header()

    def process_header(self):
        message = repr(_REQUEST).encode(_ENCODING)
        self._upstream += message
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
        while True:
            data = self.sock.recv(_BUFFER_SIZE)
            print(f'+ --> [Server] Got {data} Request.')
            if data:
                if data.decode(_ENCODING) == 'BOOK':
                    print(f'+ --> [Server] Sending Book')
                    self._send_book()
                    break

                elif data.decode(_ENCODING) == 'VIDEO':
                    print(f'+ --> [Server] Sending Video')
                    self._send_video()
                    break

                elif data.decode(_ENCODING) == "HASH":
                    print(f'+ --> [Server] Sending Hash')
                    self._send_hash()
                
                else:
                    self.close()
                    break
            else:
                self.close()
                break

            self.logging.info(f'+ --> [Server] Content Delivered.')
            print(f'+ --> [Server] Content Delivered.')

    def _send_book(self):
        f = open(_BOOK_PATH, 'rb')
        while True:
            l = f.read(_BUFFER_SIZE)
            while (l):
                self.sock.send(l)
                l = f.read(_BUFFER_SIZE)
            if not l:
                f.close()
                self.close()
                break

    def _send_video(self):
        f = open(_VIDEO_PATH, 'rb')
        while True:
            l = f.read(_BUFFER_SIZE)
            while (l):
                self.sock.send(l)
                l = f.read(_BUFFER_SIZE)
            if not l:
                f.close()
                self.close()
                break

    def _send_hash(self):
        if not self._book_hashed:
            self.set_hash_Book()
        if not self._video_hashed:
            self.set_hash_Video()
        self.sock.send(repr(_HASH).encode(_ENCODING))
        #self.close()

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

    def _read(self):
        data = self.sock.recv(_BUFFER_SIZE)
        if data:
            print(data)
        else:
            self.process_header()

    '''
    HASH
    '''

    def set_hash_Book(self):
        hasher = hashlib.sha1()
        with open(_BOOK_PATH, 'rb') as af:
            buf = af.read()
            hasher.update(buf)
        _HASH["book"]["digested"] = repr(hasher.hexdigest())
        _HASH["book"]["size"], _HASH["book"]["block"] = hasher.digest_size, hasher.block_size
        self._book_hashed = True

    def set_hash_Video(self):
        hasher = hashlib.sha1()
        with open(_BOOK_PATH, 'rb') as af:
            buf = af.read()
            hasher.update(buf)
        _HASH["video"]["digested"] = repr(hasher.hexdigest())
        _HASH["video"]["size"], _HASH["video"]["block"] = hasher.digest_size, hasher.block_size
        self._video_hashed = True
