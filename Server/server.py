import socket
from socketserver import ThreadingMixIn
import logging
from datetime import date
from datetime import datetime
from protocol import ProtocolThread

'''
SERVER PROCESS
'''

# _HOST = socket.gethostbyaddr("<your-ec2-public_ip>")[0] #  --> AMAZON EC2 IP
_HOST = 'localhost'
_PORT = 65439
_MAX_CONNECTIONS = 25

# TODO el envio de archivos solo se realiza cuando el numero definido de Clientes están CONECTADOS

# TODO Definir un tiempo en el cual el servidor bloquee la comunicación con un cliente si en ese tiempo determinado no ha hecho ninguna petición. Explique por qué es importante definir ese tiempo


if __name__ == "__main__":
    logging.basicConfig(filename='.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
    cad = f'\n\n{date.today().strftime("%B %d, %Y")} - {datetime.now().strftime("%H:%M:%S")}\n'
    logging.info(cad)

    TCP_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCP_Sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCP_Sock.bind((_HOST, _PORT))
    threads = []

    try:
        while True:
            TCP_Sock.listen(_MAX_CONNECTIONS)
            logging.info(f'--> Listening on {_HOST}:{_PORT}')
            print(f'--> Listening on {_HOST}:{_PORT}')
            connection, address = TCP_Sock.accept()
            logging.info(
                f'+ --> [Server] Connection Established with Client {address}')
            print(f'+ --> [Server] Connection Established with Client {address}')
            new_thread = ProtocolThread(address, connection)
            new_thread.execute()
            threads.append(new_thread)
        
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n--> [Server End] Caught Keyboard Interrupt.\n--> Exiting\n ")
    

    
