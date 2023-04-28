import socket

clientsocket = socket.socket()
clientsocket.connect((socket.gethostname(), 6379))
print(socket.gethostname())
while True:
    message = input("Input: ")
    if not message:
        break
    clientsocket.send(message.encode())
    data = clientsocket.recv(1024).decode()
    print(data)

clientsocket.close()
