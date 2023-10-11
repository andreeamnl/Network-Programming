import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

server_rooms = {}
server_clients = []


def client_handler(client_socket, client_address):

    print(f'Connection from {client_address}')

    while True:
        client_message = client_socket.recv(1024).decode('utf-8')

        if not client_message:
            break

        print(f'Message: {client_message}, from {client_address} ')

        message = json.loads(client_message)

        if message['type'] == 'connect':
            room_name = message['payload']['room']
            if room_name not in server_rooms:
                server_rooms[room_name] = [client_socket]
            else:
                server_rooms[room_name].append(client_socket)

            for client in server_rooms[message['payload']['room']]:
                resp = {
                    "type": "connection",
                    "payload": {
                        "message": f"Client {message['payload']['name']} has been connected "
                                   f"to the {message['payload']['room']}."
                    }
                }
                client.send(json.dumps(resp).encode('utf-8'))
        elif message['type'] == 'message':
            for client in server_rooms[message['payload']['room']]:
                notification = {
                    "type": "notification",
                    "payload": {
                        "text": message['payload']['text']
                    }
                }

                client.send(json.dumps(notification).encode('utf-8'))

    server_clients.remove(client_socket)
    client_socket.close()


while True:
    client_socket, client_address = server_socket.accept()
    server_clients.append(client_socket)
    client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
    client_thread.start()

