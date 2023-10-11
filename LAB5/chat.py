import socket
import threading
import json

# Server configuration
HOST = '127.0.0.1'
PORT = 8090

clients = {}
rooms = {}

def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")

    # Receive the "connect" message from the client
    connect_message = client_socket.recv(1024).decode('utf-8')
    connect_data = json.loads(connect_message)
    if connect_data["type"] == "connect":
        name = connect_data["payload"]["name"]
        room_name = connect_data["payload"]["room"]
        print(f"{name} connected to '{room_name}'")

        # Add the client to the room
        if room_name not in rooms:
            rooms[room_name] = []
        rooms[room_name].append(client_socket)

        welcome_message = f"Hi, {name}, you joined {room_name}"
        send_message(client_socket, "connected", {"message": welcome_message})
        send_message(client_socket, "connect_ack", {"message": "connected"})
        notification_message = f"{name} has joined the room."
        sent_notification(client_socket, room_name, notification_message)
    else:
        return

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
        except:
            break

        message_data = json.loads(message)
        if message_data["type"] == "message":
            sender = message_data["payload"]["sender"]
            room = message_data["payload"]["room"]
            chat_message = message_data["payload"]["text"]
            print(f"Received from {name} in room '{room}', message: {chat_message}")

            for client in rooms.get(room, []):
                if client != client_socket:
                    send_message(client, "message", {"sender": sender, "room": room, "message": chat_message})
        else:
            print("")

    if room_name in rooms:
        rooms[room_name].remove(client_socket)
    clients.pop(client_socket, None)
    client_socket.close()

def send_message(client_socket, message_type, payload):
    message = json.dumps({"type": message_type, "payload": payload})
    client_socket.send(message.encode('utf-8'))

def sent_notification(sender_socket, room, msg):
    for client in rooms.get(room, []):
        if client != sender_socket:
            send_message(client, "notification", {"message": msg})

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    clients[client_socket] = client_address

    # Start a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()