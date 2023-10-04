import socket

HOST = '127.0.0.1'  # IP address of your web server
PORT = 8080  # Port to connect to
paths = []
product_pages = []

# Function to send an HTTP GET request and receive the response
def send_http_request(path):
    try:
        # Create a socket that uses IPv4 and TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        client_socket.connect((HOST, PORT))
        
        # Send an HTTP GET request for the specified path
        request = f'GET {path} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n'
        client_socket.send(request.encode())

        # Receive and decode the response data
        response = client_socket.recv(4096).decode('utf-8')

        # Close the client socket
        client_socket.close()

        return response
    except Exception as e:
        pass


response = send_http_request('/products')   #retrieve product paths from listing page
responses = response.split('"')
paths = [response for response in responses if "http" in response]
for path in paths:
    path=path.split("8080")[1]
    product_pages.append(path)

# simple pages 
simple_pages = ['/about', '/contacts']
page_contents = {}
for path in simple_pages:
    response = send_http_request(path)
    if response:
        page_contents[path] = response

# product pages 
product_details = {}
for path in product_pages:
    response = send_http_request(path)
    if response:
        lines = []
        #print(response)
        lines = response.split('<p>')

        name_line = lines[2].split('<', 1)[0]
        author_line = lines[3].split('<', 1)[0]
        price_line = lines[4].split('<', 1)[0]
        description_line = lines[5].split('<', 1)[0]
        #print("####################")

        product_details[path] = {
            "name": name_line,
            "author": author_line,
            "price": price_line,
            "description": description_line
        }

f = open("data.txt", "w")

print("Simple Page Contents:")
for path, content in page_contents.items():
    f.write(f"http://127.0.0.1:8080{path}:\n{content}\n")
    print(f"http://127.0.0.1:8080{path}:\n{content}\n")
    print("##################")
f.close()

print("Product Details:")
for path, details in product_details.items():
    print(f"http://127.0.0.1:8080{path}:\n{details}\n")
    print("##################")
