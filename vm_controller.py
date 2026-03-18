import subprocess
import os
import uuid
import time
import signal


class VMController:  # Don't change class name and method names.

    def __init__(self):
        """
        Initialize the VM controller
        Task: Create directory for VM files (./vms)
        """
        os.makedirs("./vms", exist_ok=True)

        # Local runtime storage of VM configs
        self.vms = {}

    def _parse_memory(self, memory):
        """Convert memory string to MB"""
        if memory.endswith("GB"):
            return int(memory[:-2]) * 1024
        if memory.endswith("MB"):
            return int(memory[:-2])
        return int(memory)

    def create(self, name, os_type, cpu, memory, user):
        """
        Create a new virtual machine
        """
        try:
            vm_id = "vm-" + str(uuid.uuid4())[:8]
            created_at = time.time()

            memory_mb = self._parse_memory(memory)

            disk_path = f"./vms/{vm_id}.qcow2"

            # Create VM disk
            subprocess.run(
                ["qemu-img", "create", "-f", "qcow2", disk_path, "10G"],
                check=True
            )

            # Random SSH port
            ssh_port = 10000 + int(uuid.uuid4().int % 5000)

            # Start VM
            subprocess.Popen([
                "qemu-system-x86_64",
                "-m", str(memory_mb),
                "-smp", str(cpu),
                "-drive", f"file={disk_path},format=qcow2",
                "-netdev", f"user,id=net0,hostfwd=tcp::{ssh_port}-:22",
                "-device", "virtio-net-pci,netdev=net0",
                "-daemonize",
                "-display", "none"
            ])

            # Save config locally
            self.vms[vm_id] = {
                "name": name,
                "os_type": os_type,
                "cpu": cpu,
                "memory_mb": memory_mb,
                "disk_path": disk_path,
                "ssh_port": ssh_port,
                "status": "running"
            }

            return {
                'success': True,
                'id': vm_id,
                'name': name,
                'created_at': created_at
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def stop(self, vm_id):
        """
        Stop a virtual machine
        """

        try:

            if vm_id not in self.vms:
                return {'success': False, 'error': 'VM not found'}

            disk_path = self.vms[vm_id]["disk_path"]

            result = subprocess.run(
                ["pgrep", "-f", disk_path],
                capture_output=True,
                text=True
            )

            if result.stdout:
                pid = result.stdout.strip().split("\n")[0]
                os.kill(int(pid), signal.SIGTERM)

            self.vms[vm_id]["status"] = "stopped"

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def start(self, vm_id):
        """
        Start a virtual machine
        """

        try:

            if vm_id not in self.vms:
                return {'success': False, 'error': 'VM not found'}

            vm = self.vms[vm_id]

            if vm["status"] == "running":
                return {'success': False, 'error': 'VM already running'}

            subprocess.Popen([
                "qemu-system-x86_64",
                "-m", str(vm["memory_mb"]),
                "-smp", str(vm["cpu"]),
                "-drive", f"file={vm['disk_path']},format=qcow2",
                "-netdev", f"user,id=net0,hostfwd=tcp::{vm['ssh_port']}-:22",
                "-device", "virtio-net-pci,netdev=net0",
                "-daemonize",
                "-display", "none"
            ])

            vm["status"] = "running"

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_status(self, vm_id):
        """
        Check if VM is running
        """

        try:

            if vm_id not in self.vms:
                return False

            disk_path = self.vms[vm_id]["disk_path"]

            result = subprocess.run(
                ["pgrep", "-f", disk_path],
                capture_output=True,
                text=True
            )

            running = bool(result.stdout.strip())

            self.vms[vm_id]["status"] = "running" if running else "stopped"

            return running

        except Exception:
            return False