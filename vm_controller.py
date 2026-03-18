import subprocess
import os
import uuid
import time
import signal
import socket

class VMController:

    def __init__(self):
        os.makedirs("./vms", exist_ok=True)
        self.vms = {}

    def _parse_memory(self, memory):
        """Convert memory string to MB"""
        if isinstance(memory, str):
            if memory.endswith("GB"):
                return int(memory[:-2]) * 1024
            if memory.endswith("MB"):
                return int(memory[:-2])
        return int(memory)
    
    def _is_port_free(self, port):
        """Check if port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) != 0
    
    def _find_port(self, start=10000, end=15000):
        """Find first free port in range"""
        for port in range(start, end):
            if self._is_port_free(port):
                return port
        return None

    def create(self, name, os_type, cpu, memory, user):
        try:
            # Basic validation
            if not isinstance(name, str) or not name:
                return {'success': False, 'error': 'Invalid name'}
            
            if not isinstance(cpu, int) or cpu <= 0:
                return {'success': False, 'error': 'Invalid CPU'}
            
            if not isinstance(user, str) or not user:
                return {'success': False, 'error': 'Invalid user'}

            vm_id = "vm-" + str(uuid.uuid4())[:8]
            created_at = time.time()

            memory_mb = self._parse_memory(memory)
            disk_path = f"./vms/{vm_id}.qcow2"

            # Create VM disk
            subprocess.run(
                ["qemu-img", "create", "-f", "qcow2", disk_path, "10G"],
                check=True
            )

            # Find free SSH port
            ssh_port = self._find_port()
            if ssh_port is None:
                return {'success': False, 'error': 'No free ports available'}

            # Start VM
            proc = subprocess.Popen([
                "qemu-system-x86_64",
                "-m", str(memory_mb),
                "-smp", str(cpu),
                "-drive", f"file={disk_path},format=qcow2",
                "-netdev", f"user,id=net0,hostfwd=tcp::{ssh_port}-:22",
                "-device", "virtio-net-pci,netdev=net0",
                "-daemonize",
                "-display", "none"
            ])

            self.vms[vm_id] = {
                "name": name,
                "os_type": os_type,
                "cpu": cpu,
                "memory_mb": memory_mb,
                "disk_path": disk_path,
                "ssh_port": ssh_port,
                "pid": proc.pid,
                "status": "running",
                "user": user
            }

            print(f"[VM] Created {vm_id} on port {ssh_port}")

            return {
                'success': True,
                'id': vm_id,
                'name': name,
                'created_at': created_at,
                'ssh_port': ssh_port 
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def stop(self, vm_id):
        try:
            if vm_id not in self.vms:
                return {'success': False, 'error': 'VM not found'}

            vm = self.vms[vm_id]

            if vm["status"] == "stopped":
                return {'success': True}

            pid = vm.get("pid")
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"[VM] Stopped {vm_id} by PID {pid}")
                except ProcessLookupError:
                    pass

            disk_path = vm["disk_path"]
            result = subprocess.run(
                ["pgrep", "-f", disk_path],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                for pid_line in result.stdout.strip().split('\n'):
                    try:
                        os.kill(int(pid_line), signal.SIGTERM)
                    except:
                        pass

            vm["status"] = "stopped"
            vm["pid"] = None

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def start(self, vm_id):
        try:
            if vm_id not in self.vms:
                return {'success': False, 'error': 'VM not found'}

            vm = self.vms[vm_id]

            if vm["status"] == "running":
                return {'success': False, 'error': 'VM already running'}

            # Start VM with saved parameters
            proc = subprocess.Popen([
                "qemu-system-x86_64",
                "-m", str(vm["memory_mb"]),
                "-smp", str(vm["cpu"]),
                "-drive", f"file={vm['disk_path']},format=qcow2",
                "-netdev", f"user,id=net0,hostfwd=tcp::{vm['ssh_port']}-:22",
                "-device", "virtio-net-pci,netdev=net0",
                "-daemonize",
                "-display", "none"
            ])

            vm["pid"] = proc.pid
            vm["status"] = "running"

            print(f"[VM] Started {vm_id} on port {vm['ssh_port']}")

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_status(self, vm_id):
        try:
            if vm_id not in self.vms:
                return False

            vm = self.vms[vm_id]
            pid = vm.get("pid")

            if not pid:
                # Try to find by disk path
                result = subprocess.run(
                    ["pgrep", "-f", vm["disk_path"]],
                    capture_output=True,
                    text=True
                )
                is_running = bool(result.stdout.strip())
                vm["status"] = "running" if is_running else "stopped"
                return is_running

            # Check if process exists
            try:
                os.kill(pid, 0)
                vm["status"] = "running"
                return True
            except OSError:
                vm["status"] = "stopped"
                vm["pid"] = None
                return False

        except Exception:
            return False