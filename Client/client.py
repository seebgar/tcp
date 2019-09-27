#!/usr/bin/env python

#!/usr/bin/env python

import socket
import time
import logging
from datetime import date
from datetime import datetime
import sys
import json
import hashlib

'''
CLIENT PROCESS
Request and Response Processing
'''

# _HOST = "<your-ec2-public_ip>"
_HOST = 'localhost'
_PORT = 65439
_BUFFER_SIZE = 1024
_BOOK_PATH = "new_Book.pdf"
_VIDEO_PATH = "new_Video.txt"
_ENCODING = "utf-8"
_DIGESTED = ""
_HASH_SIZE = 0
_HASH_BLOCKS = 0



if __name__ == "__main__":

    logging.basicConfig(filename='logs.log', filemode='a',
                        format='%(name)s - %(levelname)s - %(message)s')
    logging.info(
        f'{date.today().strftime("%B %d, %Y")} - {datetime.now().strftime("%H:%M:%S")}\n')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((_HOST, _PORT))

    logging.info(
        f'\n\n* --> [Client] Connection Established with Server {_HOST}:{_PORT}')
    print(f'* --> [Client] Connection Established with Server {_HOST}:{_PORT}')
    start = time.time()

    data = sock.recv(_BUFFER_SIZE)

    if data:
        print(data)
        formatted = json.loads(data.decode(_ENCODING).replace("'", '"'))
        print(json.dumps(formatted, indent=4, sort_keys=True))

        _book_size = formatted.get("book").get("size")
        _video_size = formatted.get("video").get("size")
        _hash_algorithm = formatted.get("hash").get("algorithm")

        request = "BOOK"
        sock.sendall(request.encode(_ENCODING))

        received = 0
        with open(_BOOK_PATH, 'wb') as f:
            while True:
                data = sock.recv(_BUFFER_SIZE)
                received += len(data)
                porcent = (received / float(_book_size)) * 100
                #if porcent > 90: print("* --> [Client] Downloading {0:.2f} %".format(porcent))
                if porcent >= 100:
                    f.close()
                    break
                f.write(data)
    print("* --> [Client] Finished Downloading")


    if data:
        data = data.decode(_ENCODING).split("\n")
        print(data[-1:])
        # data = data[-1:].replace('"', '*').replace("*", "").replace("'", '"' )
        # formatted = json.loads(data)

        # _hash_digested = formatted.get("digested")
        # _hash_size = formatted.get("size")
        # _hash_blocks = formatted.get("block")

    
    hasher = hashlib.sha224()
    with open(_BOOK_PATH, 'rb') as af:
        buf = af.read()
        hasher.update(buf)
    _DIGESTED = hasher.hexdigest()
    _HASH_SIZE = hasher.digest_size
    _HASH_BLOCKS = hasher.block_size
    print(_DIGESTED, _HASH_SIZE, _HASH_BLOCKS)

    # if _hash_digested == _DIGESTED:
    #     print(
    #         f"* --> [Client] File arrived completely and without modificcations. Hash Original \n{_hash_digested} \nVS\n{_DIGESTED}")
    # else:
    #     print(
    #         f"* --> [Client] File did not arrive completely and without modificcations. Hash Original \n{_hash_digested} \nVS\n{_DIGESTED}")


    end = time.time()
    elapsed = end - start

    logging.info(f'* --> [Client] Connection finished.')
    print(
        '* --> [Client] Connection finished. Elapsed Time:\n{0:0.6f} seconds\n\n'.format(elapsed))
