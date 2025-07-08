import socket

# Set up UDP server
server_ip = "25.21.131.22"  # Or your actual IP
server_port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

print(f"[SERVER] Listening on {server_ip}:{server_port}...")

client_address = None

while True:
    data, addr = server_socket.recvfrom(1024)
    message = data.decode()
    print(f"[SERVER] Received: '{message}' from {addr}")

    if message.startswith("HELLO"):
        client_address = addr
        server_socket.sendto(b"WELCOME", client_address)
        print(f"[SERVER] Connection established with {client_address}")
    else:
        if client_address:
            reply = f"Echo: {message}"
            server_socket.sendto(reply.encode(), client_address)

