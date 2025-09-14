#!/usr/bin/env python3
"""
Kerberos.io Multi-Agent CLI Tool (Lite Version)
Cross-platform command-line interface with minimal dependencies
"""

import os
import sys
import json
import subprocess
import ipaddress
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse

try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
    import yaml

try:
    import psutil
except ImportError:
    print("Installing psutil for system checks...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

class Colors:
    """ANSI color codes for cross-platform terminal colors"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable(cls):
        """Disable colors for Windows compatibility"""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.PURPLE = cls.CYAN = cls.WHITE = cls.NC = ''

# Disable colors on Windows unless in a compatible terminal
if os.name == 'nt' and not os.getenv('ANSICON') and not os.getenv('WT_SESSION'):
    Colors.disable()

def print_status(msg: str):
    print(f"{Colors.GREEN}[✓]{Colors.NC} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}[✗]{Colors.NC} {msg}")

def print_header(msg: str):
    print(f"{Colors.BLUE}[KERBEROS]{Colors.NC} {msg}")

def print_info(msg: str):
    print(f"{Colors.CYAN}[i]{Colors.NC} {msg}")

class KerberosManager:
    """Simplified Kerberos manager with minimal dependencies"""
    
    def __init__(self, config_file: str = "config.yml"):
        self.config_file = config_file
        self.compose_file = "docker-compose.yml"
        self.config = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration file"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            print_error(f"Configuration file '{self.config_file}' not found!")
            sys.exit(1)
            
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return self.config
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML in config file: {e}")
            sys.exit(1)
    
    def generate_ip_list(self, start_ip: str, end_ip: str) -> List[str]:
        """Generate list of IP addresses from range"""
        try:
            start = ipaddress.IPv4Address(start_ip)
            end = ipaddress.IPv4Address(end_ip)
            
            if start > end:
                raise ValueError("Start IP must be less than or equal to end IP")
                
            ip_list = []
            current = start
            while current <= end:
                ip_list.append(str(current))
                current = ipaddress.IPv4Address(int(current) + 1)
                
            return ip_list
        except ipaddress.AddressValueError as e:
            print_error(f"Invalid IP address: {e}")
            sys.exit(1)
        except ValueError as e:
            print_error(f"IP range error: {e}")
            sys.exit(1)
    
    def generate_compose_file(self) -> int:
        """Generate docker-compose.yml from configuration"""
        config = self.load_config()
        
        # Extract configuration values
        global_config = config.get('global', {})
        camera_config = config.get('cameras', {})
        docker_config = config.get('docker', {})
        custom_env = config.get('custom_environment', {})
        
        # Required values
        kerberos_image = global_config.get('kerberos_image', 'kerberos/agent:latest')
        network_name = global_config.get('network_name', 'kerberos-network')
        config_base_path = global_config.get('config_base_path', './configs')
        recordings_base_path = global_config.get('recordings_base_path', './recordings')
        
        ip_range = camera_config.get('ip_range', {})
        start_ip = ip_range.get('start')
        end_ip = ip_range.get('end')
        
        if not start_ip or not end_ip:
            print_error("IP range (start and end) must be specified in config")
            sys.exit(1)
        
        connection = camera_config.get('connection', {})
        protocol = connection.get('protocol', 'rtsp')
        port = connection.get('port', 554)
        username = connection.get('username', 'admin')
        password = connection.get('password', 'password')
        stream_path = connection.get('stream_path', '/stream1')
        
        web_port_start = docker_config.get('web_port_start', 8080)
        rtmp_port_start = docker_config.get('rtmp_port_start', 1935)
        restart_policy = docker_config.get('restart_policy', 'unless-stopped')
        
        # Generate IP list
        ip_list = self.generate_ip_list(start_ip, end_ip)
        camera_count = len(ip_list)
        
        print_status(f"Generating configuration for {camera_count} cameras")
        print_info(f"IP range: {start_ip} → {end_ip}")
        
        # Build compose structure
        compose_data = {
            'version': '3.8',
            'networks': {
                network_name: {
                    'driver': 'bridge'
                }
            },
            'services': {}
        }
        
        # Create directories
        Path(config_base_path).mkdir(parents=True, exist_ok=True)
        Path(recordings_base_path).mkdir(parents=True, exist_ok=True)
        
        # Generate services
        for i, camera_ip in enumerate(ip_list):
            camera_name = f"camera-{camera_ip.replace('.', '-')}"
            rtsp_url = f"{protocol}://{username}:{password}@{camera_ip}:{port}{stream_path}"
            web_port = web_port_start + i
            rtmp_port = rtmp_port_start + i
            
            print_info(f"Configuring {camera_name} - Web: {web_port}, RTMP: {rtmp_port}")
            
            # Create camera-specific directories
            camera_config_dir = Path(config_base_path) / camera_name
            camera_recordings_dir = Path(recordings_base_path) / camera_name
            camera_config_dir.mkdir(exist_ok=True)
            camera_recordings_dir.mkdir(exist_ok=True)
            
            # Service definition
            service = {
                'image': kerberos_image,
                'container_name': camera_name,
                'restart': restart_policy,
                'networks': [network_name],
                'ports': [
                    f"{web_port}:80",
                    f"{rtmp_port}:1935"
                ],
                'volumes': [
                    f"{config_base_path}/{camera_name}:/home/agent/data/config",
                    f"{recordings_base_path}/{camera_name}:/home/agent/data/recordings"
                ],
                'environment': {
                    'AGENT_NAME': camera_name,
                    'AGENT_CAPTURE_IPCAMERA_RTSP': rtsp_url,
                    'AGENT_CAPTURE_IPCAMERA_SUB_RTSP': rtsp_url,
                    'AGENT_STREAM_WEBRTC': 'true',
                    'AGENT_STREAM_RECORDING': 'true',
                    **custom_env
                }
            }
            
            # Add resource limits if specified
            limits = docker_config.get('limits', {})
            if limits:
                deploy_resources = {}
                if 'memory' in limits:
                    deploy_resources['memory'] = limits['memory']
                if 'cpus' in limits:
                    deploy_resources['cpus'] = limits['cpus']
                
                if deploy_resources:
                    service['deploy'] = {'resources': {'limits': deploy_resources}}
            
            compose_data['services'][camera_name] = service
        
        # Write compose file
        try:
            with open(self.compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, indent=2)
            
            print_status(f"Docker Compose file generated: {self.compose_file}")
            print_info(f"Services created: {camera_count}")
            print_info(f"Web ports: {web_port_start}-{web_port_start + camera_count - 1}")
            print_info(f"RTMP ports: {rtmp_port_start}-{rtmp_port_start + camera_count - 1}")
            
            return camera_count
            
        except Exception as e:
            print_error(f"Failed to write compose file: {e}")
            sys.exit(1)

    def run_docker_compose(self, command: List[str]) -> bool:
        """Run docker-compose command"""
        try:
            cmd = ['docker-compose'] + command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print_error(f"Command failed: {' '.join(cmd)}")
                if result.stderr:
                    print(result.stderr)
                return False
                
        except FileNotFoundError:
            print_error("Docker Compose not found. Please install Docker and Docker Compose.")
            return False
        except Exception as e:
            print_error(f"Error running command: {e}")
            return False

    def check_dependencies(self):
        """Check system dependencies"""
        print_header("Checking system dependencies...")
        
        # Check Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print_status(f"Python {python_version}")
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_status(f"Docker found")
            else:
                print_error("Docker not available")
        except FileNotFoundError:
            print_error("Docker not found")
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_status("Docker Compose found")
            else:
                print_error("Docker Compose not available")
        except FileNotFoundError:
            print_error("Docker Compose not found")
        
        # Check config file
        if Path(self.config_file).exists():
            print_status("Configuration file found")
        else:
            print_warning(f"Configuration file not found: {self.config_file}")

    def system_check(self):
        """Comprehensive system resources and capacity check"""
        print_header("🔍 System Resources Check")
        
        # Load configuration
        config = self.load_config()
        if not config:
            print_error("Cannot perform system check without valid configuration")
            return False
            
        # Calculate camera count
        try:
            cameras = config.get('cameras', {})
            ip_range = cameras.get('ip_range', {})
            start_ip = ip_range.get('start', '')
            end_ip = ip_range.get('end', '')
            
            if not start_ip or not end_ip:
                print_error("IP range not properly configured")
                return False
                
            ip_list = self.generate_ip_list(start_ip, end_ip)
            camera_count = len(ip_list)
            
        except Exception as e:
            print_error(f"Error calculating camera count: {e}")
            return False
        
        print_info(f"Checking capacity for {camera_count} cameras")
        
        # Calculate resource requirements
        requirements = self._calculate_resource_requirements(config, camera_count)
        
        # Get current system resources
        system_resources = self._get_system_resources()
        
        # Print current system status
        print(f"\n💻 System Resources:")
        print(f"   Memory: {system_resources['memory']['available_gb']:.1f} GB available / {system_resources['memory']['total_gb']:.1f} GB total")
        print(f"   CPU: {system_resources['cpu']['cores']} cores ({system_resources['cpu']['current_usage']:.1f}% current usage)")
        print(f"   Disk: {system_resources['disk']['free_gb']:.1f} GB free / {system_resources['disk']['total_gb']:.1f} GB total")
        
        # Print requirements
        print(f"\n📊 Estimated Requirements:")
        print(f"   Memory per agent: {requirements['memory_per_agent_mb']} MB")
        print(f"   Total memory needed: {requirements['total_memory_gb']:.1f} GB")
        print(f"   Estimated CPU usage: {requirements['total_cpu_percent']:.1f}%")
        print(f"   Daily storage: {requirements['daily_storage_gb']:.1f} GB/day")
        
        # Capacity check
        print(f"\n✅ Capacity Assessment:")
        
        memory_ok = system_resources['memory']['available_gb'] >= requirements['total_memory_gb']
        cpu_ok = requirements['total_cpu_percent'] <= 80
        storage_ok = True  # We'll just warn about storage
        
        print(f"   Memory: {'✅ OK' if memory_ok else '❌ INSUFFICIENT'}")
        if not memory_ok:
            shortage = requirements['total_memory_gb'] - system_resources['memory']['available_gb']
            print(f"      Need {shortage:.1f} GB more memory")
            
        print(f"   CPU: {'✅ OK' if cpu_ok else '⚠️  HIGH LOAD'}")
        if not cpu_ok:
            print(f"      Warning: {requirements['total_cpu_percent']:.1f}% estimated usage")
            
        # Check ports
        busy_ports = self._check_ports(config, camera_count)
        if busy_ports:
            print(f"   Ports: ⚠️  CONFLICTS DETECTED")
            for port in busy_ports[:5]:  # Show first 5
                print(f"      {port} is in use")
        else:
            print(f"   Ports: ✅ AVAILABLE")
            
        # Overall assessment
        if memory_ok and cpu_ok and not busy_ports:
            print_status("\n🎯 SYSTEM READY FOR DEPLOYMENT")
            return True
        else:
            print_warning("\n⚠️  DEPLOYMENT MAY HAVE ISSUES")
            if not memory_ok:
                print("   - Add more RAM or reduce camera count")
            if not cpu_ok:
                print("   - Monitor performance during operation")
            if busy_ports:
                print("   - Stop conflicting services or change ports")
            return False
    
    def _calculate_resource_requirements(self, config, camera_count):
        """Calculate estimated resource requirements"""
        
        # Base requirements per agent
        base_memory_mb = 256
        base_cpu_percent = 5
        
        # Additional based on features
        additional_memory = 0
        additional_cpu = 0
        
        # Recording adds overhead
        if config.get('cameras', {}).get('recording', {}).get('enabled', False):
            additional_memory += 128
            additional_cpu += 3
            
        # Streaming adds overhead
        if config.get('cameras', {}).get('stream', {}).get('enabled', False):
            additional_memory += 64
            additional_cpu += 2
            
        # Motion detection adds overhead
        if config.get('cameras', {}).get('motion_detection', {}).get('enabled', False):
            additional_memory += 32
            additional_cpu += 2
            
        memory_per_agent = base_memory_mb + additional_memory
        cpu_per_agent = base_cpu_percent + additional_cpu
        
        total_memory_mb = memory_per_agent * camera_count
        total_cpu_percent = cpu_per_agent * camera_count
        
        # Estimate daily storage (very rough)
        daily_storage_gb = 0
        if config.get('cameras', {}).get('recording', {}).get('enabled', False):
            # Rough estimate: 10MB per minute of recording
            # Assume motion triggers every 10 minutes, 40 seconds per trigger
            daily_recordings = 24 * 6  # 6 per hour
            mb_per_recording = 10 * (40/60)  # 40 seconds
            daily_storage_gb = (daily_recordings * mb_per_recording * camera_count) / 1024
            
        return {
            'memory_per_agent_mb': memory_per_agent,
            'total_memory_gb': total_memory_mb / 1024,
            'total_cpu_percent': total_cpu_percent,
            'daily_storage_gb': daily_storage_gb
        }
    
    def _get_system_resources(self):
        """Get current system resource information"""
        # Memory
        memory = psutil.virtual_memory()
        
        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Disk
        disk = psutil.disk_usage('/')
        
        return {
            'memory': {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'usage_percent': memory.percent
            },
            'cpu': {
                'cores': psutil.cpu_count(),
                'current_usage': cpu_usage
            },
            'disk': {
                'total_gb': disk.total / (1024**3),
                'free_gb': disk.free / (1024**3),
                'usage_percent': (disk.used / disk.total) * 100
            }
        }
        
    def _check_ports(self, config, camera_count):
        """Check if required ports are available"""
        import socket
        
        busy_ports = []
        web_port_start = config.get('docker', {}).get('web_port_start', 8080)
        rtmp_port_start = config.get('docker', {}).get('rtmp_port_start', 1935)
        
        # Check web ports
        for i in range(camera_count):
            port = web_port_start + i
            if self._is_port_busy(port):
                busy_ports.append(f"Web port {port}")
                
        # Check RTMP ports  
        for i in range(camera_count):
            port = rtmp_port_start + i
            if self._is_port_busy(port):
                busy_ports.append(f"RTMP port {port}")
                
        return busy_ports
        
    def _is_port_busy(self, port):
        """Check if a port is in use"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False
        except OSError:
            return True

def main():
    parser = argparse.ArgumentParser(
        description='Kerberos.io Multi-Agent CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate              Generate docker-compose.yml
  %(prog)s start                 Start all agents
  %(prog)s stop                  Stop all agents  
  %(prog)s status                Show agent status
  %(prog)s logs                  Show logs
  %(prog)s check                 Check dependencies
  %(prog)s syscheck              Check system resources and capacity
        """
    )
    
    parser.add_argument('--config', '-c', default='config.yml', 
                       help='Configuration file path (default: config.yml)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    subparsers.add_parser('generate', help='Generate docker-compose.yml from configuration')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start all Kerberos agents')
    start_parser.add_argument('--no-detach', action='store_true', help='Run in foreground')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop all Kerberos agents')
    
    # Restart command
    subparsers.add_parser('restart', help='Restart all Kerberos agents')
    
    # Status command
    subparsers.add_parser('status', help='Show status of all agents')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show logs from agents')
    logs_parser.add_argument('--service', '-s', help='Show logs for specific service')
    logs_parser.add_argument('--follow', '-f', action='store_true', help='Follow log output')
    
    # Update command
    subparsers.add_parser('update', help='Update agents to latest version')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove all containers and optionally volumes')
    cleanup_parser.add_argument('--volumes', action='store_true', help='Also remove volumes')
    cleanup_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    
    # Redeploy command
    subparsers.add_parser('redeploy', help='Regenerate configuration and restart all agents')
    
    # Check command
    subparsers.add_parser('check', help='Check system dependencies and requirements')
    
    # System check command  
    subparsers.add_parser('syscheck', help='Comprehensive system resources and capacity check')
    
    # Info command
    subparsers.add_parser('info', help='Show project information and configuration summary')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = KerberosManager(args.config)
    
    if args.command == 'check':
        manager.check_dependencies()
        
    elif args.command == 'syscheck':
        success = manager.system_check()
        if not success:
            print_info("\nTip: Use 'kerberos check' to verify Docker installation first")
        
    elif args.command == 'generate':
        print_header("Generating docker-compose.yml")
        count = manager.generate_compose_file()
        print_status(f"Successfully generated configuration for {count} cameras")
        print_info("Next: Run 'python kerberos_lite.py start' to deploy agents")
        
    elif args.command == 'start':
        # Check if compose file exists
        if not Path(manager.compose_file).exists():
            print_warning("Docker compose file not found. Generating...")
            manager.generate_compose_file()
        
        print_header("Starting Kerberos agents...")
        cmd = ['up']
        if not args.no_detach:
            cmd.append('-d')
            
        if manager.run_docker_compose(cmd):
            print_status("All agents started successfully!")
            try:
                config = manager.load_config()
                web_port = config.get('docker', {}).get('web_port_start', 8080)
                print_info(f"Web interfaces available starting from: http://localhost:{web_port}")
            except:
                pass
        
    elif args.command == 'stop':
        print_header("Stopping Kerberos agents...")
        if manager.run_docker_compose(['down']):
            print_status("All agents stopped successfully!")
        
    elif args.command == 'restart':
        print_header("Restarting Kerberos agents...")
        manager.run_docker_compose(['down'])
        manager.run_docker_compose(['up', '-d'])
        print_status("All agents restarted!")
        
    elif args.command == 'status':
        print_header("Agent Status")
        manager.run_docker_compose(['ps'])
        
    elif args.command == 'logs':
        cmd = ['logs']
        if args.follow:
            cmd.append('-f')
        if args.service:
            cmd.append(args.service)
        manager.run_docker_compose(cmd)
        
    elif args.command == 'update':
        print_header("Updating agents...")
        print_info("Pulling latest images...")
        manager.run_docker_compose(['pull'])
        print_info("Recreating containers...")
        manager.run_docker_compose(['up', '-d', '--force-recreate'])
        print_status("Update completed!")
        
    elif args.command == 'cleanup':
        print_header("Cleaning up Kerberos agents...")
        if not args.yes:
            response = input("This will remove all containers and data. Continue? (y/N): ")
            if not response.lower().startswith('y'):
                print_info("Cleanup cancelled.")
                return
        
        cmd = ['down']
        if args.volumes:
            cmd.extend(['-v', '--remove-orphans'])
        
        if manager.run_docker_compose(cmd):
            print_status("Cleanup completed!")
        
    elif args.command == 'redeploy':
        print_header("Redeploying agents...")
        manager.run_docker_compose(['down'])
        manager.generate_compose_file()
        manager.run_docker_compose(['up', '-d'])
        print_status("Redeployment completed!")
        
    elif args.command == 'info':
        try:
            config = manager.load_config()
            print_header("Kerberos.io Multi-Agent Configuration")
            
            # Global settings
            global_config = config.get('global', {})
            print(f"Kerberos Image: {global_config.get('kerberos_image', 'N/A')}")
            print(f"Network Name: {global_config.get('network_name', 'N/A')}")
            print(f"Config Path: {global_config.get('config_base_path', 'N/A')}")
            print(f"Recordings Path: {global_config.get('recordings_base_path', 'N/A')}")
            
            # Camera settings
            cameras = config.get('cameras', {})
            ip_range = cameras.get('ip_range', {})
            if ip_range:
                start_ip = ip_range.get('start', 'N/A')
                end_ip = ip_range.get('end', 'N/A')
                print(f"IP Range: {start_ip} → {end_ip}")
                
                # Calculate camera count
                try:
                    ip_list = manager.generate_ip_list(start_ip, end_ip)
                    print(f"Camera Count: {len(ip_list)}")
                except:
                    pass
            
            # Docker settings
            docker_config = config.get('docker', {})
            print(f"Web Port Start: {docker_config.get('web_port_start', 'N/A')}")
            print(f"RTMP Port Start: {docker_config.get('rtmp_port_start', 'N/A')}")
            
            # Timezone
            custom_env = config.get('custom_environment', {})
            print(f"Timezone: {custom_env.get('TZ', 'N/A')}")
            
        except Exception as e:
            print_error(f"Error reading configuration: {e}")

if __name__ == '__main__':
    main()
