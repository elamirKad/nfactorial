from threading import Thread
import socket

import select


class CacheClient(Thread):
    def __init__(self, port=6379):
        Thread.__init__(self)
        self.clientsocket = socket.socket()
        self.clientsocket.connect(('localhost', port))

    def run(self):
        while True:
            pass
        self.clientsocket.close()

    def get(self, key):
        message = f"GET\r\n{key}\r\n\r\n"
        self.clientsocket.send(message.encode().decode('unicode_escape').encode("raw_unicode_escape"))
        data = self.clientsocket.recv(1024).decode()
        print("Client:", data)
        if data == "Done":
            return None
        return data

    def set(self, key, value, ttl=0):
        message = f"SET\r\n{key}\r\n{value}\r\n{ttl}"
        self.clientsocket.send(message.encode().decode('unicode_escape').encode("raw_unicode_escape"))
        data = self.clientsocket.recv(1024).decode()
        return data

    def delete(self, key):
        message = f"DEL\r\n{key}\r\n\r\n"
        self.clientsocket.send(message.encode().decode('unicode_escape').encode("raw_unicode_escape"))
        data = self.clientsocket.recv(1024).decode()
        return data
