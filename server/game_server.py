import socket

clientsocket = socket.socket()
clientsocket.connect((socket.gethostname(), 6379))
print(socket.gethostname())
while True:
    message = input("Input: ")
    print(message.encode().decode('unicode_escape').encode("raw_unicode_escape"))
    if not message:
        break
    clientsocket.send(message.encode().decode('unicode_escape').encode("raw_unicode_escape"))
    data = clientsocket.recv(1024).decode()
    print(data)

clientsocket.close()
