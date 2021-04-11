"""Squal Logger"""
import logging


class Logger:
    """Logger"""
    def __init__(self, name: str = 'Squall', node_ip: str = None) -> None:
        """
        Logger constructor

            Parameters:
                name (String): A logger name
                node_ip (String): This node's ip

            Returns:
                None
        """
        if node_ip is not None:
            name = f'{name}-{node_ip}'
        self.logger = logging.getLogger(name)
        self.level = logging.ERROR
        self.format = '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'

    def set_level(self, level) -> None:
        """ Set logger level"""
        self.level = level

    def set_format(self, log_format) -> None:
        """ Set logger format"""
        self.format = log_format

    def get_logger(self) -> logging.Logger:
        """
        Get Logger

            Returns:
                logger (Logger)
        """
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(self.format)
        con = logging.StreamHandler()
        con.setLevel(level=logging.INFO)
        con.setFormatter(formatter)
        self.logger.addHandler(con)

        return self.logger
