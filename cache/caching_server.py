import socket
from threading import Thread
import time
import os
import atexit

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
            if self.storage[key]['timestamp'] + self.storage[key]['ttl'] < time.time():
                self.delete(key)
                return False
            return True
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
                ttl = float(ttl)
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

    def save_to_file(self):
        with open('cache', 'wb') as file:
            for key, value in self.storage.items():
                if value['ttl'] == 0:
                    ttl = 0
                else:
                    if value['timestamp'] + value['ttl'] - time.time() < 0:
                        continue
                    ttl = value['ttl']
                set_value = value['value']
                timestamp = value['timestamp']
                line = f"{key}\r\n{set_value}\r\n{ttl}\r\n{timestamp};"
                line = line.encode('utf8')
                file.write(line)

    def load_file(self):
        with open('cache', 'rb') as file:
            commands = file.read().decode('utf8').split(';')[:-1]
            print(commands)
            for command in commands:
                key, value, ttl, timestamp = command.split('\r\n')
                print(key, value, ttl, timestamp)
                if float(ttl) == 0.0:
                    self.post(key, value, 0)
                    continue
                if time.time() > float(timestamp) + float(ttl):
                    continue
                self.post(key, value, float(timestamp) + float(ttl) - time.time())


storage = CacheStorage()
if os.path.exists('cache'):
    storage.load_file()


def exit_handler():
    storage.save_to_file()


atexit.register(exit_handler)


def new_connection(clientsocket, address):
    while True:
        data = clientsocket.recv(1024).decode('utf-8')
        if not data:
            break
        print(str(data))
        print(storage.deserialize(data))
        answer = storage.run_command(data)
        if answer is None:
            answer = "Done"
        else:
            answer = str(answer)
        clientsocket.send(answer.encode())

    clientsocket.close()


def cache_backup():
    while True:
        time.sleep(60)
        storage.save_to_file()
        print("Saved cache to file")


backup_thread = Thread(target=cache_backup)
backup_thread.daemon = True
backup_thread.start()

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
