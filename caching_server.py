import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind((socket.gethostname(), 6379))

serversocket.listen(2)
print("Waiting for connections...")
(clientsocket, address) = serversocket.accept()
print("Received connection from", clientsocket)
while True:
    data = clientsocket.recv(1024).decode()
    if not data:
        break
    print(str(data))
    clientsocket.send("success!".encode())

clientsocket.close()
