"""Squal Main entry point"""
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from logger import Logger
from datastore import Datastore, Tasks
from manage_tasks import ManageTasks
from utils import get_ip, get_network, get_cluster_nodes
from aiofile import async_open

squall_node_ip = get_ip()
squall_network = get_network()
logger = Logger(name='Squall', node_ip=squall_node_ip).get_logger()

squall_cluster_members = get_cluster_nodes(squall_node_ip)
logger.info(f"Squall node ip is: {squall_node_ip}")
logger.info(f"Squall subnet is: {squall_network}")
logger.info(f"Squall cluster members are: {squall_cluster_members}")

app = FastAPI(
    title="Squall",
    description="Security Monitoring and Scanning Container for Kubernetes",
    version="0.1.0",
    static_directory='static',
    swagger_static={
        "favicon": 'favicon.ico',
    },
)

app.mount("/static", StaticFiles(directory="static"), name="static")

datastore = Datastore(f'{squall_node_ip}', '4321', squall_cluster_members)
datastore.set_logger(logger)
manage_tasks = ManageTasks()
manage_tasks.set_logger(logger)
manage_tasks.set_datastore(datastore)
manage_tasks.set_network_data({'node_ip': squall_node_ip, 'subnet': squall_network})


@app.on_event("startup")
async def startup_event():
    """ Startup """
    logger.info("Starting up Squall")

    logger.info("Starting tasks")
    await manage_tasks.run_tasks()


@app.on_event("shutdown")
async def shutdown_event():
    """ Shutdown """
    logger.info("Shutting down Squall")

    logger.info("Stopping tasks")
    await manage_tasks.shutdown()


@app.get("/tasks/", response_model=List[Tasks])
async def get_tasks():
    """
    Get tasks: gets a list of tasks
        Returns:
            Tasks (list)
    """

    return await datastore.fetch_all_jobs()


@app.get("/tasks/{uid}", response_model=Tasks)
async def get_task(uid: str):
    """
    Get task: gets a task
        Parameters:
            uid (string): a uid of a task
        Returns:
            Task (Object)
        Raises:
            HTTPException: raised if task is not found for uid
    """
    try:
        response = await datastore.fetch_one_job(uid)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    return response


@app.patch("/tasks/{uid}", response_model=Tasks)
async def patch_task(uid: str, task: Tasks):
    """
    Update task: updates a task
        Parameters:
            uid (string): a uid of a task
            task (Object): a partial or complete Task object
        Returns:
            Task (Object)
        Raises:
            HTTPException: raised if task is not found for uid
    """
    patch_data = task.dict(exclude_unset=True)
    try:
        response = await datastore.update_job(uid, patch_data)
        await manage_tasks.update_job(uid, patch_data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input")
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")

    return response


@app.get("/license", response_class=PlainTextResponse)
async def show_license():
    """
    License: view the Squall license
    """
    license_file = 'LICENSE'
    if not os.path.exists(license_file):
        logger.info("Looks like we're running local. Try the root directory of Squall")
        license_file = '../LICENSE'
    if not os.path.exists(license_file):
        raise HTTPException(status_code=404, detail="License not found")
    async with async_open(license_file, 'r') as fh:
        output = await fh.read()
    return output
