import socket
import threading

from lockpy import private

from config.ConfigReader import ConfigReader

class LoadBalancer:
    CURRENT_SERVER = 0
    LOCK = threading.Lock()

    def __init__(self):
        self.config_reader = ConfigReader()
        self.configured_servers_ip = self.config_reader.get_config("SERVERS", "IP_ADDRESSES")
        self.configured_server_ports = self.config_reader.get_config("SERVERS", "PORTS")
        self.configured_servers = list(zip(self.configured_servers_ip, self.configured_server_ports))
        self.balancer_ip = self.config_reader.get_config("BALANCER", "IP_ADDRESS")
        self.balancer_port = self.config_reader.get_config("BALANCER", "PORT")

    def handle_incoming_request(self, client_socket: socket.socket):
        available_server_ip, available_server_port = self.get_available_server()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((available_server_ip, available_server_port))

        threading.Thread(target=self.forward_requests, args=(client_socket, server_socket), daemon=True).start()
        threading.Thread(target=self.forward_requests, args=(server_socket, client_socket), daemon=True).start()

    def start_balancer(self):
        balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        balancer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        balancer_socket.bind((self.balancer_ip, self.balancer_port))
        balancer_socket.listen(100)

        while True:
            client_socket, address = balancer_socket.accept()
            threading.Thread(target=self.handle_incoming_request, args=(client_socket,), daemon=True).start()

    @private
    def get_available_server(self):
        with self.LOCK:
            server = self.configured_servers[self.CURRENT_SERVER]
            self.CURRENT_SERVER = (self.CURRENT_SERVER + 1) % len(self.configured_servers)
        return server

    @private
    def forward_requests(self, source, destination):
        try:
            while True:
                data = source.recv(4096)
                if data: destination.sendall(data)
        finally:
            source.close()
            destination.close()

