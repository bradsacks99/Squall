import asyncio
from interfaces.i_task import ITask

class Sample3(ITask):

    def __init__(self):
        self.uid = "9f3a2199-a5d0-4e8a-9d23-a7f5a8d39c77"
        self.name = "Sample3"
        self.desc = "A Sample Task"
        self.frequency = 5
        self.logger = None
        self.database = None

    def get_uid(self):
        return self.uid

    def get_name(self):
        return self.name

    def get_desc(self):
        return self.desc

    def get_frequency(self):
        return self.frequency

    def set_database(self, database):
        self.database = database

    @staticmethod
    async def run(*args, **kwargs):
        network = kwargs.get('network', '0.0.0.0')
        logger =  kwargs.get('logger', None)
        #while True:
        logger.info(f"Checking network: {network} qqqq")
        await asyncio.sleep(1)



