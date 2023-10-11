import socket
import threading
import json

# Server configuration
HOST = '127.0.0.1'
PORT = 8090

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")

def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        message_data = json.loads(message)
        if message_data["type"] == "connected":
            print(message_data["payload"]["message"])
        elif message_data["type"] == "message":
            sender = message_data["payload"]["sender"]
            room = message_data["payload"]["room"]
            text = message_data["payload"]["message"]
            print(f"{sender} in room '{room}': {text}")
        elif message_data["type"] == "error":
            err = message_data["payload"]["message"]
            print(err)
        elif message_data["type"] == "connect_ack":
            ack_message = message_data["payload"]["message"]
            print(f"Connection: {ack_message}")
        else:
            print("")

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

client_name = input("Name: ")
room_name = input("Room: ")
connect_message = json.dumps({"type": "connect", "payload": {"name": client_name, "room": room_name}})
client_socket.send(connect_message.encode('utf-8'))

while True:
    message = input("Enter a message (or 'exit' to quit): ")

    if message.lower() == 'exit':
        print("User exited from room")
        break
    text = json.dumps({"type": "message",
                       "payload": {"sender": client_name,
                                   "room": room_name,
                                   "text": message}})
    client_socket.send(text.encode('utf-8'))

# Close the client socket when done
client_socket.close()