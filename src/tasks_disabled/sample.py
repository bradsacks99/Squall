import asyncio
import sys

from interfaces.i_task import ITask
from logger import Logger
from utils import get_network

class Sample(ITask):

    def __init__(self):
        self.uid = "20e9a6fe-0ec6-4d39-b383-010334efb229"
        self.name = "PortScan"
        self.desc = "A Network Port Scanner"
        self.frequency = 30
        self.logger = Logger("PortScan").get_logger()
        self.database = None
        self.network = get_network()

    def get_uid(self):
        return self.uid

    def get_name(self):
        return self.name

    def get_desc(self):
        return self.desc

    def get_frequency(self):
        return self.frequency

    def get_config(self):
        return {
            'network': self.network,
            'logger': self.logger
        }

    def set_database(self, database):
        self.database = database

    def _get_network(self) -> str:
        output = None
        cmd = ['ifconfig', 'eth0']
        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as err:
            self.logger.error(str(err))
            raise err

        regex = r'inet\s(\d+.\d+.\d+.\d+)\s\snetmask\s(\d+.\d+.\d+.\d+)\s'
        match = re.search(regex, output.decode('utf-8'))
        if match:
            ip = match.group(1)
            mask = match.group(2)
            bits = ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen
            ip_int = int(ipaddress.IPv4Address(ip))
            mask_int = int(ipaddress.IPv4Address(mask))
            net_int = ip_int & mask_int
            net_addr = str(ipaddress.IPv4Address(net_int))
            ip_address = f'{net_addr}/{bits}'
        return ip_address

    @staticmethod
    async def run(*args, **kwargs):
        network = kwargs.get('network', '0.0.0.0')
        logger = kwargs.get('logger', None)
        logger.info(f"Checking network: {network}")
        # s = sr1(IP(dst=network)/TCP(dport=80, flags="S"))
        # logger.info(s.show())




