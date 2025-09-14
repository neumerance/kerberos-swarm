#!/usr/bin/env python3
"""
Example usage script for Kerberos.io Multi-Agent CLI
This demonstrates how to use the CLI programmatically
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a CLI command and show results"""
    print(f"\n🔹 {description}")
    print(f"Command: kerberos {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(['python', 'kerberos_cli.py'] + cmd.split(), 
                              capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
            
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: kerberos_cli.py not found")
        return False

def main():
    """Demonstrate CLI usage"""
    print("🔒 Kerberos.io Multi-Agent CLI Demo")
    print("=" * 50)
    
    # Check system
    if not run_command("check", "Checking system dependencies"):
        print("❌ System check failed. Please install missing dependencies.")
        return
    
    # Show configuration info
    run_command("info", "Showing configuration information")
    
    # Generate compose file
    if run_command("generate", "Generating docker-compose.yml"):
        print("✅ Docker Compose file generated successfully")
    else:
        print("❌ Failed to generate compose file")
        return
    
    # You can uncomment these to actually deploy (be careful!)
    # print("\n⚠️  Uncomment the lines below to actually deploy agents")
    # 
    # # Start agents
    # if run_command("start", "Starting all agents"):
    #     print("✅ All agents started")
    #     time.sleep(5)  # Wait a bit
    #     
    #     # Show status
    #     run_command("status", "Checking agent status")
    #     
    #     # Stop agents
    #     run_command("stop", "Stopping all agents")
    #     print("✅ All agents stopped")
    
    print("\n🎉 Demo completed!")
    print("📚 Run 'python kerberos_cli.py --help' for full command reference")

if __name__ == "__main__":
    main()
