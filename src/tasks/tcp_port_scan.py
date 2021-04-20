import os
import asyncio
import ipaddress
import socket
from interfaces.i_task import ITask
from logger import Logger


class TcpPortScan(ITask):

    datastore = None

    def __init__(self):
        self.uid = "e7338578-b527-43dc-a0a7-2bd04233629f"
        self.name = "TcpPortScan"
        self.desc = "A Squall task to scan TCP ports"
        self.frequency = 300
        self.run_immediately = False
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
            'ports': '0-1024',
            'concurrency': 400
        }

    @classmethod
    async def run(cls, *args, **kwargs) -> None:
        logger = kwargs.get('logger', None)
        ports = kwargs.get('ports', None)
        concurrency = kwargs.get('concurrency', None)
        network_data = kwargs.get('network_data', {})

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

        async def scan_entry(addresses, ports, loop, concurrency):
            """
            scan TCP ports

                Parameters:
                    addresses (string): An IP address
                    port_range (int): a TCP port
                    loop (EventLoop): the event loop
                    concurrency (int): asyncio Semaphore concurrency value
            """
            sem = asyncio.Semaphore(concurrency)
            tasks = [asyncio.ensure_future(port_scan(sem, ip, port, loop)) for ip in addresses for port in ports]
            responses = await asyncio.gather(*tasks)
            return responses

        ip = network_data.get('node_ip', None)
        bits = ipaddress.IPv4Network(f'0.0.0.0/255.255.255.192').prefixlen
        ip_int = int(ipaddress.IPv4Address(ip))
        mask_int = int(ipaddress.IPv4Address('255.255.255.192'))
        net_int = ip_int & mask_int
        net_addr = str(ipaddress.IPv4Address(net_int))
        subnet = f'{net_addr}/{bits}'

        logger.info(f"Beginning TCP scan on ports: {ports}, for subnet: {subnet}")
        ports_bits = ports.split('-')
        start_port = int(ports_bits[0])
        end_port = int(ports_bits[1])
        ipaddresses = [str(ip) for ip in ipaddress.IPv4Network(subnet)]
        ports = range(start_port, end_port + 1)
        output_data = await scan_entry(ipaddresses, ports, asyncio.get_running_loop(), concurrency)
        logger.info(f"Done TCP scan on ports: {ports}, for subnet: {subnet}")
        for data in output_data:
            if data in output_data:
                if data[2]:
                    logger.warning(f'port: {data[1]} is open on {data[0]}')
