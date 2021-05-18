"""Squall task manager"""
import os
import pkgutil
import importlib
import asyncio
from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.job import Job
# pylint: disable=import-error
import tasks

class ManageTasks:
    """ManageTasks"""

    def __init__(self) -> None:
        """
        ManageTasks constructor

            Parameters:
                logger (Logger): A logger instance

            Returns:
                None
        """

        self.logger = None
        self.datastore = None
        self.network_data = None
        self.pkg_dir = 'tasks'
        self.user_pkg_dir = 'user_tasks'
        self.jobs = {}

        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 100
        }

        self.scheduler = AsyncIOScheduler(
            event_loop=asyncio.get_running_loop(),
            job_defaults=job_defaults,
            jobstores=jobstores,
            timezone=utc
        )

    def set_logger(self, logger) -> None:
        """ Set logger"""
        self.logger = logger

    def set_datastore(self, datastore) -> None:
        """" Set Data Store"""
        self.datastore = datastore

    def set_network_data(self, network_data: dict = None) -> None:
        """
        set_network_data: Set's network data needed by jobs

            Returns:
                 None

            Raises
                ValueError: if network_data is not valid
        """
        if network_data is None or not isinstance(network_data, dict):
            raise ValueError("network_data must be a dictionary")
        self.network_data = network_data

    async def run_tasks(self) -> None:
        """
        run_tasks: finds and runs the tasks

            Returns:
                 None
        """

        packages = [self.pkg_dir]
        if os.path.exists(self.user_pkg_dir):
            packages.append(self.user_pkg_dir)

        # pylint: disable=unused-variable
        for (module_loader, name, ispkg) in pkgutil.iter_modules(packages):
            self.logger.info(f"Getting class: {name}")
            try:
                a_class = self.get_class(name)
            except ModuleNotFoundError as err:
                self.logger.error(err)
                continue
            except AttributeError as err:
                self.logger.error(err)
                continue
            except ValueError as err:
                self.logger.error(err)
                continue

            frequency = a_class.get_frequency()

            if hasattr(a_class, 'datastore'):
                a_class.datastore = self.datastore

            keyword_args = {
                'logger': self.logger,
                'network_data': self.network_data
            }

            try:
                keyword_args = a_class.get_config()
                keyword_args['network_data'] = self.network_data
            except NotImplementedError:
                self.logger.info("Config not implemented for " + str(a_class))

            job_id = a_class.get_uid()

            job = self.set_monitoring_task(a_class, frequency, job_id, keyword_args)

            self.jobs[job_id] = {
                'job': job,
                'name': a_class.get_name(),
                'desc': a_class.get_desc(),
                'frequency': frequency
            }
            # store jobs in data store
            self.datastore.set(job_id, {
                'uid': job_id,
                'name': a_class.get_name(),
                'desc': a_class.get_desc(),
                'frequency': frequency
            })

        # start the scheduler
        self.scheduler.start()

    def set_monitoring_task(self, the_class, frequency, job_id, keyword_args) -> Job:
        """
        set_monitoring_task: adds a monitoring task to the job scheduler

            Parameters:
                the_class (Task): A Task class
                frequency (int): The frequency of the task
                job_id (uuid4): The id of the job
                keyword_arks (dict): keyword arguements to pass to the job

            Returns:
                Job
        """

        self.logger.info(f"setting set_monitoring_task with frequency {frequency}")

        job = self.scheduler.add_job(
            the_class.run,
            'interval',
            seconds=frequency,
            kwargs=keyword_args,
            id=job_id,
            replace_existing=False,
            max_instances=1
        )

        return job

    async def update_job(self, uid: str = None, update_data: dict = None) -> None:
        """
        update_job: Update a job instance

            Parameters:
                uid (string): A job uid
                update_data (dict): updated job data

            Raises:
                ValueError: if input is invalid
        """
        if uid is None or not isinstance(uid, str):
            raise ValueError('uid must be a string')
        if update_data is None or not isinstance(update_data, dict):
            raise ValueError('update_data must be a dict')

        self.logger.info(f"Modifying job {uid}, setting frequency {update_data['frequency']}")

        self.jobs[uid]['job'] = self.scheduler.reschedule_job(
            uid,
            trigger='interval',
            seconds=update_data['frequency']
        )

    def get_class(self, name: str = None) -> object:
        """
        get_class: gets an instance of a task class

            Parameters:
                name (string): A class name

            Returns:
                object

            Raises:
                ValueError: if input is invalid
                ModuleNotFoundError: raised if module cannot be imported
                AttributeError: raised if classname is not a valid attribute
        """
        if name is None or not isinstance(name, str):
            raise ValueError('name must be a string')

        try:
            module = importlib.import_module(f"{self.pkg_dir}.{name}")
        except ModuleNotFoundError:
            module = importlib.import_module(f"{self.user_pkg_dir}.{name}")
        except ModuleNotFoundError as err:
            self.logger.error("Module could not be imported")
            raise err

        bits = name.split('_')
        class_name = ''.join([x.capitalize() for x in bits])
        try:
            a_class = getattr(module, class_name)
        except AttributeError as err:
            self.logger.error(f"can't get class: {class_name}")
            raise err
        a_instance = a_class()

        return a_instance

    async def shutdown(self) -> None:
        """shutdown: shutdown the job scheduler"""
        self.logger.info("Shutting down job scheduler")
        await self.scheduler.remove_all_jobs()
        await self.scheduler.shutdown()
        await asyncio.sleep(1)
