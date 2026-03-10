"""Vercel serverless function entry point for Star Office UI"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import tempfile

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'vercel-deployment-secret-key-2026')

# Set up paths
temp_dir = tempfile.gettempdir()
STATE_FILE = os.path.join(temp_dir, "state.json")
AGENTS_STATE_FILE = os.path.join(temp_dir, "agents-state.json")
JOIN_KEYS_FILE = os.path.join(temp_dir, "join-keys.json")

# Initialize files
def init_files():
    """Initialize state files with defaults"""
    if not os.path.exists(STATE_FILE):
        default_state = {
            "status": os.environ.get("STAR_OFFICE_STATUS", "idle"),
            "message": os.environ.get("STAR_OFFICE_MESSAGE", "AI助手办公室已上线！"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_state, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(AGENTS_STATE_FILE):
        with open(AGENTS_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
            
    if not os.path.exists(JOIN_KEYS_FILE):
        default_keys = {
            "ocj_vercel_demo": {
                "maxConcurrent": 3,
                "description": "Demo key for Vercel deployment"
            }
        }
        with open(JOIN_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_keys, f, ensure_ascii=False, indent=2)

# Initialize on import
init_files()

# Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "star-office-ui",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/state')
def get_state():
    """Get current state"""
    init_files()
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({
            "status": "idle",
            "message": "Vercel deployment",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

@app.route('/set_state', methods=['POST'])
def set_state():
    """Set state"""
    init_files()
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    state = {
        "status": data.get("status", "idle"),
        "message": data.get("message", ""),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    return jsonify(state)

@app.route('/agents')
def get_agents():
    """Get agents list"""
    init_files()
    try:
        with open(AGENTS_STATE_FILE, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        return jsonify({
            "agents": list(agents.values()),
            "count": len(agents)
        })
    except:
        return jsonify({"agents": [], "count": 0})

@app.route('/memo')
@app.route('/yesterday-memo')
def get_memo():
    """Get yesterday memo (dummy for Vercel)"""
    return jsonify({
        "date": "2026-03-09",
        "content": [
            "• AI助手办公室部署到Vercel成功",
            "• 支持多Agent协作展示",
            "• 可以通过API推送状态更新"
        ],
        "has_content": True
    })

# Catch all for frontend routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Serve frontend files or return 404"""
    # Don't serve API routes here
    if path.startswith(('state', 'health', 'agents', 'memo', 'set_state')):
        return jsonify({"error": "Not found"}), 404
    
    # For now, just return a simple message
    # In production, this would serve the static files
    return jsonify({
        "message": "Star Office UI on Vercel", 
        "path": path,
        "hint": "Frontend should be served by Vercel static handler"
    })

# Export handler for Vercel
handler = app