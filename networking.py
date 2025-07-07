import socket as s
import threading as t
import json
import time

def validate_data_size(data, max_size_mb=10):
    """
    Kontroluje velikost dat před odesláním
    :param data: Data k odeslání
    :param max_size_mb: Maximální povolená velikost v MB
    :return: True pokud jsou data v pořádku, False pokud jsou příliš velká
    """
    try:
        json_size = len(json.dumps(data).encode('utf-8'))
        return json_size <= (max_size_mb * 1024 * 1024)
    except Exception:
        return False

def validate_data_structure(data):
    """
    Kontroluje strukturu dat před odesláním
    :param data: Data k ověření
    :return: True pokud mají data správnou strukturu, False pokud ne
    """
    try:
        json.dumps(data)
        if isinstance(data, dict):
            allowed_keys = {"Player", "Enemies", "Projectiles", "Sound_events", "Shooting","Events"}
            if not all(key in allowed_keys for key in data.keys()):
                return False

            if "Player" in data and data["Player"] is not None:
                if not isinstance(data["Player"], tuple) or len(data["Player"]) != 2:
                    return False

            if "Sound_events" in data and not isinstance(data["Sound_events"], dict):
                return False

            return True
    except (TypeError, json.JSONDecodeError):
        return False
    return True

class NetworkManager:
    """
    Univerzální třída pro síťovou komunikaci, může fungovat jako host nebo klient
    """
    def __init__(self, message_callback, is_host=False):
        """
        Inicializace síťového manageru
        :param message_callback: Callback funkce pro zpracování přijatých zpráv
        :param is_host: True pro hostitele, False pro klienta
        """
        self.message_callback = message_callback
        self.is_host = is_host
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket.setsockopt(s.IPPROTO_TCP, s.TCP_NODELAY, 1)
        if self.is_host:
            self.socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.running = False
        self.buffer_size = 16384
        self.connection_socket = None  # Socket pro aktivní spojení

    def start(self, port, ip=''):
        """
        Spustí síťové spojení
        :param port: Port pro připojení/naslouchání
        :param ip: IP adresa pro připojení (ignorováno pro hostitele)
        :return: True pokud bylo spojení úspěšné, False pokud ne
        """
        try:
            if self.is_host:
                return self._start_host(port)
            else:
                return self._start_client(ip, port)
        except Exception as e:
            print(f"Chyba při {'spuštění serveru' if self.is_host else 'připojování'}: {e}")
            return False

    def _start_host(self, port):
        """Spustí server jako hostitel"""
        self.socket.bind(('', port))
        self.socket.listen(1)
        hostname = s.gethostname()
        self.local_ip = s.gethostbyname(hostname)
        print(f"Host čeká na připojení na IP adrese {self.local_ip}, port {port}")

        self.connection_socket, self.client_address = self.socket.accept()
        self.connection_socket.setsockopt(s.IPPROTO_TCP, s.TCP_NODELAY, 1)
        print(f"Klient připojen z adresy {self.client_address}")

        self._start_receiving()
        return True

    def _start_client(self, host_ip, port):
        """Připojí se k serveru jako klient"""
        print(f"Připojování k hostu {host_ip} na portu {port}...")
        self.socket.connect((host_ip, port))
        self.connection_socket = self.socket
        print("Úspěšně připojeno k hostu!")

        self._start_receiving()
        return True

    def _start_receiving(self):
        """Spustí přijímací smyčku ve vlastním vlákně"""
        self.running = True
        self.receive_thread = t.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def _receive_loop(self):
        """Smyčka pro přijímání zpráv"""
        incomplete_data = ""
        while self.running:
            try:
                data = self.connection_socket.recv(self.buffer_size).decode('utf-8')
                if not data:
                    break

                incomplete_data += data
                try:
                    message = json.loads(incomplete_data)
                    self.message_callback(message)
                    incomplete_data = ""
                except json.JSONDecodeError:
                    continue

            except Exception as e:
                print(f"Chyba příjmu: {e}")
                time.sleep(0.1)
                continue
        self.stop()

    def send(self, data):
        """
        Bezpečné odeslání dat
        :param data: Data k odeslání
        :return: True pokud bylo odeslání úspěšné, False pokud ne
        """
        if not self.running or not self.connection_socket:
            return False

        if not validate_data_structure(data):
            print("Chyba: Neplatná struktura dat")
            return False

        if not validate_data_size(data):
            print("Chyba: Data jsou příliš velká")
            return False

        try:
            message = json.dumps(data)
            self.connection_socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Chyba odesílání: {e}")
            return False

    def stop(self):
        """Ukončí síťové spojení"""
        self.running = False
        try:
            if self.connection_socket:
                self.connection_socket.close()
            if self.is_host:
                self.socket.close()
        except:
            pass