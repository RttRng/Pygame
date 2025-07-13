import socket
import sys
import threading
import json
import string

FORMAT = "utf-8"


class Host:
    def __init__(self, port, callback):
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
        data = json.dumps(data)
        if (self.client_socket is None):
            return
        split_data = self.split(data)
        for chunk in split_data:
            self.client_socket.send(chunk.encode(FORMAT))

    def split(self, json_str, chunk_size=2000):
        chunks = [json_str[i:i + chunk_size] for i in range(0, len(json_str), chunk_size)]

        # Generate prefixes: 'a' to 'z', then '0' for the last chunk
        prefixes = list(string.ascii_lowercase) + ['0']

        # # If the string needs more than 26 chunks before the final one,
        # # we can extend with double letters (aa, ab, ...) or use numbers instead
        # if len(chunks) > len(prefixes):
        #     extra_prefixes = [f"{i}" for i in range(1, len(chunks) - len(prefixes) + 1)]
        #     prefixes = list(string.ascii_lowercase) + extra_prefixes + ['0']

        # Add prefix to each chunk
        labeled_chunks = [prefixes[i] + chunk for i, chunk in enumerate(chunks[:-1])]
        labeled_chunks.append('0' + chunks[-1])  # Final chunk gets '0'

        return labeled_chunks

    def stitch_json_parts(self,parts):
        # Create a dictionary keyed by the prefix
        parts_dict = {part[0]: part[1:] for part in parts}
        if '0' not in parts_dict.keys():
            return False
        # Separate '0' from the rest, sort the letters, then add '0' at the end
        regular_keys = sorted([k for k in parts_dict if k != '0'])
        ordered_keys = regular_keys.append('0')

        # Stitch the parts back together
        stitched_json = ''.join([parts_dict[key] for key in regular_keys])

        return stitched_json

    def receive(self):
        cashe = []
        while True:
            try:
                data = self.client_socket.recv(2048).decode(FORMAT)
                cashe.append(data)
                out = self.stitch_json_parts(cashe)
                if out == False:
                    continue
                cashe.clear()
                data_json = json.loads(out)
                out = False
                if isinstance(data_json, dict):
                    type = data_json["type"]
                    if type == "DISCONNECT":
                        print(f"[HOST] Disconnected from {self.client_address}")
                        break
                    self.callback(type, data_json)
                else:
                    print(f"[HOST] Received unexpected JSON format: {data_json}")

            except Exception as e:
                print(f"[HOST] Error receiving data: {e}")

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
        data = json.dumps(data)
        split_data = self.split(data)
        for chunk in split_data:
            self.client_socket.send(chunk.encode(FORMAT))


    def split(self, json_str, chunk_size=2000):
        chunks = [json_str[i:i + chunk_size] for i in range(0, len(json_str), chunk_size)]

        # Generate prefixes: 'a' to 'z', then '0' for the last chunk
        prefixes = list(string.ascii_lowercase) + ['0']

        # # If the string needs more than 26 chunks before the final one,
        # # we can extend with double letters (aa, ab, ...) or use numbers instead
        # if len(chunks) > len(prefixes):
        #     extra_prefixes = [f"{i}" for i in range(1, len(chunks) - len(prefixes) + 1)]
        #     prefixes = list(string.ascii_lowercase) + extra_prefixes + ['0']

        # Add prefix to each chunk
        labeled_chunks = [prefixes[i] + chunk for i, chunk in enumerate(chunks[:-1])]
        labeled_chunks.append('0' + chunks[-1])  # Final chunk gets '0'

        return labeled_chunks

    def stitch_json_parts(self,parts):
        # Create a dictionary keyed by the prefix
        parts_dict = {part[0]: part[1:] for part in parts}
        if '0' not in parts_dict.keys():
            return False
        # Separate '0' from the rest, sort the letters, then add '0' at the end
        regular_keys = sorted([k for k in parts_dict if k != '0'])
        ordered_keys = regular_keys.append('0')

        # Stitch the parts back together
        stitched_json = ''.join([parts_dict[key] for key in regular_keys])

        return stitched_json

    def receive(self):
        cashe = []
        while True:
            try:
                data = self.client_socket.recv(2048).decode(FORMAT)
                cashe.append(data)
                print(cashe)
                out = self.stitch_json_parts(cashe)
                if out == False:
                    continue
                cashe.clear()
                data_json = json.loads(out)
                out = False
                if isinstance(data_json, dict):
                    type = data_json["type"]
                    if type == "DISCONNECT":
                        print(f"[CLIENT] Disconnected from {self.address}:{self.port}")
                        break
                    self.callback(type, data_json)
                else:
                    print(f"[CLIENT] Received unexpected JSON format: {data_json}")


            except Exception as e:
                print(f"[CLIENT] Error receiving data: {e}")
                continue
