import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((HOST, PORT))


def message_handler():

    while True:
        message = client_socket.recv(1024).decode('utf-8')

        if not message:
            break

        message = json.loads(message)

        if message['type'] == 'connection':
            print(f"Connection received: {message['payload']['message']}")

        elif message['type'] == 'notification':
            print(f"Message received: {message['payload']['text']}")


client_thread = threading.Thread(target=message_handler)
client_thread.daemon = True
client_thread.start()

connection_room = str(input('Room: '))
client_name = str(input('Name: '))

message = {
    "type": "connect",
    "payload": {
        "room": connection_room,
        "name": client_name
    }
}


client_socket.send((json.dumps(message)).encode('utf-8'))

while True:

    client_message = str(input())

    if client_message.upper() == 'EXIT':
        break

    mess = {
        "type": "message",
        "payload": {
            "room": connection_room,
            "text": client_message,
            "sender": client_name
        }
    }

    client_socket.send(json.dumps(mess).encode('utf-8'))

client_socket.close()