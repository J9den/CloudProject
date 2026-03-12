import docker



class DockerController: # don't Change class name and method names
    def __init__(self):

        pass

    def create(self, name, image, cpu, memory, user):
        """
        Create a new container
        This method will be used by api.py

        Parameters (order must NOT be changed):
            name: instance name (string)
            image: docker image name (string, e.g. "ubuntu:22.04")
            cpu: number of CPU cores (integer)
            memory: memory size (string, e.g. "4GB")
            user: username (string)

        Return format (MUST be exactly like this):

            Success case:
            {
                'success': True,
                'id': 'container-xxxxxx',     # container ID
                'name': name,                  # same as input name
            }

            Failure case:
            {
                'success': False,
                'error': 'error message here'
            }
            then write your codes》
        """


        pass

    def stop(self, container_id):
        """
        Stop a container

        Parameters:
            container_id: container ID

        Return:
            {'success': True} OR {'success': False, 'error': 'error message'}
        """



        pass

    def start(self, container_id):
        """
        Start a container

        Parameters:
            container_id: container ID

        Return:
            {'success': True} OR {'success': False, 'error': 'error message'}
        """



        pass

    def get_status(self, container_id):
        """
                Get container status

                Parameters:
                    container_id: container ID

                Return:
                    'running' or 'stopped' or 'unknown'

                Hint: Check container.status
                """

        pass