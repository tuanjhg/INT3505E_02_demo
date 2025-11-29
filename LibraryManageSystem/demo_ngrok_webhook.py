#!/usr/bin/env python3
"""
Ngrok Demo Script for Library Management System Webhook
This script starts ngrok tunnel and configures the webhook URL
"""

import os
import sys
import time
import subprocess
import requests
import json
from threading import Thread

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"ngrok is installed: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print_error("ngrok is not installed or not in PATH")
    print_info("Please install ngrok:")
    print_info("  1. Download from: https://ngrok.com/download")
    print_info("  2. Extract and add to PATH")
    print_info("  3. Sign up at: https://dashboard.ngrok.com/signup")
    print_info("  4. Get auth token and run: ngrok authtoken <YOUR_TOKEN>")
    return False

def start_webhook_receiver():
    """Start webhook receiver server"""
    print_header("STARTING WEBHOOK RECEIVER")
    print_info("Starting Flask webhook receiver on port 5001...")
    
    # Start receiver in background
    receiver_cmd = [sys.executable, 'webhook_receiver.py']
    receiver_process = subprocess.Popen(
        receiver_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code == 200:
            print_success("Webhook receiver is running on http://localhost:5001")
            return receiver_process
        else:
            print_error("Webhook receiver failed to start")
            return None
    except requests.exceptions.RequestException:
        print_error("Could not connect to webhook receiver")
        return None

def start_ngrok_tunnel(port=5001):
    """Start ngrok tunnel"""
    print_header("STARTING NGROK TUNNEL")
    print_info(f"Starting ngrok tunnel for port {port}...")
    
    # Start ngrok
    ngrok_cmd = ['ngrok', 'http', str(port), '--log=stdout']
    ngrok_process = subprocess.Popen(
        ngrok_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for ngrok to start
    time.sleep(3)
    
    # Get ngrok public URL
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                public_url = tunnels[0]['public_url']
                print_success(f"ngrok tunnel is running!")
                print_info(f"Public URL: {Colors.BOLD}{public_url}{Colors.RESET}")
                return ngrok_process, public_url
    except requests.exceptions.RequestException:
        pass
    
    print_error("Failed to get ngrok public URL")
    print_info("Check ngrok dashboard: http://localhost:4040")
    return ngrok_process, None

def test_webhook(webhook_url):
    """Test webhook endpoint"""
    print_header("TESTING WEBHOOK")
    print_info(f"Sending test webhook to: {webhook_url}")
    
    test_data = {
        "event": "book_borrowed",
        "user": {
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "book": {
            "id": 1,
            "title": "The Great Gatsby",
            "isbn": "978-0-7432-7356-5"
        },
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Test webhook sent successfully!")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Webhook failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to send test webhook: {e}")
        return False

def display_instructions(public_url):
    """Display usage instructions"""
    webhook_url = f"{public_url}/webhook"
    
    print_header("SETUP INSTRUCTIONS")
    
    print(f"{Colors.BOLD}1. Configure Library Management System:{Colors.RESET}")
    print(f"   Add to your .env file:")
    print(f"   {Colors.CYAN}ADMIN_WEBHOOK_URL={webhook_url}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}2. Or set environment variable:{Colors.RESET}")
    print(f"   Windows PowerShell:")
    print(f"   {Colors.CYAN}$env:ADMIN_WEBHOOK_URL='{webhook_url}'{Colors.RESET}")
    print(f"   Linux/Mac:")
    print(f"   {Colors.CYAN}export ADMIN_WEBHOOK_URL='{webhook_url}'{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}3. View webhooks in browser:{Colors.RESET}")
    print(f"   {Colors.CYAN}{public_url}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}4. ngrok Dashboard:{Colors.RESET}")
    print(f"   {Colors.CYAN}http://localhost:4040{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}5. Test with curl:{Colors.RESET}")
    print(f"""   {Colors.CYAN}curl -X POST {webhook_url} \\
     -H "Content-Type: application/json" \\
     -d '{{"event":"test","message":"Hello from curl"}}'{Colors.RESET}""")

def main():
    """Main function"""
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║       Library Management System - Ngrok Webhook Demo            ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)
    
    # Check ngrok
    if not check_ngrok_installed():
        return 1
    
    # Start webhook receiver
    receiver_process = start_webhook_receiver()
    if not receiver_process:
        return 1
    
    try:
        # Start ngrok tunnel
        ngrok_process, public_url = start_ngrok_tunnel()
        
        if not public_url:
            print_warning("Could not get public URL automatically")
            print_info("Please check http://localhost:4040 for the ngrok URL")
            input("\nPress Enter after you have the URL...")
        else:
            # Set environment variable
            os.environ['WEBHOOK_URL'] = public_url
            
            # Display instructions
            display_instructions(public_url)
            
            # Send test webhook
            print()
            send_test = input(f"{Colors.YELLOW}Send test webhook? (y/n): {Colors.RESET}").lower()
            if send_test == 'y':
                test_webhook(f"{public_url}/webhook")
        
        # Keep running
        print_header("WEBHOOK RECEIVER RUNNING")
        print_info("Press Ctrl+C to stop...")
        print_info(f"View webhooks: {public_url if public_url else 'http://localhost:5001'}")
        print_info("ngrok dashboard: http://localhost:4040")
        print()
        
        # Wait forever
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
    
    finally:
        # Cleanup
        print_info("Stopping services...")
        try:
            receiver_process.terminate()
            receiver_process.wait(timeout=5)
            print_success("Webhook receiver stopped")
        except:
            pass
        
        try:
            ngrok_process.terminate()
            ngrok_process.wait(timeout=5)
            print_success("ngrok tunnel stopped")
        except:
            pass
        
        print(f"\n{Colors.GREEN}✨ Goodbye!{Colors.RESET}\n")

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
