import os
import asyncio
import ipaddress
import socket
from interfaces.i_task import ITask
from logger import Logger


class NodePortScan(ITask):

    datastore = None

    def __init__(self):
        self.uid = "31fca3c1-bf88-436b-ab71-ec028b1d3534"
        self.name = "NodePortScan"
        self.desc = "A Squall task to scan for unexpected Node ports"
        self.exceptions = [30080]
        self.frequency = 300
        self.run_immediately = True
        self.logger = Logger(self.name).get_logger()

    def get_frequency(self):
        return self.frequency

    def get_uid(self):
        return self.uid

    def get_name(self):
        return self.name

    def get_desc(self):
        return self.desc

    def get_config(self):
        return {
            'logger': self.logger,
            'ports': '30000-30100',
            'concurrency': 400,
            'exceptions': self.exceptions
        }

    @classmethod
    async def run(cls, *args, **kwargs) -> None:
        logger = kwargs.get('logger', None)
        ports = kwargs.get('ports', None)
        concurrency = kwargs.get('concurrency', None)
        network_data = kwargs.get('network_data', {})
        exceptions = kwargs.get('exceptions', [])

        async def check_port(ip, port, loop):
            conn = asyncio.open_connection(ip, port, loop=loop)
            try:
                reader, writer = await asyncio.wait_for(conn, timeout=1.0)
                conn.close()
                return (ip, port, True)
            except (ConnectionRefusedError, asyncio.TimeoutError, OSError):
                return (ip, port, False)

        async def port_scan(sem, ip, port, loop):
            async with sem:
                return await check_port(ip, port, loop)

        async def scan_entry(addresses, ports, loop, concurrency, exceptions):
            """
            scan TCP ports

                Parameters:
                    addresses (string): An IP address
                    port_range (int): a TCP port
                    loop (EventLoop): the event loop
                    concurrency (int): asyncio Semaphore concurrency value
            """
            sem = asyncio.Semaphore(concurrency)
            tasks = [asyncio.ensure_future(port_scan(sem, ip, port, loop)) for ip in addresses for port in ports if port not in exceptions]
            responses = await asyncio.gather(*tasks)
            return responses

        ip = network_data.get('node_ip', None)
        bits = ipaddress.IPv4Network(f'0.0.0.0/255.255.255.192').prefixlen
        ip_int = int(ipaddress.IPv4Address(ip))
        mask_int = int(ipaddress.IPv4Address('255.255.255.192'))
        net_int = ip_int & mask_int
        net_addr = str(ipaddress.IPv4Address(net_int))
        subnet = f'{net_addr}/{bits}'

        logger.info(f"Beginning NodePort TCP scan on ports: {ports}, for subnet: {subnet}")
        ports_bits = ports.split('-')
        start_port = int(ports_bits[0])
        end_port = int(ports_bits[1])
        ipaddresses = [str(ip) for ip in ipaddress.IPv4Network(subnet)]
        ports = range(start_port, end_port + 1)
        output_data = await scan_entry(ipaddresses, ports, asyncio.get_running_loop(), concurrency, exceptions)
        logger.info(f"Done NodePort TCP scan on ports: {ports}, for subnet: {subnet}")
        for data in output_data:
            if data in output_data:
                if data[2]:
                    logger.warning(f'port: {data[1]} is open on {data[0]}')
