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

        initialize_client(clientsocket, username, password)
        process_client_messages(clientsocket, username)
    except Exception as e:
        print(e)
        clientsocket.close()
        return


def initialize_client(clientsocket, username, password):
    print("check")
    result = cache_client.get(username)
    print(result, type(result))
    if result is None or result == '':
        create_new_client(clientsocket, username, password)
    else:
        load_existing_client(clientsocket, username, password, result)


def create_new_client(clientsocket, username, password):
    cache_client.set(username, password)
    cache_client.set(f"{username}.record", 0)
    cache_client.set(f"{username}.score", 0)
    cache_client.set(f"{username}.state", 'None')
    client = [clientsocket, username, 0, 0, 'None']
    client_sockets[username] = client
    print(client_sockets)
    send_auth_response(clientsocket, client)


def load_existing_client(clientsocket, username, password, result):
    stored_password = json.loads(result.replace("'", "\""))['value']
    if stored_password != password:
        clientsocket.close()
        return

    record, score, state = fetch_client_data(username)
    client = [clientsocket, username, record, score, state]
    client_sockets[username] = client
    print(client_sockets)
    send_auth_response(clientsocket, client)


def fetch_client_data(username):
    record = get_cached_value(f"{username}.record")
    score = get_cached_value(f"{username}.score")
    state = get_cached_value(f"{username}.state", default_value='None')

    return record, score, state


def get_cached_value(key, default_value=None):
    value = cache_client.get(key)
    if value is None:
        return default_value

    return json.loads(value.replace("'", "\""))['value']


def send_auth_response(clientsocket, client):
    answer = f"AUTH\r\n{client[2]}\r\n{client[3]}\r\n{client[4]}"
    clientsocket.send(answer.encode())


def process_client_messages(clientsocket, username):
    while True:
        data = clientsocket.recv(1024).decode('utf-8')
        print("\nResult:", data)
        if not data:
            break
        if data[:3] == "UPD":
            command, score, current_state = data.split('\r\n')
            update_client_data(username, score, current_state)

    client_sockets.pop(username)
    clientsocket.close()


def update_client_data(username, score, current_state):
    cache_client.set(f"{username}.state", current_state)
    cache_client.set(f"{username}.score", score)
    if int(score) > int(client_sockets[username][2]):
        cache_client.set(f"{username}.record", score)
        client_sockets[username][2] = score
    client_sockets[username][3] = score
    client_sockets[username][4] = current_state


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
serversocket.bind(('0.0.0.0', 2048))
serversocket.listen(30)
print("Waiting for connections...")
while True:
    (clientsocket, address) = serversocket.accept()
    print("Received connection from", clientsocket)
    conn = Thread(target=new_connection, args=(clientsocket, address))

    conn.start()


serversocket.close()
