#!/usr/bin/env python

#!/usr/bin/env python

import socket

from protocol import Protocol

'''
CLIENT PROCESS
Request and Response Processing
'''

# _HOST = "<your-ec2-public_ip>"
_HOST = 'localhost'
_PORT = 65439
_REQUEST = "VIDEO"  # "BOOK" || "VIDEO"


def ejecutar():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((_HOST, _PORT))

        client = Protocol((_HOST, _PORT), sock, _REQUEST)
        client.execute()
    except KeyboardInterrupt:
        print("\n--> [Client End] Caught Keyboard Interrupt.\n--> Exiting\n ")

        

if __name__ == "__main__":
    ejecutar()



