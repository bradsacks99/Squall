import os
import asyncio
from interfaces.i_task import ITask
from logger import Logger


class FindClusterMembers(ITask):

    datastore = None

    @property
    def datastore(self):
        return type(self).datastore

    @datastore.setter
    def datastore(self, val):
        type(self).datastore = val

    def __init__(self):
        self.uid = "c224f46e-d258-4818-a1bb-4361ceaf849c"
        self.name = "FindClusterMembers"
        self.desc = "A Squall background task to find new cluster memebers"
        self.raft_service = os.getenv("RAFT_SERVICE_NAME", None)
        self.frequency = 30
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
            'raft_service': self.raft_service
        }

    @classmethod
    async def run(cls, *args, **kwargs) -> None:
        logger = kwargs.get('logger', None)
        raft_service = kwargs.get('raft_service', None)
        logger.info(cls.datastore)

        if raft_service is None:
            logger.error("Unable to run task. No raft_service value for DNS lookup")
            return

        logger.info(f"Getting dns records for: {raft_service}")
        cmd = f'nslookup {raft_service}'

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        dns_response = stdout.decode()

        ip_addresses = []
        for lines in dns_response.split('\n'):
            if 'Address' in lines:
                ip_addresses.append(lines.replace('Address: ', ''))
        ip_addresses.pop(0)

        logger.info(f'Updating cluster members with ip addresses {ip_addresses}')
        result = await cls.datastore.update_members(ip_addresses)
        logger.info(f'The new cluster members are {result}')
        logger.info("Cluster status: " + str(cls.datastore.getStatus()))
