"""Vercel serverless function - minimal working version"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = self.path
        
        # Health check
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "service": "star-office-ui",
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # State endpoint
        elif path == '/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": os.environ.get("STAR_OFFICE_STATUS", "idle"),
                "message": os.environ.get("STAR_OFFICE_MESSAGE", "AI助手办公室已上线！"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Agents endpoint
        elif path == '/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"agents": [], "count": 0}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Memo endpoint
        elif path in ['/memo', '/yesterday-memo']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "date": "2026-03-09",
                "content": [
                    "• AI助手办公室部署到Vercel成功",
                    "• 支持多Agent协作展示",
                    "• 可以通过API推送状态更新"
                ],
                "has_content": True
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default 404
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "path": path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/set_state':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                response = {
                    "status": data.get("status", "idle"),
                    "message": data.get("message", ""),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self.send_response(404)
            self.end_headers()