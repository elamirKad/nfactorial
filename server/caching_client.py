from threading import Thread
import socket

import select


class CacheClient(Thread):
    def __init__(self, port=6379):
        Thread.__init__(self)
        self.clientsocket = socket.socket()
        self.clientsocket.connect((socket.gethostname(), port))

    def run(self):
        while True:
            ready = select.select([self.clientsocket], [], [], 0.1)
            if ready[0]:
                data = self.clientsocket.recv(1024).decode()
                if data is None or data == ' ':
                    break
        self.clientsocket.close()

    def get(self, key):
        message = f"GET\r\n{key}\r\n\r\n"
        self.clientsocket.send(message.encode().decode('unicode_escape').encode("raw_unicode_escape"))
        data = self.clientsocket.recv(1024).decode()
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
