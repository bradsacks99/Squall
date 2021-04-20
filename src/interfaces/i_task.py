from abc import ABCMeta, abstractmethod


class ITask:
    """Task interface"""

    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return "1.0"

    @abstractmethod
    def set_logger(self, logger): raise NotImplementedError

    @abstractmethod
    def set_database(self, database): raise NotImplementedError

    @abstractmethod
    def set_datastore(self, datastore): raise NotImplementedError

    @abstractmethod
    def get_uid(self): raise NotImplementedError

    @abstractmethod
    def get_name(self): raise NotImplementedError

    @abstractmethod
    def get_desc(self): raise NotImplementedError

    @abstractmethod
    def get_frequency(self): raise NotImplementedError

    @abstractmethod
    def get_config(self): raise NotImplementedError

    @abstractmethod
    async def run(self): raise NotImplementedError
