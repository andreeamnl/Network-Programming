import socket
import signal
import sys
import threading
import json
from time import sleep
# Define the server's IP address and port
HOST = '127.0.0.1' # IP address to bind to (localhost)
PORT = 8080 # Port to listen on
# Create a socket that uses IPv4 and TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the address and port
server_socket.bind((HOST, PORT))
# Listen for incoming connections
server_socket.listen(5) # Increased backlog for multiple simultaneous connections
print(f"Server is listening on {HOST}:{PORT}")



product_file= open('products.json', 'r') 
products = json.load(product_file)

# Function to handle client requests
def handle_request(client_socket):
    # Receive and print the client's request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")
    # Parse the request to get the HTTP method and path
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]
    # Initialize the response content and status code
    response_content = ''
    status_code = 200
    # Define a simple routing mechanism
    if path == '/':
        response_content = 'Ciao'
    elif path == '/about':
        response_content = 'This is the About page.'
    elif path == '/contacts':
        response_content = 'No need to contact'
    elif path == '/products':
       for i in range(len(products)):
            product= products[i]

            response_content += f'<li><a href="http://127.0.0.1:8080/products/{i}">{product["name"]}</a></li>'

        ##response_content = 'This is products page'

    elif path == '/products/0':
            product= products[0]
            response_content = '<h1><p>Products</p></h1><ul>'
            response_content += f'<li><strong><p>{product["name"]},</p></strong> <p>{product["author"]}</p><p>${product["price"]}</p><p>{product["description"]}</p></li>'
            response_content += '</ul>'

    elif path == '/products/1':
            response_content = '<h1><p>Products</p></h1><ul>'
            product= products[1]
            response_content += f'<li><strong><p>{product["name"]},</p></strong> <p>{product["author"]}</p><p>${product["price"]}</p><p>{product["description"]}</p></li>'
            response_content += '</ul>'


    else:

        response_content = '404 Not Found'
        status_code = 404
    # Prepare the HTTP response
    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))
    # Close the client socket
    client_socket.close()
    # Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)
    # Register the signal handler
signal.signal(signal.SIGINT, signal_handler)



while True:
    # Accept incoming client connections
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    # Create a thread to handle the client's request
    client_handler = threading.Thread(target=handle_request, args=(client_socket,))
    client_handler.start()


