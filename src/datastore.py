"""Squal Datastore"""
import pickle
from pydantic import BaseModel
from typing import Optional
from pysyncobj import SyncObj, SyncObjConf, replicated
from pickle import PicklingError, UnpicklingError


class Datastore(SyncObj):
    def __init__(self, address, port, member_addresses=None) -> None:
        """
        Datastore constructor

            Parameters:
                address (String): This squall node's address
                member_addresses (list): Member squall node addresses

            Returns:
                None
        """
        if member_addresses is None:
            member_addresses = []
        self.this_node_address = address
        self.port = port
        self.member_addresses = member_addresses
        this_node = f'{self.this_node_address}:{self.port}'
        member_nodes = [ f'{ip}:{self.port}' for ip in self.member_addresses ]
        cfg = SyncObjConf(dynamicMembershipChange=True, bindAddress=f'{self.this_node_address}:{self.port}')
        super(Datastore, self).__init__(this_node, member_nodes, cfg)
        self.__data = {}
        self.logger = None

    @replicated
    def set(self, key: str = None, value: dict = None) -> None:
        """
        set

            Parameters:
                key (String): key value
                value (dict): data

            Returns:
                None

            Raises:
                ValueError: if input is invalid
                PicklingError: if unable to picked value

        """
        if key is None or not isinstance(key, str):
            raise ValueError('Key must be a string')
        try:
            self.__data[key] = pickle.dumps(value)
        except PicklingError as err:
            self.logger.error(err)
            raise err

    @replicated
    def pop(self, key: str = None) -> dict:
        """
        pop

            Parameters:
                key (String): key value

            Returns:
                dict

            Raises:
                ValueError: if input is invalid
                UnpicklingError: if unable to picked value
        """
        if key is None or not isinstance(key, str):
            raise ValueError('Key must be a string')
        try:
            job = pickle.loads(self.__data.pop(key, None))
        except UnpicklingError as err:
            self.logger.error(err)
            raise err
        return job

    def get(self, key: str = None) -> dict:
        """
        get

            Parameters:
                key (String): key value [optional]

            Returns:
                dict

            Raises:
                UnpicklingError: if unable to picked value
        """
        if key is None:
            return self.__data
        try:
            job = pickle.loads(self.__data[key])
        except UnpicklingError as err:
            self.logger.error(err)
            raise err
        return job

    async def fetch_all_jobs(self) -> list:
        """
        Fetch All Jobs

            Returns:
                List

            Raises:
                UnpicklingError: could not deserialize
        """
        output = []
        data_dict = self.get()
        for job_id in data_dict.keys():
            try:
                job = pickle.loads(data_dict[job_id])
            except UnpicklingError as err:
                self.logger.error(err)
                raise err
            output.append(job)
        self.logger.info(output)
        return output

    async def fetch_one_job(self, uid: str = None) -> dict:
        """
        Fetch A Job

            Parameters:
                uid (string): a uid for a job

            Returns:
                dict

            Raises:
                ValueError: if input is invalid
                KeyError: raised if job is not found for uid

        """
        if uid is None or not isinstance(uid, str):
            raise ValueError('uid must be a string')
        try:
            data_dict = self.get(uid)
        except KeyError as err:
            self.logger.error(f"No job found with uid: {uid}")
            raise err
        return data_dict

    async def update_job(self, uid: str = None, update_data: dict = None) -> dict:
        """
        Update A Job

            Parameters:
                uid (string): a uid for a job
                update_data (dict): updated job data

            Returns:
                dict

            Raises:
                ValueError: if input is invalid
                KeyError: raised if job is not found for uid
        """
        if uid is None or not isinstance(uid, str):
            raise ValueError('uid must be a string')
        if update_data is None or not isinstance(update_data, dict):
            raise ValueError('update_data must be a dict')
        try:
            data_dict = self.get(uid)
            data_dict['frequency'] = update_data['frequency']
            self.set(uid, data_dict)
        except KeyError as err:
            self.logger.error(f"No job found with uid: {uid}")
            raise err

        return data_dict

    async def update_members(self, member_addresses=None) -> list:
        """
        Update members

            Parameters:
                member_addresses (list): Member squall node addresses

            Returns:
                list
        """
        if member_addresses is None:
            member_addresses = []
        this_node = {self.this_node_address}
        squall_nodes = set(member_addresses)

        current_members = set(self.member_addresses)

        # take this node out of the new set
        the_new_set = squall_nodes - this_node
        self.member_addresses = list(the_new_set)
        self.logger.info(f"current members: {self.member_addresses}")
        the_members = the_new_set & (current_members | squall_nodes)

        # get members to remove
        remove_members = current_members - the_members
        # get members to add
        add_members = the_members - current_members

        for member in add_members:
            self.logger.info(f'adding member: {member}')
            self.addNodeToCluster(f'{member}:{self.port}')

        for member in remove_members:
            self.logger.info(f'removing member: {member}')
            await self.removeNodeFromCluster(f'{member}:{self.port}')

        return list(the_members)

    def set_logger(self, logger) -> None:
        """
        Set logger

            Parameters:
                logger (Logger): a logger object

        """
        self.logger = logger


class Tasks(BaseModel):
    uid: str
    name: Optional[str] = None
    desc: Optional[str] = None
    frequency: int
