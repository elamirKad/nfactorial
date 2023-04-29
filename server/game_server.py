import json
import socket
import time
from threading import Thread
from caching_client import CacheClient


cache_client = CacheClient()
cache_client.start()

client_sockets = {}


def new_connection(clientsocket, address):
    try:
        auth = clientsocket.recv(1024).decode('utf-8')
        print(auth)
        command, username, password = auth.split('\r\n')
        print(command, username, password)
        if command != "AUTH":
            print("QUIT")
            return
        result = cache_client.get(username)
        print(result, type(result))
        if result is None:
            cache_client.set(username, password)
            cache_client.set(f"{username}.record", 0)
            cache_client.set(f"{username}.score", 0)
            cache_client.set(f"{username}.state", 'None')
            client = [clientsocket, username, 0, 0, 'None']
        else:
            result = json.loads(result.replace("\'", "\""))['value']
            if result != password:
                clientsocket.close()
                return
            record = cache_client.get(f"{username}.record")
            record = json.loads(record.replace("\'", "\""))['value']
            print(record)
            if record is None:
                record = 0
            score = cache_client.get(f"{username}.score")
            score = json.loads(score.replace("\'", "\""))['value']
            if score is None:
                score = 0
            state = cache_client.get(f"{username}.state")
            state = json.loads(state.replace("\'", "\""))['value']
            if state == 'None' or state is None:
                state = 'None'
            client = [clientsocket, username, record, score, state]
        client_sockets[username] = client
        print(client_sockets)
        answer = f"AUTH\r\n{client[2]}\r\n{client[3]}\r\n{client[4]}"
        clientsocket.send(answer.encode())
    except Exception as e:
        print(e)
        clientsocket.close()
        return

    while True:
        data = clientsocket.recv(1024).decode('utf-8')
        print("\nResult:", data)
        if not data:
            break
        if data[:3] == "UPD":
            command, score, current_state = data.split('\r\n')
            cache_client.set(f"{username}.state", current_state)
            cache_client.set(f"{username}.score", score)
            if int(score) > int(client_sockets[username][2]):
                cache_client.set(f"{username}.record", score)
                client_sockets[username][2] = score
            client_sockets[username][3] = score
            client_sockets[username][4] = current_state
    client_sockets.pop(username)
    clientsocket.close()


def sending_stats():
    while True:
        time.sleep(2)
        stats = 'UPD\r\n' + ';'.join([str(x[1]) + ':' + str(x[3]) for x in client_sockets.values()])
        # print(stats)
        # print(client_sockets)
        try:
            for key, users in client_sockets.items():
                try:
                    users[0].send(stats.encode())
                except Exception as e:
                    print(e)
                    client_sockets.pop(key)
        except Exception as e:
            print(e)


stats_thread = Thread(target=sending_stats)
stats_thread.daemon = True
stats_thread.start()


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((socket.gethostname(), 2048))
serversocket.listen(30)
print("Waiting for connections...")
while True:
    (clientsocket, address) = serversocket.accept()
    print("Received connection from", clientsocket)
    conn = Thread(target=new_connection, args=(clientsocket, address))

    conn.start()


serversocket.close()
