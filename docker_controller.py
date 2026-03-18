import random
import time
import socket

import docker
from docker.errors import DockerException

class DockerController: # don't Change class name and method names
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException:
            self.client = None
            print("Docker is currently unavailable.")

    def is_free(self, port, host='0.0.0.0'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            return True
        except socket.error:
            return False
        finally:
            sock.close()
    def find_port(self):
        attempts = 50
        for _ in range(attempts):
            port = random.randint(8000, 9000)
            if self.is_free(port):
                return port
        for port in range(8000, 9001):
            if self.is_free(port):
                return port
        return None


    def create(self, name, image, cpu, memory, user):

        if not self.client:
            return{"success": False, "error": "Docker unavailable"}

        if not isinstance(name, str):
            return{"success": False, "error": "name must be string!"}
        if len(name) == 0:
            return{"success" : False, "error": "the field cannot be empty!"}

        if not isinstance(cpu, int):
            if isinstance(cpu, str):
                try:
                    cpu = float(cpu)
                except Exception as e:
                    return {"success": False, "error": "enter CPU as a number!"}
            else:
                return {"success": False, "error": "enter CPU as a number!"}
        if cpu <= 0:
            return {"success": False, "error" : "enter CPU!" }

        dock_cpu = int(cpu * 1e9)

        if not isinstance(user, str):
            return{"success" : False, "error": "user must be string format!"}
        if len(user) == 0:
            return{"success": False, "error": "user cannot be empty!"}

        if not isinstance(image, str):
            return{"success": False, "error": "image must be string format!"}
        try: #downloading img
            self.client.images.pull(image)
        except Exception as e:
            return {"success": False, "error": str(e)}

        if not isinstance(memory, str):
            return {"success": False, "error": "Memory accepts string format!"}
        try:
            if memory[-2:]=="GB":
                docker_memory = int(memory[:-2]) * 1024**3
            elif memory[-2:] == "MB":
                docker_memory = int(memory[:-2]) * 1024**2
            else:
                return {"success": False, "error": "Data entry error"}
        except Exception as e:
            return {"success": False, "error": "Data entry error"}

        port_ssh = self.find_port()
        if port_ssh is None:
            return {"success": False, "error": "At the moment all ports are busy"}


        try:
            container = self.client.containers.create(
                name = name,
                image = image,
                detach = True,
                nano_cpus = dock_cpu,
                mem_limit = docker_memory,
                labels = {"user": user},
                ports = {'22/tcp': port_ssh}
            )
            container.start()

            return {
                "success": True,
                "id": container.id,
                "name": name,
                "created_at": time.time(),
                "port": port_ssh
            }
        except Exception as e:
            return {
                "success": False,"error": f"Error: {str(e)}"}
    def stop(self, container_id):

        if not self.client:
            return {"success": False, "error": "Docker not available!"}

        if not isinstance(container_id, str) or len(container_id) == 0:
            return {"success": False, "error": "Invalid container id!"}

        try:
            container = self.client.containers.get(container_id)
            status = container.status

            if status == "stopped":
                return {"success": True, "message": "Container stopped"}
            if status == "running":
                container.stop(timeout=10)
                print("Container is stopped")
                return {"success": True}
            else:
                return{"success": False, "error": "Problem, container not stopped"}
        except docker.errors.NotFound:
            return {"success": False, "error": "This container is not found!"}

    def start(self, container_id):

        if not self.client:
            return {"success": False, "error": "Docker not available"}

        if not isinstance(container_id, str) or len(container_id) == 0:
            return {"success": False, "error": "Invalid container id!"}

        try:
            container = self.client.containers.get(container_id)
            status = container.status

            if status == "running":
                return {"success": True}
            else:
                container.start()
                print("Container is running")
                return {"success": True}
        except docker.errors.NotFound:
            return {"success": False, "error": "This container is not found!"}


    def get_status(self, container_id):

        try:
            container = self.client.containers.get(container_id)
            status = container.status
            possible_status = {
                "running" : "running",
                "exited" :  "stopped",
                "paused": "stopped",
                "restarting": "running",
                "created": "stopped",
                "dead": "unknown"
            }
            return possible_status.get(status, "unknown")
        except docker.errors.NotFound:
            return "unknown"
        except Exception as e:
            print(f"Unexpected error in get_status: {e}")
            return "unknown"