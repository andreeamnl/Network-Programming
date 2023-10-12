import socket
import threading
import json
import os
import re

HOST = '127.0.0.1'
PORT = 1111
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

def receive_messages(name):
    while True:
        server_message = CLIENT_SOCKET.recv(1024).decode('utf-8')
        if not server_message:
            break

        try:
            data = json.loads(server_message)
        except json.JSONDecodeError:
            print("Received invalid JSON data from the server.")
            continue

        handle_server_message(data, name)


def handle_server_message(data, name):
    message_type = data.get('type', '')

    if message_type == 'connect_ack' or message_type == 'notification':
        print(data['payload']['message'])
    elif message_type == 'download-ack':
        download_file(data, name)
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

def download_file(data, name):
    message_type = data.get('type', '')

    if message_type == 'download-ack':
        file_name = data['payload']['file_name']

        room = data['payload'].get('room', '')  

        file_path = os.path.join(MEDIA_FOLDER, room, file_name)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)

            stream_message = {
                "type": "download-ack",
                "payload": {
                    "file_name": file_name,
                    "file_size": file_size
                }
            }
            server_data = json.dumps(stream_message)
            CLIENT_SOCKET.sendall(bytes(server_data, encoding='utf-8'))

            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(1024), b''):
                    CLIENT_SOCKET.sendall(chunk)
        else:
            notification_message = {
                "type": "notification",
                "payload": {
                    "message": f"The file {file_name} does not exist.\n"
                }
            }
            server_data = json.dumps(notification_message)
            CLIENT_SOCKET.sendall(bytes(server_data, encoding='utf-8'))
    else:
        print(f'Invalid message type for download: {message_type}')


def main():
    connect()
    name, room = perform_server_connection()

    if not os.path.isdir(os.path.join(MEDIA_FOLDER, name)):
        os.makedirs(os.path.join(MEDIA_FOLDER, name))

    receive_thread = threading.Thread(target=receive_messages, args=(name,))
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