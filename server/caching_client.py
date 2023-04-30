import socket


class CacheClient():
    def __init__(self, port=6379):
        self.clientsocket = socket.socket()
        self.port = port

    def run(self):
        self.clientsocket.connect(('localhost', self.port))

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

    def stop(self):
        self.clientsocket.close()
