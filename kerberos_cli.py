#!/usr/bin/env python3
"""
Kerberos.io Multi-Agent CLI Tool
Cross-platform command-line interface for managing Kerberos.io agent deployments
"""

import os
import sys
import json
import subprocess
import ipaddress
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import docker

console = Console()

class KerberosManager:
    """Main class for managing Kerberos.io deployments"""
    
    def __init__(self, config_file: str = "config.yml"):
        self.config_file = config_file
        self.compose_file = "docker-compose.yml"
        self.project_name = "kerberos-swarms"
        self.docker_client = None
        self.config = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration file"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            raise click.ClickException(f"Configuration file '{self.config_file}' not found!")
            
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return self.config
        except yaml.YAMLError as e:
            raise click.ClickException(f"Invalid YAML in config file: {e}")
    
    def get_docker_client(self):
        """Get Docker client with error handling"""
        if self.docker_client is None:
            try:
                self.docker_client = docker.from_env()
                # Test connection
                self.docker_client.ping()
            except Exception as e:
                raise click.ClickException(f"Cannot connect to Docker: {e}")
        return self.docker_client
    
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
            raise click.ClickException(f"Invalid IP address: {e}")
        except ValueError as e:
            raise click.ClickException(f"IP range error: {e}")
    
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
            raise click.ClickException("IP range (start and end) must be specified in config")
        
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
        
        console.print(f"[green]Generating configuration for {camera_count} cameras[/green]")
        console.print(f"[blue]IP range: {start_ip} → {end_ip}[/blue]")
        
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
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating camera services...", total=camera_count)
            
            for i, camera_ip in enumerate(ip_list):
                camera_name = f"camera-{camera_ip.replace('.', '-')}"
                rtsp_url = f"{protocol}://{username}:{password}@{camera_ip}:{port}{stream_path}"
                web_port = web_port_start + i
                rtmp_port = rtmp_port_start + i
                
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
                progress.update(task, advance=1)
        
        # Write compose file
        try:
            with open(self.compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, indent=2)
            
            console.print(f"[green]✓ Docker Compose file generated: {self.compose_file}[/green]")
            console.print(f"[blue]Services created: {camera_count}[/blue]")
            console.print(f"[blue]Web ports: {web_port_start}-{web_port_start + camera_count - 1}[/blue]")
            console.print(f"[blue]RTMP ports: {rtmp_port_start}-{rtmp_port_start + camera_count - 1}[/blue]")
            
            return camera_count
            
        except Exception as e:
            raise click.ClickException(f"Failed to write compose file: {e}")

# CLI Command Groups
@click.group()
@click.option('--config', '-c', default='config.yml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Kerberos.io Multi-Agent CLI Tool
    
    Cross-platform command-line interface for managing Kerberos.io agent deployments.
    Deploy multiple agents based on IP ranges with automated Docker Compose generation.
    """
    ctx.ensure_object(dict)
    ctx.obj['manager'] = KerberosManager(config)

@cli.command()
@click.pass_context
def generate(ctx):
    """Generate docker-compose.yml from configuration"""
    manager = ctx.obj['manager']
    
    try:
        count = manager.generate_compose_file()
        console.print(Panel(
            f"[green]✓ Successfully generated configuration for {count} cameras[/green]\n"
            f"[blue]Next: Run 'kerberos start' to deploy agents[/blue]",
            title="Generation Complete",
            title_align="left"
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--detach/--no-detach', '-d', default=True, help='Run in background')
@click.pass_context
def start(ctx, detach):
    """Start all Kerberos agents"""
    manager = ctx.obj['manager']
    
    # Check if compose file exists
    if not Path(manager.compose_file).exists():
        console.print("[yellow]Docker compose file not found. Generating...[/yellow]")
        try:
            manager.generate_compose_file()
        except Exception as e:
            console.print(f"[red]Failed to generate compose file: {e}[/red]")
            sys.exit(1)
    
    try:
        console.print("[blue]Starting Kerberos agents...[/blue]")
        
        cmd = ['docker-compose', 'up']
        if detach:
            cmd.append('-d')
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✓ All agents started successfully![/green]")
            
            # Show port information
            try:
                config = manager.load_config()
                web_port = config.get('docker', {}).get('web_port_start', 8080)
                console.print(f"[blue]Web interfaces available starting from: http://localhost:{web_port}[/blue]")
            except:
                pass
        else:
            console.print(f"[red]Error starting agents: {result.stderr}[/red]")
            sys.exit(1)
            
    except FileNotFoundError:
        console.print("[red]Docker Compose not found. Please install Docker and Docker Compose.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.pass_context
def stop(ctx):
    """Stop all Kerberos agents"""
    try:
        console.print("[yellow]Stopping all agents...[/yellow]")
        
        result = subprocess.run(['docker-compose', 'down'], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✓ All agents stopped successfully![/green]")
        else:
            console.print(f"[red]Error stopping agents: {result.stderr}[/red]")
            sys.exit(1)
            
    except FileNotFoundError:
        console.print("[red]Docker Compose not found.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.pass_context
def restart(ctx):
    """Restart all Kerberos agents"""
    console.print("[yellow]Restarting all agents...[/yellow]")
    ctx.invoke(stop)
    ctx.invoke(start)

@cli.command()
@click.pass_context
def status(ctx):
    """Show status of all agents"""
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[blue]Agent Status:[/blue]")
            console.print(result.stdout)
        else:
            console.print("[red]Error getting status[/red]")
            
    except FileNotFoundError:
        console.print("[red]Docker Compose not found.[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option('--service', '-s', help='Show logs for specific service')
@click.option('--follow/--no-follow', '-f', default=False, help='Follow log output')
@click.pass_context
def logs(ctx, service, follow):
    """Show logs from agents"""
    try:
        cmd = ['docker-compose', 'logs']
        if follow:
            cmd.append('-f')
        if service:
            cmd.append(service)
            
        subprocess.run(cmd)
        
    except FileNotFoundError:
        console.print("[red]Docker Compose not found.[/red]")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.pass_context
def update(ctx):
    """Update agents to latest version"""
    try:
        console.print("[blue]Pulling latest images...[/blue]")
        subprocess.run(['docker-compose', 'pull'])
        
        console.print("[blue]Recreating containers...[/blue]")
        subprocess.run(['docker-compose', 'up', '-d', '--force-recreate'])
        
        console.print("[green]✓ Update completed![/green]")
        
    except Exception as e:
        console.print(f"[red]Error updating: {e}[/red]")

@cli.command()
@click.option('--volumes/--no-volumes', default=False, help='Also remove volumes')
@click.confirmation_option(prompt='This will remove all containers and data. Continue?')
@click.pass_context
def cleanup(ctx, volumes):
    """Remove all containers and optionally volumes"""
    try:
        cmd = ['docker-compose', 'down']
        if volumes:
            cmd.extend(['-v', '--remove-orphans'])
            
        subprocess.run(cmd)
        console.print("[green]✓ Cleanup completed![/green]")
        
    except Exception as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")

@cli.command()
@click.pass_context
def redeploy(ctx):
    """Regenerate configuration and restart all agents"""
    console.print("[blue]Redeploying agents...[/blue]")
    ctx.invoke(stop)
    ctx.invoke(generate)
    ctx.invoke(start)

@cli.command()
def check():
    """Check system dependencies and requirements"""
    console.print("[blue]Checking system dependencies...[/blue]")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"[green]✓[/green] Python {python_version}")
    
    # Check Docker
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        docker_version = docker_client.version()['Version']
        console.print(f"[green]✓[/green] Docker {docker_version}")
    except Exception:
        console.print("[red]✗[/red] Docker not available")
        return
    
    # Check Docker Compose
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓[/green] Docker Compose available")
        else:
            console.print("[red]✗[/red] Docker Compose not found")
    except FileNotFoundError:
        console.print("[red]✗[/red] Docker Compose not found")
    
    # Check config file
    if Path('config.yml').exists():
        console.print("[green]✓[/green] Configuration file found")
    else:
        console.print("[yellow]![/yellow] Configuration file not found (config.yml)")
    
    console.print("\n[green]System check completed![/green]")

@cli.command()
@click.pass_context
def info(ctx):
    """Show project information and configuration summary"""
    manager = ctx.obj['manager']
    
    try:
        config = manager.load_config()
        
        # Create info table
        table = Table(title="Kerberos.io Multi-Agent Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        # Global settings
        global_config = config.get('global', {})
        table.add_row("Kerberos Image", global_config.get('kerberos_image', 'N/A'))
        table.add_row("Network Name", global_config.get('network_name', 'N/A'))
        table.add_row("Config Path", global_config.get('config_base_path', 'N/A'))
        table.add_row("Recordings Path", global_config.get('recordings_base_path', 'N/A'))
        
        # Camera settings
        cameras = config.get('cameras', {})
        ip_range = cameras.get('ip_range', {})
        if ip_range:
            start_ip = ip_range.get('start', 'N/A')
            end_ip = ip_range.get('end', 'N/A')
            table.add_row("IP Range", f"{start_ip} → {end_ip}")
            
            # Calculate camera count
            try:
                ip_list = manager.generate_ip_list(start_ip, end_ip)
                table.add_row("Camera Count", str(len(ip_list)))
            except:
                pass
        
        # Docker settings
        docker_config = config.get('docker', {})
        table.add_row("Web Port Start", str(docker_config.get('web_port_start', 'N/A')))
        table.add_row("RTMP Port Start", str(docker_config.get('rtmp_port_start', 'N/A')))
        table.add_row("Restart Policy", docker_config.get('restart_policy', 'N/A'))
        
        # Timezone
        custom_env = config.get('custom_environment', {})
        table.add_row("Timezone", custom_env.get('TZ', 'N/A'))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error reading configuration: {e}[/red]")

if __name__ == '__main__':
    cli()
