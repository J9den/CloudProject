import subprocess
import os



class VMController: #Don't change class name and method names.

    def __init__(self):
        """
        Initialize the VM controller
        Task: Create directory for VM files (./vms)
        """
        # Create ./vms directory if it doesn't exist
        # Example: os.makedirs("./vms", exist_ok=True)
        pass

    def create(self, name, os_type, cpu, memory, user):
        """
        Create a new virtual machine
        This method will be used by api.py

        Parameters (order must NOT be changed):
            name: instance name (string)
            os_type: operating system (string, e.g. "Ubuntu 22.04")
            cpu: number of CPU cores (integer)
            memory: memory size (string, e.g. "4GB")
            user: username (string)

        Return format (MUST be exactly like this):

            Success case:
            {
                'success': True,
                'id': 'vm-xxxxxx',           # generated unique ID
                'name': name,                 # same as input name
                'created_at': 1234567890.123  # timestamp
            }

            Failure case:
            {
                'success': False,
                'error': 'error message here'
            }

        Hints:
            - Use qemu-img to create disk: qemu-img create -f qcow2 disk.qcow2 10G
            - Use qemu-system-x86_64 to start VM
            - Generate unique ID with: str(uuid.uuid4())[:8]
        """
        # Remember to return the exact format shown above
        pass

    def stop(self, vm_id):
        """
        Stop a virtual machine

        Parameters:
            vm_id: virtual machine ID

        Return:
            {'success': True} OR {'success': False, 'error': 'error message'}

        """
        pass

    def start(self, vm_id):
        """
        Start a virtual machine

        Parameters:
            vm_id: virtual machine ID

        Return:
            {'success': True} OR {'success': False, 'error': 'error message'}

        Note: You may need to save VM configuration when creating
        """
        pass

    def get_status(self, vm_id):
        """
        Check if VM is running

        Parameters:
            vm_id: virtual machine ID

        Return:
            True (if running) or False (if stopped)

        Hint: Use pgrep -f vm_id to check if process exists
        """
        pass