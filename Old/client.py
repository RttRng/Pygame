import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external host (doesn't have to be reachable)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

i = input("Ip adresa z hamachi (jakože tvoje): ")
if i == "":
    client_ip = "25.21.131.22"  # Replace with your actual IP if needed
else:
    client_ip = i
client_port = 0
server_ip = "25.21.131.22"
server_port = 12345
print(client_ip)
server_address = (server_ip,server_port)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind((client_ip, client_port))

# Send "HELLO" with client's IP/PORT (just symbolic—server gets it from addr)
client_socket.sendto(b"HELLO", server_address)
print("Sent HELLO")
while True:
    data, addr = client_socket.recvfrom(1024)
    print(f"[CLIENT] Received: '{data.decode()}' from {addr}")
    # Example of sending more data
    msg = input("[CLIENT] Type message: ")
    client_socket.sendto(msg.encode(), server_address)