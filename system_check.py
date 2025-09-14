#!/usr/bin/env python3
"""
System Resources Check for Kerberos Multi-Agent Deployment
Analyzes system capacity to run configured Kerberos agents
"""

import psutil
import yaml
import sys
from pathlib import Path
import ipaddress

def load_config(config_path="config.yml"):
    """Load and parse the Kerberos configuration"""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_path}' not found!")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error parsing configuration: {e}")
        return None

def calculate_camera_count(config):
    """Calculate total number of cameras from IP range"""
    try:
        start_ip = config['cameras']['ip_range']['start']
        end_ip = config['cameras']['ip_range']['end']
        
        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)
        
        return int(end) - int(start) + 1
    except Exception as e:
        print(f"❌ Error calculating camera count: {e}")
        return 0

def get_resource_requirements(config, camera_count):
    """Calculate resource requirements based on configuration"""
    
    # Base resource requirements per agent
    base_memory_mb = 256  # Base memory per agent
    base_cpu_percent = 5  # Base CPU percentage per agent
    
    # Additional resources based on configuration
    additional_memory = 0
    additional_cpu = 0
    
    # Recording increases resource usage
    if config.get('cameras', {}).get('recording', {}).get('enabled', False):
        additional_memory += 128  # Additional MB for recording
        additional_cpu += 3  # Additional CPU percentage
    
    # Live streaming increases resource usage
    if config.get('cameras', {}).get('stream', {}).get('enabled', False):
        additional_memory += 64  # Additional MB for streaming
        additional_cpu += 2  # Additional CPU percentage
    
    # Motion detection increases resource usage
    motion_config = config.get('cameras', {}).get('motion_detection', {})
    if motion_config.get('enabled', False):
        additional_memory += 32  # Additional MB for motion detection
        additional_cpu += 2  # Additional CPU percentage
    
    # Calculate totals
    memory_per_agent = base_memory_mb + additional_memory
    cpu_per_agent = base_cpu_percent + additional_cpu
    
    total_memory_mb = memory_per_agent * camera_count
    total_cpu_percent = cpu_per_agent * camera_count
    
    return {
        'camera_count': camera_count,
        'memory_per_agent_mb': memory_per_agent,
        'cpu_per_agent_percent': cpu_per_agent,
        'total_memory_mb': total_memory_mb,
        'total_memory_gb': round(total_memory_mb / 1024, 2),
        'total_cpu_percent': total_cpu_percent,
        'estimated_disk_usage_gb_per_day': calculate_disk_usage(config, camera_count)
    }

def calculate_disk_usage(config, camera_count):
    """Estimate daily disk usage based on recording settings"""
    if not config.get('cameras', {}).get('recording', {}).get('enabled', False):
        return 0
    
    # Rough estimates for video data
    # Assumes 720p video at medium quality
    mb_per_minute = 10  # Rough estimate
    
    # Get recording duration
    duration = config.get('cameras', {}).get('recording', {}).get('duration', 30)
    pre_recording = config.get('cameras', {}).get('recording', {}).get('pre_recording', 5)
    post_recording = config.get('cameras', {}).get('recording', {}).get('post_recording', 5)
    
    total_recording_seconds = duration + pre_recording + post_recording
    
    # Assume motion triggers recording every 10 minutes on average
    recordings_per_day = 24 * 60 / 10  # 144 recordings per day
    
    mb_per_camera_per_day = (total_recording_seconds / 60) * mb_per_minute * recordings_per_day
    total_mb_per_day = mb_per_camera_per_day * camera_count
    
    return round(total_mb_per_day / 1024, 2)  # Convert to GB

def check_system_resources():
    """Check current system resources"""
    # Memory
    memory = psutil.virtual_memory()
    total_memory_gb = round(memory.total / (1024**3), 2)
    available_memory_gb = round(memory.available / (1024**3), 2)
    memory_usage_percent = memory.percent
    
    # CPU
    cpu_count = psutil.cpu_count()
    cpu_usage_percent = psutil.cpu_percent(interval=1)
    
    # Disk
    disk = psutil.disk_usage('/')
    total_disk_gb = round(disk.total / (1024**3), 2)
    free_disk_gb = round(disk.free / (1024**3), 2)
    disk_usage_percent = round((disk.used / disk.total) * 100, 1)
    
    return {
        'memory': {
            'total_gb': total_memory_gb,
            'available_gb': available_memory_gb,
            'usage_percent': memory_usage_percent
        },
        'cpu': {
            'cores': cpu_count,
            'current_usage_percent': cpu_usage_percent
        },
        'disk': {
            'total_gb': total_disk_gb,
            'free_gb': free_disk_gb,
            'usage_percent': disk_usage_percent
        }
    }

def check_network_ports(config, camera_count):
    """Check if required network ports are available"""
    import socket
    
    web_port_start = config.get('docker', {}).get('web_port_start', 8080)
    rtmp_port_start = config.get('docker', {}).get('rtmp_port_start', 1935)
    
    busy_ports = []
    
    # Check web ports
    for i in range(camera_count):
        port = web_port_start + i
        if is_port_in_use(port):
            busy_ports.append(f"Web port {port}")
    
    # Check RTMP ports
    for i in range(camera_count):
        port = rtmp_port_start + i
        if is_port_in_use(port):
            busy_ports.append(f"RTMP port {port}")
    
    return busy_ports

def is_port_in_use(port):
    """Check if a port is currently in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def print_system_check_report(config_path="config.yml"):
    """Generate and print comprehensive system check report"""
    
    print("🔍 Kerberos Multi-Agent System Check")
    print("=" * 50)
    
    # Load configuration
    config = load_config(config_path)
    if not config:
        return False
    
    # Calculate requirements
    camera_count = calculate_camera_count(config)
    if camera_count == 0:
        print("❌ Unable to determine camera count from configuration")
        return False
    
    requirements = get_resource_requirements(config, camera_count)
    system_resources = check_system_resources()
    
    # Print configuration summary
    print(f"\n📋 Configuration Summary:")
    print(f"   Cameras: {camera_count}")
    print(f"   IP Range: {config['cameras']['ip_range']['start']} - {config['cameras']['ip_range']['end']}")
    print(f"   Recording: {'✅ Enabled' if config.get('cameras', {}).get('recording', {}).get('enabled', False) else '❌ Disabled'}")
    print(f"   Streaming: {'✅ Enabled' if config.get('cameras', {}).get('stream', {}).get('enabled', False) else '❌ Disabled'}")
    print(f"   Motion Detection: {'✅ Enabled' if config.get('cameras', {}).get('motion_detection', {}).get('enabled', False) else '❌ Disabled'}")
    
    # Print resource requirements
    print(f"\n💾 Resource Requirements:")
    print(f"   Memory per agent: {requirements['memory_per_agent_mb']} MB")
    print(f"   CPU per agent: {requirements['cpu_per_agent_percent']}%")
    print(f"   Total memory needed: {requirements['total_memory_gb']} GB")
    print(f"   Total CPU needed: {requirements['total_cpu_percent']}%")
    print(f"   Estimated daily storage: {requirements['estimated_disk_usage_gb_per_day']} GB/day")
    
    # Print current system resources
    print(f"\n💻 Current System Resources:")
    print(f"   Memory: {system_resources['memory']['available_gb']} GB available / {system_resources['memory']['total_gb']} GB total ({system_resources['memory']['usage_percent']:.1f}% used)")
    print(f"   CPU: {system_resources['cpu']['cores']} cores, {system_resources['cpu']['current_usage_percent']:.1f}% current usage")
    print(f"   Disk: {system_resources['disk']['free_gb']} GB free / {system_resources['disk']['total_gb']} GB total ({system_resources['disk']['usage_percent']:.1f}% used)")
    
    # Check capacity
    print(f"\n✅ Capacity Assessment:")
    
    # Memory check
    memory_sufficient = system_resources['memory']['available_gb'] >= requirements['total_memory_gb']
    memory_status = "✅ SUFFICIENT" if memory_sufficient else "❌ INSUFFICIENT"
    print(f"   Memory: {memory_status}")
    if not memory_sufficient:
        needed = requirements['total_memory_gb'] - system_resources['memory']['available_gb']
        print(f"      Need {needed:.1f} GB more memory")
    
    # CPU check
    cpu_sufficient = requirements['total_cpu_percent'] <= 80  # Leave 20% headroom
    cpu_status = "✅ SUFFICIENT" if cpu_sufficient else "⚠️  HIGH USAGE"
    print(f"   CPU: {cpu_status}")
    if not cpu_sufficient:
        print(f"      Warning: Estimated {requirements['total_cpu_percent']}% CPU usage may cause performance issues")
    
    # Disk check (1 week storage)
    weekly_storage_gb = requirements['estimated_disk_usage_gb_per_day'] * 7
    disk_sufficient = system_resources['disk']['free_gb'] >= weekly_storage_gb
    disk_status = "✅ SUFFICIENT" if disk_sufficient else "⚠️  LIMITED"
    print(f"   Disk (1 week storage): {disk_status}")
    if not disk_sufficient and requirements['estimated_disk_usage_gb_per_day'] > 0:
        print(f"      Warning: Only {system_resources['disk']['free_gb']:.1f} GB free, need {weekly_storage_gb:.1f} GB for 1 week")
    
    # Port availability check
    print(f"\n🔌 Port Availability:")
    busy_ports = check_network_ports(config, camera_count)
    if not busy_ports:
        print("   ✅ All required ports are available")
    else:
        print("   ⚠️  Some ports are in use:")
        for port in busy_ports:
            print(f"      - {port}")
    
    # Overall recommendation
    print(f"\n🎯 Overall Assessment:")
    
    if memory_sufficient and cpu_sufficient and disk_sufficient and not busy_ports:
        print("   ✅ READY FOR DEPLOYMENT")
        print("   Your system can handle all configured Kerberos agents!")
        return True
    else:
        print("   ⚠️  DEPLOYMENT WITH CAUTION")
        if not memory_sufficient:
            print("   - Consider reducing the number of cameras or adding more RAM")
        if not cpu_sufficient:
            print("   - Monitor CPU usage during deployment")
        if not disk_sufficient:
            print("   - Plan for regular cleanup of recordings or add more storage")
        if busy_ports:
            print("   - Stop services using conflicting ports or modify port configuration")
        return False

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
    success = print_system_check_report(config_file)
    sys.exit(0 if success else 1)
