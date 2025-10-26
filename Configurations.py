import itertools

from config.ConfigReader import ConfigReader

class Configurations:
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configured_servers_ip = self.config_reader.get_config("SERVERS", "IP_ADDRESSES")
        self.configured_servers_ports = self.config_reader.get_config("SERVERS", "PORTS")
        self.configured_servers = list(zip(self.configured_servers_ip, self.configured_servers_ports))
        self.configured_servers_iterator = itertools.cycle(self.configured_servers)
        self.balancer_ip = self.config_reader.get_config("BALANCER", "IP_ADDRESS")
        self.balancer_port = self.config_reader.get_config("BALANCER", "PORT")
