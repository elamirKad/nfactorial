import socket
import time
from threading import Thread


def print_stats(clientsocket):
    while True:
        try:
            stats = clientsocket.recv(1024).decode()
            command, stats = stats.split('\r\n')
            print(stats.split(';'))
        except:
            pass


def send_data(clientsocket):
    clientsocket.send('AUTH\r\nelsddddddakmk\r\nelamir'.encode().decode('unicode_escape').encode("raw_unicode_escape"))
    while True:
        time.sleep(2)
        send = 'UPD\r\n104\r\n[[0,0,0],[0,0,0],[0,0,0]]'
        clientsocket.send(send.encode().decode('unicode_escape').encode("raw_unicode_escape"))
        time.sleep(2)
        send = 'UPD\r\n2048\r\n[[0,0,2],[0,0,0],[0,0,0]]'
        clientsocket.send(send.encode().decode('unicode_escape').encode("raw_unicode_escape"))


clientsocket = socket.socket()
clientsocket.connect((socket.gethostname(), 2048))

stats_thread = Thread(target=print_stats, args=(clientsocket,))
stats_thread.daemon = True
stats_thread.start()

send_thread = Thread(target=send_data, args=(clientsocket,))
send_thread.daemon = True
send_thread.start()

while True:
    data = clientsocket.recv(1024).decode()
    if not data:
        break
    print(data)
clientsocket.close()
