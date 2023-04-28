import socket
from threading import Thread

'''
Custom Caching Protocol
{COMMAND}\r\n{KEY}\r\n{VALUE:optional}\r\n{TTL}
COMMAND: GET, SET, UPD, DEL
TTL - time to live (default=0)
Use ';' for separating 
'''


class CacheStorage:
    def __init__(self):
        self.storage = {}

    @classmethod
    def deserialize(cls, message):
        return message.split('\r\n')

    @classmethod
    def serialize(cls, command, key, value='', ttl=0):
        return f"{command}\r\n{key}\r\n{value}\r\n{ttl}"


# call = "SET\r\nlol\r\n\r\n0"
# result = CacheStorage.deserialize(call)
# print(result)
# print(CacheStorage.serialize(*result))


def new_connection(clientsocket, address):
    while True:
        data = clientsocket.recv(1024).decode()
        if not data:
            break
        print(str(data))
        clientsocket.send("success!".encode())

    clientsocket.close()


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((socket.gethostname(), 6379))
serversocket.listen(5)
print("Waiting for connections...")

while True:
    (clientsocket, address) = serversocket.accept()
    print("Received connection from", clientsocket)
    conn = Thread(target=new_connection, args=(clientsocket, address))

    conn.start()


serversocket.close()
