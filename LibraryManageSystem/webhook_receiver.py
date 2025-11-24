"""
Webhook Receiver Server for Library Management System
Simple server to receive and display webhook notifications
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
webhook_history = []

@app.route('/')
def index():
    """Display webhook history as HTML"""
    # Build info section with dynamic values
    base_url = request.url_root.rstrip('/')
    count = len(webhook_history)
    
    html_start = """<!DOCTYPE html>
<html><head><title>Webhook Receiver</title><meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<style>
body {{ font-family: Arial; max-width: 1200px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
h1 {{ color: #333; }}
.webhook {{ background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.event {{ background: #4CAF50; color: white; padding: 5px 10px; border-radius: 3px; display: inline-block; }}
.time {{ color: #666; font-size: 0.9em; }}
pre {{ background: #f8f8f8; padding: 10px; overflow-x: auto; border-radius: 3px; }}
.info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
.empty {{ text-align: center; color: #999; padding: 60px; }}
</style></head><body>
<h1>🔔 Webhook Receiver</h1>
<div class="info">
<strong>Webhook Endpoint:</strong> <code>{0}/webhook</code><br>
<strong>Total Received:</strong> {1}<br>
<strong>Auto-refresh:</strong> Every 5 seconds
</div>""".format(base_url, count)
    
    html_content = ""
    if webhook_history:
        for wh in reversed(webhook_history):
            event = wh.get("event", "unknown")
            time = wh.get("received_at", "")
            payload = json.dumps(wh, indent=2, ensure_ascii=False)
            html_content += f'<div class="webhook"><span class="event">{event}</span> <span class="time">{time}</span><pre>{payload}</pre></div>'
    else:
        html_content = '<div class="empty">No webhooks received yet. Waiting...</div>'
    
    html_end = "</body></html>"
    return html_start + html_content + html_end

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """Receive webhook notification"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data'}), 400
        
        webhook_data = {**data, 'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        webhook_history.append(webhook_data)
        
        if len(webhook_history) > 50:
            webhook_history.pop(0)
        
        print("\n" + "="*70)
        print(f"🔔 WEBHOOK RECEIVED at {webhook_data['received_at']}")
        print("="*70)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*70 + "\n")
        
        return jsonify({'status': 'success', 'received_at': webhook_data['received_at']}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'total_webhooks': len(webhook_history)}), 200

@app.route('/clear', methods=['POST'])
def clear():
    """Clear all webhooks"""
    webhook_history.clear()
    return '<script>window.location="/"</script>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          Webhook Receiver Server                                ║
╚══════════════════════════════════════════════════════════════════╝

🚀 Server: http://localhost:{port}
📡 Webhook: http://localhost:{port}/webhook
💚 Health: http://localhost:{port}/health

Waiting for webhooks...
    """)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
