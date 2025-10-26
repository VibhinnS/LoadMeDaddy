import itertools
import asyncio

from lockpy import private

from config.ConfigReader import ConfigReader

class LoadBalancer:
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configured_servers_ip = self.config_reader.get_config("SERVERS", "IP_ADDRESSES")
        self.configured_server_ports = self.config_reader.get_config("SERVERS", "PORTS")
        self.configured_servers = list(zip(self.configured_servers_ip, self.configured_server_ports))
        self.configured_server_iterator = itertools.cycle(self.configured_servers)
        self.balancer_ip = self.config_reader.get_config("BALANCER", "IP_ADDRESS")
        self.balancer_port = self.config_reader.get_config("BALANCER", "PORT")

    async def handle_incoming_request(self, client_reader, client_writer):
        available_server_ip, available_server_port = next(self.configured_server_iterator)
        server_reader, server_writer = await asyncio.open_connection(available_server_ip, available_server_port)

        await asyncio.gather(
            self.forward_requests(client_reader, server_writer),
            self.forward_requests(server_reader, client_writer)
        )

    async def start_balancer(self):
        load_balancer_server = await asyncio.start_server(
            self.handle_incoming_request,
            self.balancer_ip,
            self.balancer_port
        )

        async with load_balancer_server:
            await load_balancer_server.serve_forever()

    @private
    async def forward_requests(self, source, destination):
        try:
            while True:
                data = await source.read(4096)
                if not data: break
                destination.write(data)
                await destination.drain()
        finally:
            destination.close()
            await destination.wait_closed()

