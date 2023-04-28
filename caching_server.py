import socket
from threading import Thread


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
