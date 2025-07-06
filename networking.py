import socket
import threading
import json
import time

class Host:
    def __init__(self, port, message_callback):
        self.port = port
        self.message_callback = message_callback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.running = False
        self.buffer_size = 16384  # Zvětšený buffer

    def start(self):
        try:
            self.socket.bind(('', self.port))
            self.socket.listen(1)
            hostname = socket.gethostname()
            self.local_ip = socket.gethostbyname(hostname)
            print(f"Host čeká na připojení na IP adrese {self.local_ip}, port {self.port}")

            self.client_socket, self.client_address = self.socket.accept()
            self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print(f"Klient připojen z adresy {self.client_address}")

            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            return True
        except Exception as e:
            print(f"Chyba při spuštění serveru: {e}")
            return False

    def _receive_loop(self):
        incomplete_data = ""
        while self.running:
            try:
                data = self.client_socket.recv(self.buffer_size).decode('utf-8')
                if not data:
                    break
                
                incomplete_data += data
                try:
                    message = json.loads(incomplete_data)
                    self.message_callback(message)
                    incomplete_data = ""
                except json.JSONDecodeError:
                    continue  # Počkáme na další data
                
            except Exception as e:
                print(f"Chyba příjmu: {e}")
                time.sleep(0.1)  # Přidáme malé zpoždění při chybě
                continue
        self.stop()

    def send(self, data):
        if self.running:
            try:
                message = json.dumps(data)
                self.client_socket.sendall(message.encode('utf-8'))
                return True
            except Exception as e:
                print(f"Chyba odesílání: {e}")
                return False
        return False

    def stop(self):
        self.running = False
        try:
            self.client_socket.close()
            self.socket.close()
        except:
            pass

class Client:
    def __init__(self, message_callback):
        self.message_callback = message_callback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.running = False
        self.buffer_size = 16384  # Zvětšený buffer

    def connect(self, host_ip, port):
        try:
            print(f"Připojování k hostu {host_ip} na portu {port}...")
            self.socket.connect((host_ip, port))
            print("Úspěšně připojeno k hostu!")

            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            return True
        except Exception as e:
            print(f"Chyba při připojování: {e}")
            return False

    def _receive_loop(self):
        incomplete_data = ""
        while self.running:
            try:
                data = self.socket.recv(self.buffer_size).decode('utf-8')
                if not data:
                    break
                
                incomplete_data += data
                try:
                    message = json.loads(incomplete_data)
                    self.message_callback(message)
                    incomplete_data = ""
                except json.JSONDecodeError:
                    continue  # Počkáme na další data
                    
            except Exception as e:
                print(f"Chyba příjmu: {e}")
                time.sleep(0.1)  # Přidáme malé zpoždění při chybě
                continue
        self.stop()

    def send(self, data):
        if self.running:
            try:
                message = json.dumps(data)
                self.socket.sendall(message.encode('utf-8'))
                return True
            except Exception as e:
                print(f"Chyba odesílání: {e}")
                return False
        return False

    def stop(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass