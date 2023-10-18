import socket
import threading
import json
import os

HOST = '127.0.0.1'
PORT = 1117
MEDIA_FOLDER = 'server_media'
CLIENTS = {}
ROOMS = {}

def start_server():
    server_socket = create_server_socket()
    accept_connections(server_socket)

def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f'Server is listening on {HOST}:{PORT}')
    return server_socket

def accept_connections(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        CLIENTS[client_socket] = {'address': client_address}
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def handle_client(client_socket):
    client_address = CLIENTS[client_socket]['address']
    print(f'Accepted connection from {client_address}')

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        data = json.loads(message)
        handle_message(client_socket, data)

def handle_message(client_socket, data):
    message_type = data.get('type', '')

    if message_type == 'connect':
        handle_connect(client_socket, data)
    elif message_type == 'disconnect':
        handle_disconnect(client_socket, data)
    elif message_type == 'upload':
        handle_upload(client_socket, data)
    elif message_type == 'download':
        handle_download(client_socket, data)
    elif message_type == 'message':
        handle_message_broadcast(client_socket, data)
    else:
        print(f'\nInvalid client message received: {data}')

def handle_connect(client_socket, data):
    acknowledge_message = {
        "type": "connect_ack",
        "payload": {
            "message": f"\nYou successfully connected to the room '{data['payload']['room']}'."
        }
    }
    server_data = json.dumps(acknowledge_message)
    client_socket.send(bytes(server_data, encoding='utf-8'))

    room = data['payload']['room']
    if room not in ROOMS:
        ROOMS[room] = set()

    ROOMS[room].add(client_socket)

    if len(CLIENTS) > 1:
        notification_message = {
            "type": "notification",
            "payload": {
                "message": f"{data['payload']['name']} has joined the room.\n"
            }
        }
        server_data = json.dumps(notification_message)
        send_broadcast_message(client_socket, CLIENTS, ROOMS, bytes(server_data, encoding='utf-8'))

def handle_disconnect(client_socket, data):
    CLIENTS.pop(client_socket, None)

    if len(CLIENTS) != 0:
        notification_message = {
            "type": "notification",
            "payload": {
                "message": f"{data['payload']['name']} left the room.\n"
            }
        }
        server_data = json.dumps(notification_message)
        send_broadcast_message(client_socket, CLIENTS, ROOMS, bytes(server_data, encoding='utf-8'))

    for room in ROOMS:
        if room == data['payload']['room']:
            ROOMS[room].discard(client_socket)
            break

def handle_upload(client_socket, data):
    room = data['payload']['room']
    file_name = data['payload']['file_name']
    file_size = data['payload']['file_size']
    file_path = os.path.join(MEDIA_FOLDER, room, file_name)

    if not os.path.isdir(os.path.join(MEDIA_FOLDER, room)):
        os.makedirs(os.path.join(MEDIA_FOLDER, room))

    with open(file_path, 'wb') as file:
        while file_size > 0:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            file.write(chunk)
            file_size -= len(chunk)

    notification_message = {
        "type": "notification",
        "payload": {
            "message": f"{data['payload']['name']} uploaded the {file_name} file.\n"
        }
    }
    server_data = json.dumps(notification_message)
    send_broadcast_message(client_socket, CLIENTS, ROOMS, bytes(server_data, encoding='utf-8'))

def handle_download(client_socket, data):
    file_path = f"{MEDIA_FOLDER}/{data['payload']['room']}/{data['payload']['file_name']}"
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        

        stream_message = {
            "type": "download-ack",
            "payload": {
                "file_name": data['payload']['file_name'],
                "file_size": file_size
            }
        }
        server_data = json.dumps(stream_message)
        client_socket.sendall(bytes(server_data, encoding='utf-8'))

        if file_size > 1024:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
        else:
            with open(file_path, 'rb') as file:
                chunk = file.read(file_size)
                client_socket.sendall(chunk)
    else:
        notification_message = {
            "type": "notification",
            "payload": {
                "message": f"The file {data['payload']['file_name']} does not exist.\n"
            }
        }
        server_data = json.dumps(notification_message)
        client_socket.sendall(bytes(server_data, encoding='utf-8'))

def handle_message_broadcast(client_socket, data):
    room = data['payload']['room']
    sender = data['payload']['sender']
    message_text = data['payload']['text']

    message_to_broadcast = {
        "type": "message",
        "payload": {
            "room": room,
            "sender": sender,
            "text": message_text
        }
    }

    server_data = json.dumps(message_to_broadcast)
    send_broadcast_message(client_socket, CLIENTS, ROOMS, bytes(server_data, encoding='utf-8'))

def send_broadcast_message(client_socket, clients, rooms, data):
    for client in clients:
        if client != client_socket:
            for room in rooms:
                if (client in rooms[room]) and (client_socket in rooms[room]):
                    client.sendall(data)
                    break

if __name__ == '__main__':
    start_server()