#!/usr/bin/env python3
"""
Simple Manual Webhook Tester
Send test webhooks to receiver for demonstration
"""

import requests
import json
import time
from datetime import datetime

# Configuration
WEBHOOK_URL = "http://localhost:5001/webhook"  # Change to your ngrok URL when ready

# Test data examples
TEST_WEBHOOKS = [
    {
        "event": "book_borrowed",
        "user": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "id": 101
        },
        "book": {
            "id": 1,
            "title": "The Great Gatsby",
            "isbn": "978-0-7432-7356-5",
            "author": "F. Scott Fitzgerald"
        },
        "timestamp": datetime.now().isoformat()
    },
    {
        "event": "book_returned",
        "user": {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "id": 102
        },
        "book": {
            "id": 2,
            "title": "1984",
            "isbn": "978-0-452-28423-4",
            "author": "George Orwell"
        },
        "timestamp": datetime.now().isoformat()
    },
    {
        "event": "book_overdue",
        "user": {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "id": 103
        },
        "book": {
            "id": 3,
            "title": "To Kill a Mockingbird",
            "isbn": "978-0-06-112008-4",
            "author": "Harper Lee"
        },
        "days_overdue": 5,
        "fine_amount": 5.00,
        "timestamp": datetime.now().isoformat()
    },
    {
        "event": "user_registered",
        "user": {
            "name": "Diana Prince",
            "email": "diana@example.com",
            "id": 104
        },
        "timestamp": datetime.now().isoformat()
    },
    {
        "event": "payment_received",
        "user": {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "id": 103
        },
        "payment": {
            "amount": 5.00,
            "method": "credit_card",
            "transaction_id": "TXN-20251124-001"
        },
        "timestamp": datetime.now().isoformat()
    }
]

def send_webhook(webhook_url, payload):
    """Send a webhook and return response"""
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response': response.json() if response.ok else response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e)
        }

def print_colored(text, color='white'):
    """Print colored text"""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'white': '\033[0m'
    }
    print(f"{colors.get(color, colors['white'])}{text}\033[0m")

def main():
    """Main function"""
    print_colored("\n╔══════════════════════════════════════════════════════════════════╗", 'cyan')
    print_colored("║          Webhook Manual Tester                                  ║", 'cyan')
    print_colored("╚══════════════════════════════════════════════════════════════════╝\n", 'cyan')
    
    # Get webhook URL
    print(f"Current webhook URL: {WEBHOOK_URL}")
    custom_url = input("\nEnter webhook URL (or press Enter to use default): ").strip()
    
    if custom_url:
        webhook_url = custom_url
    else:
        webhook_url = WEBHOOK_URL
    
    print_colored(f"\nUsing webhook URL: {webhook_url}", 'blue')
    
    # Check if receiver is available
    try:
        response = requests.get(webhook_url.replace('/webhook', '/health'), timeout=5)
        if response.status_code == 200:
            print_colored("✅ Webhook receiver is online!", 'green')
        else:
            print_colored("⚠️  Warning: Webhook receiver returned non-200 status", 'yellow')
    except requests.exceptions.RequestException:
        print_colored("⚠️  Warning: Could not connect to webhook receiver", 'yellow')
        print_colored("   Make sure webhook_receiver.py is running!", 'yellow')
        proceed = input("\nContinue anyway? (y/n): ").lower()
        if proceed != 'y':
            return
    
    print_colored("\n📋 Available test webhooks:", 'cyan')
    for i, webhook in enumerate(TEST_WEBHOOKS, 1):
        print(f"  {i}. {webhook['event']}")
    print(f"  {len(TEST_WEBHOOKS) + 1}. Send all")
    print("  0. Exit")
    
    while True:
        print_colored("\n" + "="*70, 'white')
        choice = input("Select option (0-6): ").strip()
        
        if choice == '0':
            print_colored("\n👋 Goodbye!", 'cyan')
            break
        
        try:
            choice_num = int(choice)
            
            if choice_num == len(TEST_WEBHOOKS) + 1:
                # Send all webhooks
                print_colored("\n🚀 Sending all test webhooks...", 'blue')
                for i, webhook in enumerate(TEST_WEBHOOKS, 1):
                    print(f"\nSending {i}/{len(TEST_WEBHOOKS)}: {webhook['event']}")
                    result = send_webhook(webhook_url, webhook)
                    
                    if result.get('success'):
                        print_colored(f"✅ Success! Status: {result['status_code']}", 'green')
                    else:
                        print_colored(f"❌ Failed: {result.get('error', 'Unknown error')}", 'red')
                    
                    if i < len(TEST_WEBHOOKS):
                        time.sleep(1)  # Brief pause between webhooks
                
                print_colored("\n✅ All webhooks sent!", 'green')
                
            elif 1 <= choice_num <= len(TEST_WEBHOOKS):
                # Send specific webhook
                webhook = TEST_WEBHOOKS[choice_num - 1]
                webhook['timestamp'] = datetime.now().isoformat()  # Update timestamp
                
                print_colored(f"\n🚀 Sending webhook: {webhook['event']}", 'blue')
                print("\nPayload:")
                print(json.dumps(webhook, indent=2))
                
                result = send_webhook(webhook_url, webhook)
                
                if result.get('success'):
                    print_colored(f"\n✅ Success! Status: {result['status_code']}", 'green')
                    print("Response:", json.dumps(result['response'], indent=2))
                else:
                    print_colored(f"\n❌ Failed!", 'red')
                    if 'error' in result:
                        print(f"Error: {result['error']}")
                    else:
                        print(f"Status: {result.get('status_code')}")
                        print(f"Response: {result.get('response')}")
            else:
                print_colored("❌ Invalid choice!", 'red')
                
        except ValueError:
            print_colored("❌ Invalid input! Please enter a number.", 'red')
        except KeyboardInterrupt:
            print_colored("\n\n👋 Goodbye!", 'cyan')
            break

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", 'red')
        import traceback
        traceback.print_exc()
