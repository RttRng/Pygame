import socket
import sys
import threading
import json

FORMAT = "utf-8"


class Host:
    def __init__(self, port, callback):
        self.name = "[HOST]"
        self.port = port
        self.callback = callback
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", self.port))
        self.client_socket = None
        self.client_address = None
        threading.Thread(target=self.start).start()

    def start(self):
        self.server_socket.listen()
        print(f"[HOST] Listening on port {self.port}...")
        while True:
            self.client_socket, self.client_address = self.server_socket.accept()
            threading.Thread(target=self.receive).start()
            print(f"[HOST] Connection established with {self.client_address}")

    def send(self, type=str, data=dict):
        data.update({"type": type})
        data = json.dumps(data).encode(FORMAT)
        if (self.client_socket is None):
            return
        self.client_socket.send(data)

    def receive(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode(FORMAT)
                data_json = json.loads(data)
                if isinstance(data_json, dict):
                    type = data_json["type"]
                    if type == "DISCONNECT":
                        print(f"[HOST] Disconnected from {self.client_address}")
                        break
                    self.callback(type, data_json)
                else:
                    print(f"{self.name} Received unexpected JSON format: {data_json}")

            except Exception as e:
                print(f"{self.name} Error receiving data: {e}")

                continue
        self.client_socket.close()


class Client:
    def __init__(self, address, port, callback):
        self.name = "[CLIENT]"
        self.callback = callback
        self.address = address
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.address, self.port))
        print(f"[CLIENT] Connected to {self.address}:{self.port}")
        threading.Thread(target=self.receive).start()

    def send(self, type, data):
        data["type"] = type
        data = json.dumps(data).encode(FORMAT)
        self.client_socket.send(data)

    def receive(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode(FORMAT)
                data_json = json.loads(data)
                if isinstance(data_json, dict):
                    type = data_json["type"]
                    if type == "DISCONNECT":
                        print(f"[CLIENT] Disconnected from {self.address}:{self.port}")
                        break
                    self.callback(type, data_json)
                else:
                    print(f"{self.name} Received unexpected JSON format: {data_json}")


            except Exception as e:
                print(f"{self.name} Error receiving data: {e}")
                continue
