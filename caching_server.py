import socket
from threading import Thread
import time

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

    def check_ttl(self, key):
        try:
            if self.storage[key]['ttl'] == 0:
                return True
            self.delete(key)
            return self.storage[key]['timestamp'] + self.storage[key]['ttl'] > time.time()
        except:
            return False

    def get(self, key):
        if self.check_ttl(key):
            return self.storage[key]
        return None

    def post(self, key, value, ttl):
        self.storage[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }

    def delete(self, key):
        self.storage.pop(key)

    def run_command(self, message):
        try:
            command, key, value, ttl = self.deserialize(message)
            try:
                ttl = int(ttl)
            except:
                pass
            if command == 'GET':
                return self.get(key)
            elif command == 'SET':
                self.post(key, value, ttl)
            elif command == 'UPD':
                pass
            elif command == 'DEL':
                self.delete(key)
            return None
        except:
            return None


# call = "SET\r\nlol\r\nkek\r\n1"
# result = CacheStorage.deserialize(call)
# print(result)
# print(CacheStorage.serialize(*result))
# storage = CacheStorage()
# print(storage.run_command(call))
# call = "GET\r\nlol\r\n\r\n"
# time.sleep(2)
# print(storage.run_command(call))
# print(storage.storage)


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
