import pprint, time
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class StepExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """

    def __init__(self, auto_start: " Whether to immediately start the container after creation" =False , container_name = "fasdfas2"):
        my_docker_kwargs = {
            "name":  container_name,
            "image": "http-server-group-3-2",
            "ports" : {8080: 8080},
            "network": "fas-net" 
            }

        super().__init__("http://localhost:8080", my_docker_kwargs, auto_start)

    def start_run(self):
        self.exemplar_container.exec_run("uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload", detach=True)

    # stop the container if it goes to except
    def stop(self):
       self.stop_container()

