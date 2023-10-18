import socket
import threading
import json
import os
import re

HOST = '127.0.0.1'
PORT = 1117
MEDIA_FOLDER = 'client_media'
CLIENT_SOCKET = None

def connect():
    global CLIENT_SOCKET
    CLIENT_SOCKET = create_client_socket()
    print(f"Connected to {HOST}:{PORT}")

def create_client_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((HOST, PORT))
    return client_socket

def perform_server_connection():
    name = input('Enter your name: ')
    room = input('Enter the room: ')

    connection_message = {
        "type": "connect",
        "payload": {
            "name": name,
            "room": room
        }
    }

    data = json.dumps(connection_message)
    CLIENT_SOCKET.sendall(bytes(data, encoding='utf-8'))

    return name, room

def receive_messages(client_socket, name):
    while True:
        server_message = client_socket.recv(1024).decode('utf-8')
        if not server_message:
            break

        data = json.loads(server_message)
        handle_server_message(data, name, client_socket)

def handle_server_message(data, name, client_socket):
    message_type = data.get('type', '')

    if message_type == 'connect_ack' or message_type == 'notification':
        print(data['payload']['message'])
    elif data['type'] == 'download-ack':
        download_file(client_socket, data, name)
    elif message_type == 'message':
        print(f"\nRoom: {data['payload']['room']}, {data['payload']['sender']}: {data['payload']['text']}")
    else:
        print(f'\nInvalid message received: {data}')

def upload_file(file_path, name, room):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_upload_message = {
        "type": "upload",
        "payload": {
            "file_name": file_name,
            "file_size": file_size,
            "name": name,
            "room": room
        }
    }
    data = json.dumps(file_upload_message)
    CLIENT_SOCKET.sendall(bytes(data, encoding='utf-8'))

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            CLIENT_SOCKET.sendall(chunk)

def download_file(client_socket, data, name):
    file_name = data['payload']['file_name']
    option = 'w'
    if not os.path.exists(os.path.join(MEDIA_FOLDER, name, file_name)):
        option = 'x'

    with open(os.path.join(MEDIA_FOLDER, name, file_name), f'{option}b') as received_file:
        file_size = data['payload']['file_size']
        index = 0
        while index < file_size:
            chunk = client_socket.recv(1024)
            received_file.write(chunk)
            index += len(chunk)

    print('File was downloaded successfully')

def main():
    connect()
    name, room = perform_server_connection()

    if not os.path.isdir(os.path.join(MEDIA_FOLDER, name)):
        os.makedirs(os.path.join(MEDIA_FOLDER, name))

    receive_thread = threading.Thread(target=receive_messages, args=(CLIENT_SOCKET, name))

    receive_thread.daemon = True
    receive_thread.start()

    while True:
        message = input()
        if message.lower() == 'exit':
            disconnect_message = {
                "type": "disconnect",
                "payload": {
                    "name": name,
                    "room": room
                }
            }
            data = json.dumps(disconnect_message)
            CLIENT_SOCKET.sendall(bytes(data, encoding='utf-8'))
            break

        if re.match(r'upload ([A-Za-z\./]+)', message):
            upload_file(message.split(' ')[1], name, room)
        elif re.match(r'download ([A-Za-z\.]+)', message):
            file_download_message = {
                "type": "download",
                "payload": {
                    "file_name": message.split(' ')[1],
                    "name": name,
                    "room": room
                }
            }
            data = json.dumps(file_download_message)
            CLIENT_SOCKET.sendall(bytes(data, encoding='utf-8'))
        else:
            chat_message = {
                "type": "message",
                "payload": {
                    "sender": name,
                    "room": room,
                    "text": f'{message}\n'
                }
            }

            data = json.dumps(chat_message)
            CLIENT_SOCKET.sendall(bytes(data, encoding='utf-8'))

if __name__ == '__main__':
    main()