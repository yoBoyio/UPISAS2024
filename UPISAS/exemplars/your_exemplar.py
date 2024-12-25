import pprint
import time
import logging
import docker  # Docker SDK for Python
from UPISAS.exemplar import Exemplar

pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class StepExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """

    def __init__(self, auto_start: "Whether to immediately start the container after creation" = False, container_name="fas2"):
        self.container_name = container_name
        self.docker_client = docker.from_env()  # Initialize Docker client

        # Define Docker container parameters
        my_docker_kwargs = {
            "name": container_name,
            "image": "http-server-group-3_2",
            "ports": {8080: 8080},
            "network": "fas-net"
        }

        # Base endpoint for the application running inside the container
        base_endpoint = "http://localhost:8080"

        # Check if the container already exists
        existing_container = self.get_existing_container()

        if existing_container:
            logging.info(f"Using existing container: {container_name}")
            self.exemplar_container = existing_container

            # Set the base_endpoint explicitly since super().__init__() isn't called
            self.base_endpoint = base_endpoint

            # If auto_start is True, start the container if it is not already running
            if auto_start and existing_container.status != "running":
                logging.info(f"Starting container: {container_name}")
                existing_container.start()
        else:
            # Create a new container if it doesn't exist
            logging.info(f"Creating new container: {container_name}")
            super().__init__(base_endpoint, my_docker_kwargs, auto_start)

    def get_existing_container(self):
        """
        Check if the container with the specified name already exists.
        Returns the container object if it exists, or None otherwise.
        """
        try:
            return self.docker_client.containers.get(self.container_name)
        except docker.errors.NotFound:
            logging.info(f"Container {self.container_name} not found.")
            return None

    def start_run(self):
        """
        Start the application inside the container.
        """
        logging.info(f"Starting run inside container: {self.container_name}")
        self.exemplar_container.exec_run(
            "uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload", detach=True
        )

    def stop(self):
        """
        Stop the container if it goes into an exception.
        """
        logging.info(f"Stopping container: {self.container_name}")
        self.stop_container()
