import socket
import threading

port = 42069

class Host:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        # Získání lokální IP adresy pro zobrazení
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Host čeká na připojení na IP adrese {local_ip}, port {self.port}...")
        self.client_socket, self.client_address = self.socket.accept()
        print(f"Klient připojen z adresy {self.client_address}")
        self.chat()
    
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    print("Klient se odpojil.")
                    break
                print(f"Klient: {message}")
            except:
                print("Spojení bylo přerušeno.")
                break
        self.client_socket.close()
        self.socket.close()
    
    def chat(self):
        # Spustí přijímání zpráv v samostatném vlákně
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Hlavní smyčka pro odesílání zpráv
        try:
            while True:
                message = input("")
                if message.lower() == 'konec':
                    break
                self.client_socket.send(message.encode('utf-8'))
        except:
            print("Chyba při odesílání zprávy.")
        finally:
            self.client_socket.close()
            self.socket.close()

class Client:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        while True:
            host_ip = input("Zadejte IP adresu hosta: ").strip()
            if not host_ip:
                host_ip = 'localhost'  # Výchozí hodnota, pokud uživatel nic nezadá
            
            try:
                print(f"Připojování k hostu {host_ip} na portu {self.port}...")
                self.socket.connect((host_ip, self.port))
                print("Úspěšně připojeno k hostu!")
                break
            except ConnectionRefusedError:
                print("Připojení odmítnuto. Ujistěte se, že host běží a IP adresa je správná.")
                retry = input("Chcete to zkusit znovu? (ano/ne): ").lower()
                if retry != 'ano':
                    raise SystemExit("Program ukončen.")
            except socket.gaierror:
                print("Neplatná IP adresa. Zkuste to znovu.")
                retry = input("Chcete to zkusit znovu? (ano/ne): ").lower()
                if retry != 'ano':
                    raise SystemExit("Program ukončen.")
        self.chat()
    
    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if not message:
                    print("Host se odpojil.")
                    break
                print(f"Host: {message}")
            except:
                print("Spojení bylo přerušeno.")
                break
        self.socket.close()
    
    def chat(self):
        # Spustí přijímání zpráv v samostatném vlákně
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Hlavní smyčka pro odesílání zpráv
        try:
            while True:
                message = input("")
                if message.lower() == 'konec':
                    break
                self.socket.send(message.encode('utf-8'))
        except:
            print("Chyba při odesílání zprávy.")
        finally:
            self.socket.close()

if __name__ == "__main__":
    role = input("Zadejte roli (host/client): ").lower()
    
    if role == "host":
        host = Host(port)
        host.start()
    elif role == "client":
        client = Client(port)
        client.connect()  # Již nepředáváme výchozí 'localhost'
    else:
        print("Neplatná role! Použijte 'host' nebo 'client'.")